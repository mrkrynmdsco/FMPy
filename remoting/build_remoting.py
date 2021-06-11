import os
import tarfile
import shutil
from subprocess import check_call
from fmpy.util import download_file


url = 'https://github.com/rpclib/rpclib/archive/refs/tags/v2.3.0.tar.gz'
checksum = 'eb9e6fa65e1a79b37097397f60599b93cb443d304fbc0447c50851bc3452fdef'

# build configuration
config = 'Release'

download_file(url, checksum)

filename = os.path.basename(url)

basedir = os.path.dirname(__file__)

source_dir = 'rpclib-2.3.0'

rpclib_dir = os.path.join(basedir, source_dir).replace('\\', '/')

shutil.rmtree(source_dir, ignore_errors=True)

print("Extracting %s" % filename)
with tarfile.open(filename, 'r:gz') as tar:
    tar.extractall()

# patch the CMake project to link static against the MSVC runtime
with open(os.path.join(source_dir, 'CMakeLists.txt'), 'a') as file:
    # Append 'hello' at the end of file
    file.write('''
        
# set_property(TARGET rpc PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
message(${CMAKE_CXX_FLAGS_RELEASE})
message(${CMAKE_CXX_FLAGS_DEBUG})

set(CompilerFlags
        CMAKE_CXX_FLAGS
        CMAKE_CXX_FLAGS_DEBUG
        CMAKE_CXX_FLAGS_RELEASE
        CMAKE_C_FLAGS
        CMAKE_C_FLAGS_DEBUG
        CMAKE_C_FLAGS_RELEASE
        )
foreach(CompilerFlag ${CompilerFlags})
  string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
endforeach()

message(${CMAKE_CXX_FLAGS_RELEASE})
message(${CMAKE_CXX_FLAGS_DEBUG})
''')


path = os.path.dirname(__file__)

print("Building RPCLIB...")
for bitness, generator in [('win32', 'Visual Studio 15 2017'), ('win64', 'Visual Studio 15 2017 Win64')]:

    cmake_args = [
        'cmake',
        '-B', source_dir + '/' + bitness,
        '-D', 'RPCLIB_MSVC_STATIC_RUNTIME=ON',
        '-D', 'CMAKE_INSTALL_PREFIX=' + source_dir + '/' + bitness + '/rpc',
        '-G', generator,
        source_dir
    ]

    # build rpclib
    check_call(args=cmake_args)
    check_call(args=['cmake', '--build', source_dir + '/' + bitness, '--target', 'install', '--config', config])

    # build remoting binaries
    check_call(['cmake', '-B', bitness, '-G', 'Visual Studio 15 2017', '-D', 'RPCLIB=' + rpclib_dir + '/' + bitness + '/rpc', '-B', bitness, '.'])
    check_call(['cmake', '--build', bitness, '--config', config])
