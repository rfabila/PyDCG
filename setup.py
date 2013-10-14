from distutils.core import setup, Extension
import sys
import pickle
import urllib2
import os

download = None

while 'install' in sys.argv and download not in ['Y', 'N']:
    download = raw_input('Download point sets? (~600 Mb) Y/N ')

if download == 'Y':
    names = ['03.b08', '04.b08', '05.b08', '06.b08', '07.b08', '08.b08', '09.b16', '10.b16']
    route = os.path.join(os.path.dirname(__file__), "PyDCG/point_sets/otypes")
    
    for file_name in names:
        if not os.path.exists('PyDCG/point_sets/otypes' + file_name):
            print "Downloading otypes" + file_name + "..."
            f = urllib2.urlopen('http://www.ist.tugraz.at/aichholzer/research/rp/triangulations/ordertypes/data/otypes' + file_name)
            data = f.read()
            with open(route + file_name, "wb") as dest:
                dest.write(data)
    print "Done."

arch = "-DINT32"
geometricbasics_config = {}
sources_dir = "PyDCG/Cpp_sources/"

if sys.maxsize > (2**31-1):
    arch = "-DINT64"
    geometricbasics_config["MAX_INT"]=2**62
else:
    geometricbasics_config["MAX_INT"]=2**30
    
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
       package_data = {'PyDCG' : ['Icons/*.*', 'config/*.*', 'point_sets/*.*']},
       ext_modules = [crossingCpp, holesCpp, geometricbasicsCpp]
      )
