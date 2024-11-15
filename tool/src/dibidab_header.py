from __future__ import annotations  # allows the use of the current class as type hint
from dataclasses import dataclass   # for @dataclass

import cxxheaderparser.simple as simple_parser
import cxxheaderparser.types

import dibidab_jinja
import sys
import os
import pathlib

if len(sys.argv) != 3:
    print("Dibidab-header-tool: Expected 2 arguments: <input-file> <out-directory>")
    exit(1)

input_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])

if not output_path.exists():
    os.makedirs(output_path)

class CxxVisitor(simple_parser.SimpleCxxVisitor):
    def __init__(self):
        super().__init__()

    def on_class_field(self, state: cxxheaderparser.simple.SClassBlockState, f: cxxheaderparser.types.Field) -> None:
        f.line_number = state.location.lineno
        super().on_class_field(state, f)

visitor = CxxVisitor()
parser = simple_parser.CxxParser(os.fsdecode(input_path), None, visitor)
parser.parse()
parsed_input = visitor.data

@dataclass
class NamespaceWrapper:
    current: simple_parser.NamespaceScope
    parent: NamespaceWrapper | None

    def get_id_chain_list(self):
        list = []
        it = self
        while it != None:
            if it.current.name.format() != "":
                list.insert(0, it.current.name.format())
            it = it.parent
        return list

def format_id(typename: cxxheaderparser.types.PQName, namespace: NamespaceWrapper | None):
    id = ""
    if namespace != None:
        namespaces = namespace.get_id_chain_list()
        id += "::".join(namespaces)
        if len(namespaces) > 0:
            id += "::"
    id += "::".join(seg.format() for seg in typename.segments)
    return id

def get_struct_render_info(struct: simple_parser.ClassScope, namespace: NamespaceWrapper):
    name = "__".join(seg.format() for seg in struct.class_decl.typename.segments)
    id = format_id(struct.class_decl.typename, namespace)
    variables = []
    json_variables = []
    is_component = False
    is_empty = True
    json_method = "array"

    json_exposing = False
    lua_exposing = False
    prev_expose_line = 0

    for field in struct.fields:
        if isinstance(field.type, cxxheaderparser.types.Type):
            typename_str = field.type.typename.format()
            # Check if field is a recognized macro from <dibidab_header.h>:
            if typename_str == "dibidab_expose":
                if field.line_number != prev_expose_line:
                    prev_expose_line = field.line_number
                    json_exposing = lua_exposing = False
                if field.name != None:
                    exposing_to = field.name.format().lower()
                    if exposing_to == "json":
                        json_exposing = True
                    elif exposing_to == "lua":
                        lua_exposing = True
                else:
                    json_exposing = lua_exposing = False
                continue
            elif typename_str == "dibidab_component":
                is_component = True
                continue
            elif typename_str == "dibidab_json_method":
                if field.name == None:
                    raise SystemExit("Pass a json method for: " + id)
                json_method = field.name.format().lower()
                continue

        if field.name == None:
            continue

        is_empty = False

        if not json_exposing and not lua_exposing:
            continue

        # Pointers, Pointers to Pointers, Arrays are ignored.
        if not isinstance(field.type, cxxheaderparser.types.Type):
            continue

        if field.access != "public" and (json_exposing or lua_exposing):
            raise SystemExit("Trying to expose a variable without public visibility: " + id + "::" + field.name.format())

        var = {
            "name": field.name.format(),
            "type": field.type.typename.format(),
            "json_exposed": json_exposing,
            "lua_exposed": lua_exposing
        }
        variables.append(var)
        if json_exposing:
            json_variables.append(var)

    any_exposed_to_lua = any([var["lua_exposed"] for var in variables])
    info = {
        # name is used in function/variable names.
        "name": name,
        # id is used as actual typename, including `namespace::`
        "id": id,
        # id, without `namespace::`
        "id_namespaceless": format_id(struct.class_decl.typename, None),
        # namespaces leading to this type
        "namespaces": namespace.get_id_chain_list(),
        "is_component": is_component,
        "is_empty": is_empty,
        "json_method": json_method,
        "any_exposed_to_lua": any_exposed_to_lua,
        "any_exposed_to_json": any([var["json_exposed"] for var in variables]),
        "generate_lua_user_type": any_exposed_to_lua or is_component,
        # exposed variables:
        "variables": variables,
        # copy of variables, but only with variables that are exposed to json.
        # This allows us to loop over the json vars and use `loop.index0` in jinja without skipping indices.
        "json_variables": json_variables
    }
    return info

def get_enum_render_info(enum: simple_parser.EnumDecl, namespace: NamespaceWrapper):
    name = "__".join(seg.format() for seg in enum.typename.segments)
    id = format_id(enum.typename, namespace)
    info = {
        "name": name,
        "id": id,
        "id_namespaceless": format_id(enum.typename, None),
        "vals": [ value.name for value in enum.values ]
    }
    return info

struct_render_info = []
enum_render_info = []

def loop_over_namespace(namespace: NamespaceWrapper):
    for child_name, child_space in namespace.current.namespaces.items():
        loop_over_namespace(NamespaceWrapper(child_space, namespace))

    for struct in namespace.current.classes:
        struct_render_info.append(get_struct_render_info(struct, namespace))

    for enum in namespace.current.enums:
        enum_render_info.append(get_enum_render_info(enum, namespace))

loop_over_namespace(NamespaceWrapper(parsed_input.namespace, None))

input_name = input_path.name.split(".")[0]

any_struct_exposed_to_json = any([struct["any_exposed_to_json"] for struct in struct_render_info])
any_struct_exposed_to_lua = any([struct["generate_lua_user_type"] for struct in struct_render_info])
any_struct_is_component = any([struct["is_component"] for struct in struct_render_info])

### Render ###
def render(file_type_name):
    jinja_template = dibidab_jinja.jinja_env.get_template(file_type_name + ".jinja")

    render_result = jinja_template.render(
        structs = struct_render_info,
        enums = enum_render_info,
        input_name = input_name,
        original_header_rel_path = os.path.relpath(input_path, output_path),
        category_path = os.path.relpath(input_path.parent, os.path.commonpath([input_path, output_path])).replace("\\", "/").split("/"),
        any_struct_exposed_to_json = any_struct_exposed_to_json,
        any_struct_exposed_to_lua = any_struct_exposed_to_lua,
        any_struct_is_component = any_struct_is_component
    )
    struct_file_path = output_path.joinpath(input_name + "." + file_type_name)
    if struct_file_path.exists() and struct_file_path.read_text() == render_result:
        # No need to save the same content again. Could trigger unnecessary recompilation.
        return
    struct_file = open(struct_file_path.absolute(), "w")
    struct_file.write(render_result)
    struct_file.close()

render("info.cpp")
if any_struct_exposed_to_json:
    render("json.inl")
    render("json.cpp.inl")
######
