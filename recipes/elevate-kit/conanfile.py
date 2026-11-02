from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os


class ElevateKitConan(ConanFile):
    name = "elevate-kit"
    version = "1.0.6"
    description = "Seamless, zero-prompt, kernel-verified cross-platform privilege escalation framework"
    topics = ("elevation", "privilege", "ipc", "cpp")
    license = "MIT"
    homepage = "https://github.com/xyz1001/elevate-kit"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    package_type = "library"

    def requirements(self):
        self.requires("cli11/2.6.0")
        self.requires("fmt/10.2.1", transitive_libs=not self.options.shared)
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("scope-lite/0.2.0")
        self.requires("sole/1.0.4")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TEST"] = False
        tc.variables["BUILD_EXAMPLE"] = False
        tc.variables["VERSION_NAME"] = self.version
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["elevate_kit"]
        self.cpp_info.requires = [
            "cli11::cli11",
            "fmt::_fmt",
            "nlohmann_json::nlohmann_json",
            "scope-lite::scopelite",
            "sole::sole",
        ]
        if self.options.shared:
            self.cpp_info.defines = ["ELEVATE_KIT_DLL"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["taskschd", "ole32", "oleaut32", "shell32", "advapi32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
        self.cpp_info.set_property("cmake_file_name", "elevate-kit")
        self.cpp_info.set_property("cmake_target_name", "elevate-kit::elevate-kit")
