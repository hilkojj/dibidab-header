import cxxheaderparser.simple as simple_parser
import dibidab_jinja
import sys
import os
import pathlib

if len(sys.argv) != 3:
    print("Dibidab-header-tool: Expected 2 arguments: <input-file> <out-directory>")
    exit(1)

print("Dibidab-header-tool!")

input_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])

if not output_path.exists():
    os.makedirs(output_path)

parsed_input = simple_parser.parse_file(input_path)

def format_struct_id(struct: simple_parser.ClassScope, namespace: simple_parser.NamespaceScope):
    id = ""
    namespace_id = namespace.name.format()
    if len(namespace_id) > 0:
        id += namespace_id + "::"
    id += "::".join(seg.format() for seg in struct.class_decl.typename.segments)
    return id

struct_render_info = []

def loop_over_namespace(namespace: simple_parser.NamespaceScope):
    for child_name, child_space in namespace.namespaces.items():
        loop_over_namespace(child_space)

    for struct in namespace.classes:
        print(format_struct_id(struct, namespace))
        struct_render_info.append({
            "name": "__".join(seg.format() for seg in struct.class_decl.typename.segments),
            "id": format_struct_id(struct, namespace)
        })


loop_over_namespace(parsed_input.namespace)

input_name = input_path.name.split(".")[0]

jinja_struct_info_template = dibidab_jinja.jinja_env.get_template("struct_info.jinja")

struct_info = jinja_struct_info_template.render(structs = struct_render_info, input_name = input_name)
struct_info_file = open(output_path.joinpath(input_name + ".struct_info.inl").absolute(), "w")
struct_info_file.write(struct_info)
struct_info_file.close()
