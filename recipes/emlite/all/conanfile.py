from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, collect_libs
from conan.tools.scm import Git
import os

required_conan_version = ">=2.0"

class EmliteConan(ConanFile):
    name = "emlite"
    version = "0.1.2"
    license = "MIT"
    url = "https://github.com/emlite/emlite-cpp"
    homepage = "https://github.com/emlite/emlite-cpp"
    description = "emlite is a tiny JS bridge for native C/C++ code via Wasm."
    topics = ("wasm", "emscripten", "javascript", "bridge", "c", "c++")
    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "capi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "capi": False,
    }

    def config_options(self):
        # fPIC has no effect on Windows
        if self.settings.get_safe("os") == "Windows":
            del self.options.fPIC

    def validate(self):
        if str(self.settings.get_safe("os")) != "Emscripten":
            raise ConanInvalidConfiguration("emlite is intended for os=Emscripten")

    def layout(self):
        # If CMakeLists.txt lives at repo root (most common), keep "."
        # If it's under "src/", change to: cmake_layout(self, src_folder="src")
        cmake_layout(self, src_folder=".")

    def requirements(self):
        # This is your adapter layer for Emscripten specifics
        if str(self.settings.get_safe("os")) == "Emscripten":
            self.requires("emsenv/0.1.2")

    def source(self):
        git = Git(self)
        git.clone(
            "https://github.com/emlite/emlite-cpp.git",
            target=".",
            args=["--depth=1", f"--branch=v{self.version}"]
        )

    def generate(self):
        # Conan 2: produce CMakePresets.json + deps files
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={
            "EMLITE_CLIB_ONLY": "ON" if self.options.capi else "OFF",
            "EMLITE_BUILD_EXAMPLES": "OFF",
        })
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # CMake integration hints for consumers
        self.cpp_info.set_property("cmake_file_name", "emlite")
        self.cpp_info.set_property("cmake_target_name", "emlite::emlite")
        self.cpp_info.libs = collect_libs(self)
