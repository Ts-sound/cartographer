
set(LIB_NAME plugin_metrics_prometheus)

file(GLOB_RECURSE LIB_HDRS "${CMAKE_CURRENT_SOURCE_DIR}/*.h")
file(GLOB_RECURSE LIB_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/*.cc")
file(GLOB_RECURSE LIB_TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/*_test.cc")
list(REMOVE_ITEM LIB_SRCS ${LIB_TEST_SRCS})

if(${BUILD_PROMETHEUS})

    find_package(ZLIB REQUIRED)
    find_package(prometheus-cpp REQUIRED)

    add_library(${LIB_NAME} SHARED ${LIB_HDRS} ${LIB_SRCS})
    target_include_directories(${LIB_NAME} PUBLIC
        ${prometheus-cpp_INCLUDE_DIR}
        $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:include>
    )
    target_link_libraries(${LIB_NAME} PUBLIC ${ZLIB_LIBRARIES})
    target_link_libraries(${LIB_NAME} PUBLIC absl::algorithm
        absl::base
        absl::flat_hash_map
        absl::memory
    )
    target_link_libraries(${LIB_NAME} PRIVATE prometheus-cpp::core prometheus-cpp::pull)
    target_compile_options(${LIB_NAME} PRIVATE -fvisibility=hidden -fvisibility-inlines-hidden)
endif()
