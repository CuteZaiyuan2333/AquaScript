"""
Cython编译配置
用于将.pyx文件编译为C扩展
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# 编译选项
compiler_directives = {
    'language_level': 3,
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'embedsignature': True,
    'optimize.use_switch': True,
    'optimize.unpack_method_calls': True,
}

# 扩展模块定义
extensions = [
    Extension(
        "cython_aquavm",
        ["cython_aquavm.pyx"],
        extra_compile_args=[
            "/O2",  # Windows MSVC优化
            "/favor:INTEL64",  # 针对64位Intel处理器优化
        ] if hasattr(__builtins__, '__IPYTHON__') else [
            "-O3",  # GCC/Clang优化
            "-march=native",  # 针对本机CPU优化
            "-ffast-math",  # 快速数学运算
        ],
        define_macros=[
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ],
    )
]

setup(
    name="AquaVM Cython Extension",
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
        annotate=True,  # 生成HTML注释文件
    ),
    zip_safe=False,
)