import dibidab_jinja
import sys
import os
import pathlib

if len(sys.argv) != 3:
    print("Dibidab-registry-tool: Expected 1 argument: <registry-namespace> <out-directory>")
    exit(1)

print("Dibidab-registry-tool!")

registry_namespace = sys.argv[1]
output_path = pathlib.Path(sys.argv[2])

struct_info_file_names = [
    file.split(".")[0]
    for file in os.listdir(output_path)
    if os.path.isfile(output_path.joinpath(file))
    and file.endswith(".struct_info.inl")
]

struct_info_registry_template = dibidab_jinja.jinja_env.get_template("struct_info_registry.jinja")

struct_registry = struct_info_registry_template.render(
    registry_namespace = registry_namespace,
    struct_info_file_names = struct_info_file_names
)

struct_registry_file = open(output_path.joinpath("registry.struct_info.h").absolute(), "w")
struct_registry_file.write(struct_registry)
struct_registry_file.close()
