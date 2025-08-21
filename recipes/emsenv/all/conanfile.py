from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, collect_libs
from conan.tools.scm import Git
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"

class EmsEnvConan(ConanFile):
    name = "emsenv"
    version = "0.1.2"
    license = "MIT"
    url = "https://github.com/emlite/emsenv"
    homepage = "https://github.com/emlite/emsenv"
    description = "emsenv is an emscripten adapter for the emlite project."
    topics = ("emscripten", "wasm", "adapter")
    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder=".")

    def configure(self):
        if self.settings.get_safe("os") == "Windows":
            del self.options.fPIC

    def validate(self):
        if str(self.settings.get_safe("os")) != "Emscripten":
            raise ConanInvalidConfiguration("emsenv is intended for os=Emscripten")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/emlite/emsenv.git",
                  target=".", args=["--depth=1", f"--branch=v{self.version}"])

    def generate(self):
        tc = CMakeToolchain(self); tc.generate()
        deps = CMakeDeps(self); deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "emsenv")
        self.cpp_info.set_property("cmake_target_name", "emsenv::emsenv")
        self.cpp_info.includedirs = []              # <- no headers in this package
        self.cpp_info.libs = collect_libs(self)     # pick up built libs from lib/
        # (defaults for libdirs=['lib'], bindirs=['bin'] are fine)
