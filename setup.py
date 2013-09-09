from distutils.core import setup, Extension
import sys

arch = "-DINT32"

if sys.maxsize > (2**31-1):
    arch = "-DINT64"

holesCpp = Extension('PyDCG.holesCpp',
                    sources = ["PyDCG/Cpp_sources/holesCPP_wrapper.cpp", "PyDCG/Cpp_sources/holesCPP.cpp"])
holesCpp.extra_compile_args = ['--std=c++0x'];

geometricbasicsCpp = Extension('PyDCG.geometricbasicsCpp',
                    sources = ["PyDCG/Cpp_sources/geometricbasicsCpp_wrapper.cpp", "PyDCG/Cpp_sources/geometricbasicsCpp.cpp"])
geometricbasicsCpp.extra_compile_args = [arch]

setup (name = 'PyDCG',
       author = 'author',
       author_email = 'author@email.com',
       url = 'http://www.url.com',
       version = '0.0.1',
       description = 'Python package with implementations of discrete and combinatorial geometry algorithms.',
       packages = ['PyDCG'],
       package_data = {'PyDCG' : ['Icons/*.*']},
       ext_modules = [holesCpp, geometricbasicsCpp]
      )
