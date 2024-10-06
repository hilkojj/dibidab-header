import sys
import pathlib

if len(sys.argv) != 2:
    print("Dibidab-registry-tool: Expected 1 argument: <out-directory>")
    exit(1)

output_path = pathlib.Path(sys.argv[1])

