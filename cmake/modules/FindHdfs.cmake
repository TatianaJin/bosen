# - Try to find Hdfs
##
# The following are set after configuration is done:
#  HDFS_LIBRARIES
#  HDFS_INCLUDE_DIRS


message(STATUS $ENV{LIBHDFS3_HOME}/include)
find_path(HDFS_INCLUDE_DIR NAMES hdfs.h  HINTS $ENV{LIBHDFS3_HOME}/include/hdfs)
find_library(HDFS_LIBRARY NAMES hdfs3 HINTS $ENV{LIBHDFS3_HOME}/lib)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(HDFS DEFAULT_MSG
        HDFS_INCLUDE_DIR HDFS_LIBRARY)

if(HDFS_FOUND)
    set(HDFS_INCLUDE_DIRS ${HDFS_INCLUDE_DIR})
    set(HDFS_LIBRARIES ${HDFS_LIBRARY})
endif()
