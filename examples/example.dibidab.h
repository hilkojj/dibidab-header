
#include <dibidab_header.h>

#include <string>
#include <vector>

struct NonExistentStruct;

struct Person
{
  dibidab_expose(lua, json);
    std::string name;
    int age = 0;
    std::vector<int> numbers = { 3, 4, 5 };

  dibidab_hide;
    NonExistentStruct *pointer = nullptr;
    struct AnotherNonExistentStruct *anotherPointer = nullptr;
    int hiddenInt = -1;
};
