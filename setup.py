from distutils.core import setup, Extension
import sys
import pickle

arch = "-DINT32"
geometricbasics_config = {}
sources_dir = "PyDCG/Cpp_sources/"

if sys.maxsize > (2**31-1):
    arch = "-DINT64"
    geometricbasics_config["MAX_INT"]=62
else:
    geometricbasics_config["MAX_INT"]=30
    
geometricbasics_config_file=open("PyDCG/config/geometricbasics.config","w")
pickle.dump(geometricbasics_config,geometricbasics_config_file)
geometricbasics_config_file.close()
    
geometricbasicsCpp = Extension('PyDCG.geometricbasicsCpp',
                    sources = [sources_dir+"geometricbasicsCpp_wrapper.cpp", sources_dir+"geometricbasicsCpp.cpp"])
geometricbasicsCpp.extra_compile_args = ['--std=c++0x', arch]

holesCpp = Extension('PyDCG.holesCpp',
                    sources = [sources_dir+"holesCPP_wrapper.cpp", sources_dir+"holesCPP.cpp", sources_dir+"geometricbasicsCpp.cpp"])
holesCpp.extra_compile_args = ['--std=c++0x', arch];

crossingCpp = Extension('PyDCG.crossingCpp',
                    sources = [sources_dir+"count_crossing_wrapper.cpp", sources_dir+"count_crossing.cpp", sources_dir+"geometricbasicsCpp.cpp"])
crossingCpp.extra_compile_args = ['--std=c++0x', arch];

setup (name = 'PyDCG',
       author = 'author',
       author_email = 'author@email.com',
       url = 'http://www.url.com',
       version = '0.0.1',
       description = 'Python package with implementations of discrete and combinatorial geometry algorithms.',
       packages = ['PyDCG'],
       package_data = {'PyDCG' : ['Icons/*.*', 'config/*.*']},
       ext_modules = [crossingCpp, holesCpp, geometricbasicsCpp]
      )
