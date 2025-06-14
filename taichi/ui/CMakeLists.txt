
# ./taichi/ui/CMakeLists.txt

add_library(taichi_ui
        gui/gui.cpp
        gui/android.cpp
        gui/cocoa.cpp
        gui/win32.cpp
        gui/x11.cpp
)

if (APPLE)
  set(CLANG_OSX_FLAGS -DTARGET_OS_OSX -x objective-c++)
  target_compile_options(taichi_ui PRIVATE ${CLANG_OSX_FLAGS})
endif()


if(TI_WITH_GGUI AND NOT ANDROID)
  target_sources(taichi_ui PRIVATE common/window_base.cpp)
endif()

target_include_directories(taichi_ui
        PRIVATE
        ${PROJECT_SOURCE_DIR}
        ${PROJECT_SOURCE_DIR}/external/glfw/include
        ${PROJECT_SOURCE_DIR}/external/eigen
        ${PROJECT_SOURCE_DIR}/external/volk
        ${PROJECT_SOURCE_DIR}/external/Vulkan-Headers/include
        ${LLVM_INCLUDE_DIRS}
        PUBLIC
        ${PROJECT_SOURCE_DIR}/external/glm
)

target_link_libraries(taichi_ui PRIVATE taichi_common)


########################################################
###                     GGUI                        ####
########################################################
if(TI_WITH_GGUI)
  # Dear ImGui
  add_definitions(-DIMGUI_IMPL_VULKAN_NO_PROTOTYPES)
  set(IMGUI_DIR ${PROJECT_SOURCE_DIR}/external/imgui)
  file(GLOB TAICHI_IMGUI_SOURCE
          ${IMGUI_DIR}/backends/imgui_impl_vulkan.cpp
          ${IMGUI_DIR}/imgui.cpp
          ${IMGUI_DIR}/imgui_draw.cpp
          ${IMGUI_DIR}/imgui_tables.cpp
          ${IMGUI_DIR}/imgui_widgets.cpp
  )
  if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    list(APPEND TAICHI_IMGUI_SOURCE ${IMGUI_DIR}/backends/imgui_impl_metal.mm)
    add_compile_options(-fobjc-arc)
  endif()
  if(ANDROID)
    list(APPEND TAICHI_IMGUI_SOURCE ${IMGUI_DIR}/backends/imgui_impl_android.cpp)
    add_library(imgui ${TAICHI_IMGUI_SOURCE})
  else()
    list(APPEND TAICHI_IMGUI_SOURCE ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp)
    add_library(imgui ${TAICHI_IMGUI_SOURCE})
    target_include_directories(imgui PRIVATE ${PROJECT_SOURCE_DIR}/external/glfw/include)
  endif()

  target_include_directories(imgui PUBLIC ${IMGUI_DIR} ${IMGUI_DIR}/backends ..)
  target_include_directories(imgui PUBLIC ${PROJECT_SOURCE_DIR}/external/Vulkan-Headers/include)

  target_link_libraries(taichi_ui PRIVATE imgui)
  if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    target_link_libraries(taichi_ui PRIVATE "-framework QuartzCore")
  endif()

  add_subdirectory(ggui)
  target_link_libraries(taichi_ui PUBLIC taichi_ui_ggui)
endif()
