# emlite-conan

emlite-conan can be used as a local conan recipe index which allows you to use emlite packages via conan.

To use emscripten with conan, you will need to add an emscripten profile:
```ini
[settings]
os=Emscripten
arch=wasm
build_type=Release
compiler=emcc
compiler.version=4.0.10
compiler.cppstd=17
compiler.libcxx=libc++

[buildenv]
CC=emcc
CXX=em++
AR=emar
NM=emnm
RANLIB=emranlib
STRIP=emstrip
```
Note that this assumes you have emscripten already installed as it doesn't require the emsdk tool supplied by conan.

You can then clone this repo, and add it as a remote:
```bash
git clone https://github.com/emlite/emlite-conan
conan remote add emlite-conan ./emlite-conan --allowed-packages="*"
```

Then you can use conan as you would normally do, and pass a `-pr:emscripten` profile argument along with `--build=missing`.

For example:
```bash
conan install --requires=wasmbind/0.1.1 -o wasmbind/*:webbind=True -r=emlite-conan --build=missing -pr=emscripten
```
Will install wasmbind along with the webbind feature to your local conan cache.

To use it in a conan project, you can add the dependency to wasmbind in your conanfile.txt:
```ini
[requires]
wasmbind/0.1.1

[options]
wasmbind/*:webbind=True

[generators]
CMakeDeps
CMakeToolchain
```

Then run the build command:
```bash
conan install . -of bin -r=emlite-conan --build=missing -pr=emscripten
```

We use CMake as our generator, so in your CMakeLists.txt you can use `find_package` to find wasmbind:
```cmake
cmake_minimum_required(VERSION 3.28)
project(demo)

find_package(wasmbind CONFIG REQUIRED)

add_executable(myapp main.cpp)

target_link_libraries(myapp PRIVATE wasmbind::webbind)

set_target_properties(myapp PROPERTIES LINKER_LANGUAGE CXX SUFFIX .js LINK_FLAGS "-sSINGLE_FILE -sALLOW_MEMORY_GROWTH=1 -sEXPORTED_FUNCTIONS=_main -Wl,--strip-all,--export-dynamic")
```

To build, you will need to use the Emscripten toolchain file or just emcmake:
```bash
cmake --preset conan-release
cmake --build --preset conan-release
```