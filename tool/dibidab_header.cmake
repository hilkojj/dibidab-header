
find_package(Python COMPONENTS Interpreter)

set(HEADER_COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/src/dibidab_header.py)
set(REGISTRY_COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/src/dibidab_registry.py)

execute_process(COMMAND ${Python3_EXECUTABLE} -m pip install --user -r ${CMAKE_CURRENT_LIST_DIR}/requirements.txt)

function(process_dibidab_headers source_dir out_dir registry_namespace)
    file(MAKE_DIRECTORY ${out_dir})

    # Headers:
    file(GLOB header_files ${source_dir}/**/*.dibidab.h)
    foreach(header_file ${header_files})
        get_filename_component(file_name ${header_file} NAME_WE)
        set(struct_info_file ${out_dir}/${file_name}.struct_info.inl)
        set(struct_json_file ${out_dir}/${file_name}.struct_json.inl)
        set(struct_json_cpp_file ${out_dir}/${file_name}.struct_json.cpp.inl)

        # Run Header Tool during build every time header is changed:
        add_custom_command(
            OUTPUT ${struct_info_file} ${struct_json_file} ${struct_json_cpp_file}
            COMMAND ${HEADER_COMMAND} ${header_file} ${out_dir}
            WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
            DEPENDS ${header_file}
            VERBATIM
        )
        # Run Header Tool once already while configuring CMake:
        execute_process(
            COMMAND ${HEADER_COMMAND} ${header_file} ${out_dir}
            WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
        )
    endforeach()

    # Run Registry Tool while configuring CMake:
    execute_process(
        COMMAND ${REGISTRY_COMMAND} ${registry_namespace} ${out_dir}
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
        COMMAND_ERROR_IS_FATAL ANY
    )

endfunction()

