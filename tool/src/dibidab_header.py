from __future__ import annotations  # allows the use of the current class as type hint
from dataclasses import dataclass   # for @dataclass

import cxxheaderparser.simple as simple_parser
import cxxheaderparser.types
from powerline.segments.vim.plugin.tagbar import currenttag

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

parsed_input = simple_parser.parse_file(input_path)

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

def format_struct_id(struct: simple_parser.ClassScope, namespace: NamespaceWrapper | None):
    id = ""
    if namespace != None:
        namespaces = namespace.get_id_chain_list()
        id += "::".join(namespaces)
        if len(namespaces) > 0:
            id += "::"
    id += "::".join(seg.format() for seg in struct.class_decl.typename.segments)
    return id

def get_struct_render_info(struct: simple_parser.ClassScope, namespace: NamespaceWrapper):
    name = "__".join(seg.format() for seg in struct.class_decl.typename.segments)
    id = format_struct_id(struct, namespace)
    variables = []
    is_component = False
    is_empty = True
    json_method = "array"

    json_exposing = False
    lua_exposing = False

    for field in struct.fields:
        if isinstance(field.type, cxxheaderparser.types.Type):
            typename_str = field.type.typename.format()
            # Check if field is a recognized macro from <dibidab_header.h>:
            if typename_str == "dibidab_expose":
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

        variables.append({
            "name": field.name.format(),
            "type": field.type.typename.format(),
            "json_exposed": json_exposing,
            "lua_exposed": lua_exposing
        })

    any_exposed_to_lua = any([var["lua_exposed"] for var in variables])
    info = {
        # name is used in function/variable names.
        "name": name,
        # id is used as actual typename, including `namespace::`
        "id": id,
        # id, without `namespace::`
        "id_namespaceless": format_struct_id(struct, None),
        # namespaces leading to this type
        "namespaces": namespace.get_id_chain_list(),
        "is_component": is_component,
        "is_empty": is_empty,
        "json_method": json_method,
        "any_exposed_to_lua": any_exposed_to_lua,
        "any_exposed_to_json": any([var["json_exposed"] for var in variables]),
        "generate_lua_user_type": any_exposed_to_lua or is_component,
        # exposed variables:
        "variables": variables
    }
    return info

struct_render_info = []

def loop_over_namespace(namespace: NamespaceWrapper):
    for child_name, child_space in namespace.current.namespaces.items():
        loop_over_namespace(NamespaceWrapper(child_space, namespace))

    for struct in namespace.current.classes:
        struct_render_info.append(get_struct_render_info(struct, namespace))


loop_over_namespace(NamespaceWrapper(parsed_input.namespace, None))

input_name = input_path.name.split(".")[0]

### Render ###
def render(file_type_name):
    jinja_template = dibidab_jinja.jinja_env.get_template(file_type_name + ".jinja")

    render_result = jinja_template.render(
        structs = struct_render_info,
        input_name = input_name,
        original_header_rel_path = os.path.relpath(input_path, output_path)
    )
    struct_file_path = output_path.joinpath(input_name + "." + file_type_name)
    if struct_file_path.exists() and struct_file_path.read_text() == render_result:
        # No need to save the same content again. Could trigger unnecessary recompilation.
        return
    struct_file = open(struct_file_path.absolute(), "w")
    struct_file.write(render_result)
    struct_file.close()

render("struct_info.inl")
render("struct_json.inl")
render("struct_json.cpp.inl")
######
