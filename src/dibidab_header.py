import sys
import cxxheaderparser.simple

if len(sys.argv) != 2:
    print("Pass a file name")
    exit(1)

fileToParsePath = sys.argv[1]

file = open(fileToParsePath, 'r')
fileContent = file.read()
file.close()

print(fileContent)

parsedData = cxxheaderparser.simple.parse_string(fileContent)

print(parsedData)
