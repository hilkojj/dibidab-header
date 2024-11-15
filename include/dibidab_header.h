#pragma once

/**
 * Choose the default method for converting between C++ and Json.
 * Options are: array, object
 * Default: array
 */
#define dibidab_json_method(method)

/**
 * Choose where to expose the following struct members to.
 * Options are: lua, json
 */
#define dibidab_expose(...)

/**
 * Generate code for using this struct as a component.
 */
#define dibidab_component

/**
 * Generates reflection and lua binding code for an enum.
 */
#define dibidab_enum(name)
