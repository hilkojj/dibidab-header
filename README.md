# Dibidab Header Tool

This tool will generate reflection code, Lua bindings and JSON-(de)serialization code for headers in game projects using the Dibidab-engine.

```c++
struct Person
{
    // This is a component, generate functions for adding/removing this to entities:
  dibidab_component;

    // Expose the following variables to Lua, and generate JSON (de)serialization code for them: 
  dibidab_expose(lua, json);
    std::string name;
    int age = 24;

    // Expose the following variable only to Lua, don't save/load them using JSON:
  dibidab_expose(lua);
    std::vector<int> numbers = { 3, 4, 5 };
};
```
Then the struct is available to use as a component in Lua:
```lua
component.Person.getFor(entity).age = 25
```
You can construct the type with a 'table-constructor':
```lua
setComponents(entity, {
    Person {
        name = "Hilko",
        age = 25,
        numbers = { 1, 2, 3 }
    },
    SomeOtherComponent {
        ...
    }
})
```

### Usage

Include the CMake file of this tool in your CMakeLists.txt and call the function.
This function will run the header tool for all `.dibidab.h` headers once during CMake configuration and will rerun for a header upon compilation if CMake has detected a file change.

(Assuming this repo is stored in `external/dibidab-header/`):
```CMake
include(${CMAKE_CURRENT_LIST_DIR}/external/dibidab-header/tool/dibidab_header.cmake)
process_dibidab_headers(
    # Source directory (to search for .dibidab.h headers):
    ${CMAKE_CURRENT_LIST_DIR}/source
    # Output directory:
    ${CMAKE_CURRENT_LIST_DIR}/source/dibidab_generated
    # namespace to put the generated registry in:
    MyProjectNamespace
)
```

### Examples

An example header is included in `examples/`.

To run the tool: `python tool/src/dibidab_header.py <input-header> <out-directory>`

To confirm the header is still valid C++: `g++ examples/example.dibidab.h -Iinclude/`

### Dependencies

Generated code is for use with the Dibidab-engine.
There will be `#include`s that reference headers from the engine and from Sol3, EnTT and Json for Modern C++, 

Tested with python 3.10.
Pip packages are listed in `tool/requirements.txt`
