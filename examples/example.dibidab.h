#pragma once

#include <dibidab_header.h>

#include <string>
#include <vector>

struct NonExistentStruct;

struct Person
{
  dibidab_component;

  dibidab_expose(lua, json);
    std::string name;
    int age = 0;
    std::vector<int> numbers = { 3, 4, 5 };

  dibidab_expose();
    NonExistentStruct *pointer = nullptr;
    struct AnotherNonExistentStruct *anotherPointer = nullptr;
    int hiddenInt = -1;
};

namespace AnotherSpace
{
    struct Yes
    {
      dibidab_json_method(object);

      dibidab_expose(lua, json);
        int b;
    };
}

Person testPerson {
    "Hilko",
    24,
    { 1, 2, 3 }
};

void test()
{
    testPerson.name = "Test";
}
