cmake_minimum_required(VERSION 3.16)

# =========================================================================
# CENTRAL APPLICATION VERSION DEFINITION
# =========================================================================
set(APP_VERSION_MAJOR 0)
set(APP_VERSION_MINOR 2)
set(APP_VERSION_PATCH 0)
set(APP_VERSION_STRING "${APP_VERSION_MAJOR}.${APP_VERSION_MINOR}.${APP_VERSION_PATCH}")

project(RapidMessageSender VERSION ${APP_VERSION_STRING} LANGUAGES CXX RC)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_AUTOUIC_SEARCH_PATHS ${CMAKE_CURRENT_SOURCE_DIR}/resources)

# Inject version definition into C++ compilation
add_compile_definitions(
    APP_VERSION_STRING="${APP_VERSION_STRING}"
    APP_VERSION_MAJOR=${APP_VERSION_MAJOR}
    APP_VERSION_MINOR=${APP_VERSION_MINOR}
    APP_VERSION_PATCH=${APP_VERSION_PATCH}
)

find_package(Qt6 REQUIRED COMPONENTS Widgets Network Core)

set(SOURCES
    src/main.cpp
    src/ui/mainwindow.h
    src/ui/mainwindow.cpp
    src/ui/custom_controls.h
    src/ui/custom_controls.cpp
    src/core/worker.h
    src/core/worker.cpp
    src/core/hotkey_listener.h
    src/core/hotkey_listener.cpp
    src/net/updater.h
    src/net/updater.cpp
)

set(UI_FILES
    resources/mainwindow.ui
)

set(RESOURCES
    resources/resources.qrc
    resources/version.rc
)

add_executable(RapidMessageSender WIN32
    ${SOURCES}
    ${UI_FILES}
    ${RESOURCES}
)

target_include_directories(RapidMessageSender PRIVATE 
    src
    src/ui
    src/core
    src/net
    ${CMAKE_CURRENT_BINARY_DIR}
)

target_link_libraries(RapidMessageSender PRIVATE
    Qt6::Widgets
    Qt6::Network
    Qt6::Core
    user32
    gdi32
    shell32
)

if(WIN32)
    set_target_properties(RapidMessageSender PROPERTIES
        WIN32_EXECUTABLE TRUE
    )
endif()
