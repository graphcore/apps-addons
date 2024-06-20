cmake_minimum_required(VERSION 3.10.0)

project(docs_benchmarking_tools)

set(BUILD_DOCS OFF CACHE BOOL "Build documentation")
if(NOT BUILD_DOCS)
  # Create an empty install target so `ninja install` still works.
  install(FILES)
  return()
endif()

find_package(graphcore_sphinx_resources REQUIRED)
find_package(LLVM REQUIRED CONFIG)

# Use the source tree to avoid needing other projects to be built.
set(VIEW_ROOT ${CMAKE_SOURCE_DIR}/..)

# Check that all the directories exist to catch code rot.
foreach(dir ${DOXYGEN_INCLUDE_DIRECTORIES})
  get_filename_component(real_dir_path "${dir}" REALPATH)
  if(NOT EXISTS ${real_dir_path})
    message(FATAL_ERROR "Documentation include directory does not exist: ${real_dir_path}")
  endif()
endforeach()

# Create a Doxyfile for doxygen to rad.
string(REPLACE ";" " " DOXYGEN_INPUT "${DOXYGEN_INCLUDE_DIRECTORIES}")
configure_file(api_reference/Doxyfile.in Doxyfile @ONLY)

# Grab the version number from the examples utils repo.
# This cmake code has been shamelessly copied from rDOCSPOPLAR.
file(READ ${CMAKE_SOURCE_DIR}/../benchmarking/version.json VERSION_JSON)
string(REGEX REPLACE
       ".*major[^:]*: \"([^\"]*)\".*" "\\1"
       BENCHMARKING_TOOLS_VERSION_MAJOR
       ${VERSION_JSON})
string(REGEX REPLACE
       ".*minor[^:]*: \"([^\"]*)\".*" "\\1"
       BENCHMARKING_TOOLS_VERSION_MINOR
       ${VERSION_JSON})
string(REGEX REPLACE
       ".*point[^:]*: \"([^\"]*)\".*" "\\1"
       BENCHMARKING_TOOLS_VERSION_POINT
       ${VERSION_JSON})
set(VERSION "${BENCHMARKING_TOOLS_VERSION_MAJOR}.${BENCHMARKING_TOOLS_VERSION_MINOR}.${BENCHMARKING_TOOLS_VERSION_POINT}")

sphinx_build_docs(
  NAME ${CMAKE_PROJECT_NAME}_user_guide
  VERSION ${VERSION}
  SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/user_guide
  COMPONENT benchmarking-tools-docs
)
set(user_guide_pdf      ${sphinx_build_docs_pdf_path})
set(user_guide_html_zip ${sphinx_build_docs_zip_path})

sphinx_build_docs(
  NAME ${CMAKE_PROJECT_NAME}_api_reference
  VERSION ${VERSION}
  SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/api_reference
  DOXYFILE ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
  COMPONENT benchmarking-tools-docs
)
set(api_reference_pdf      ${sphinx_build_docs_pdf_path})
set(api_reference_html_zip ${sphinx_build_docs_zip_path})

configure_file(docs_benchmarking-tools-config.cmake.in
               docs_benchmarking-tools-config.cmake
               @ONLY)
