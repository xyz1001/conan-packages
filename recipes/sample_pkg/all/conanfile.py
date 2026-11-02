from conan import ConanFile
from conan.tools.files import copy
import os


class SampleConan(ConanFile):
    name = "sample_pkg"
    version = "1.0.0"
    package_type = "header-library"
    description = "Example package template for custom conan packages repository"
    topics = ("template", "sample")

    # If pulling source from github/tarball, use get() in source():
    # def source(self):
    #     get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        # Example: copy headers into include directory
        include_dir = os.path.join(self.package_folder, "include")
        os.makedirs(include_dir, exist_ok=True)
        with open(os.path.join(include_dir, "sample_pkg.h"), "w") as f:
            f.write("#pragma once\n\ninline const char* sample_hello() { return \"Hello from sample_pkg!\"; }\n")

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
