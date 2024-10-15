import dibidab_jinja
import sys
import os
import pathlib

if len(sys.argv) != 3:
    print("Dibidab-registry-tool: Expected 1 argument: <registry-namespace> <out-directory>")
    exit(1)

registry_namespace = sys.argv[1]
output_path = pathlib.Path(sys.argv[2])

struct_info_file_names = [
    file.split(".")[0]
    for file in os.listdir(output_path)
    if os.path.isfile(output_path.joinpath(file))
    and file.endswith(".struct_info.inl")
]

def render(file_type_name):
    registry_template = dibidab_jinja.jinja_env.get_template(file_type_name + ".jinja")

    render_result = registry_template.render(
        registry_namespace = registry_namespace,
        struct_info_file_names = struct_info_file_names
    )
    registry_file = open(output_path.joinpath(file_type_name).absolute(), "w")
    registry_file.write(render_result)
    registry_file.close()

render("registry.struct_info.h")
render("registry.struct_json.h")
render("registry.struct_json.cpp")
