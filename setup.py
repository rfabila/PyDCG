from distutils.core import setup, Extension

arch = "-D32_BITS"

if sys.maxsize > (2**31-1):
    arch = "-D64_BITS"

holesCpp = Extension('gbasics_test.holesCpp',
                    sources = ["PyDCG/Cpp_sources/holesCPP_wrapper.cpp", "PyDCG/Cpp_sources/gbCPP.cpp"])
holesCpp.extra_compile_args = ['--std=c++0x'];

geometricbasicsC = Extension('PyDCG.geometricbasicsC',
                    sources = ["PyDCG/C_sources/geometricbasicsC_wrapper.c", "PyDCG/C_sources/geometricbasicsC_wrapper.c"])
geometricbasicsC.extra_compile_args = [arch]

setup (name = 'PyDCG',
       author = 'author',
       author_email = 'author@email.com',
       url = 'http://www.url.com',
       version = '0.0.1',
       description = 'Python package with implementations of discrete and combinatorial geometry algorithms.',
       packages = ['PyDCG'],
       package_data = {'PyDCG' : ['Icons/*.*']},
       ext_modules = [holesCpp, geometricbasicsC]
      )
