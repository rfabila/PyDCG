#    PyDCG
#
#    A Python library for Discrete and Combinatorial Geometry.
#
#    Copyright (C) 2015 Ruy Fabila Monroy
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation version 2.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from distutils.core import setup, Extension
import sys
import pickle
#import urllib2
import urllib.request, urllib.error, urllib.parse
import os

options = {}

with open("options.cfg") as options_file:
    for opt in options_file:
        if opt[0] != '#':
            k, v = opt.split()
            options[k] = int(v)

#download = None

if options['DOWNLOAD_POINT_SETS'] == 1 and 'install' in sys.argv:
    names = ['03.b08', '04.b08', '05.b08', '06.b08', '07.b08', '08.b08', '09.b16', '10.b16']
    route = os.path.join(os.path.dirname(__file__), "PyDCG/point_sets/otypes")

    for file_name in names:
        if not os.path.exists('PyDCG/point_sets/otypes' + file_name):
            print ("Downloading otypes" + file_name + "...")
            #f = urllib2.urlopen('http://www.ist.tugraz.at/aichholzer/research/rp/triangulations/ordertypes/data/otypes' + file_name)
            f = urllib.request.urlopen('http://www.ist.tugraz.at/aichholzer/research/rp/triangulations/ordertypes/data/otypes' + file_name)
            data = f.read()
            with open(route + file_name, "wb") as dest:
                dest.write(data)
    print ("Done.")

arch = "-DINT32"
config = {}
sources_dir = "PyDCG/Cpp_sources/"

if sys.maxsize > (2**31-1):
    arch = "-DINT64"
    config["MAX_INT"]=2**62
else:
    config["MAX_INT"]=2**30

geometricbasicsCpp = Extension('PyDCG.geometricbasicsCpp',
                    sources = [sources_dir+"geometricbasicsCpp_wrapper.cpp", sources_dir+"geometricbasicsCpp.cpp"])
geometricbasicsCpp.extra_compile_args = ['-I/usr/include/python3.10','-lpython3.10','--std=c++0x', '-O3', arch]

holesCpp = Extension('PyDCG.holesCpp',
                    sources = [sources_dir+"holesCPP_wrapper.cpp", sources_dir+"holesCPP.cpp", sources_dir+"geometricbasicsCpp.cpp"])
holesCpp.extra_compile_args = ['-I/usr/include/python3.10','-lpython3.10','--std=c++0x', '-O3', arch];

crossingCpp = Extension('PyDCG.crossingCpp',
                    sources = [sources_dir+"count_crossing_wrapper.cpp", sources_dir+"count_crossing.cpp", sources_dir+"geometricbasicsCpp.cpp"])
crossingCpp.extra_compile_args = ['-I/usr/include/python3.10','-lpython3.10','--std=c++0x', '-O3', arch];

modules = []

if options['PURE_PYTHON'] == 0:
    modules = [crossingCpp, holesCpp, geometricbasicsCpp]
    config['PURE_PYTHON'] = False
else:
    config['PURE_PYTHON'] = True

configFile=open("PyDCG/config/config.cfg","wb")
pickle.dump(config,configFile)
configFile.close()

setup (name = 'PyDCG',
       author = 'author',
       author_email = 'author@email.com',
       url = 'http://www.url.com',
       version = '0.0.1',
       description = 'Python package with implementations of discrete and combinatorial geometry algorithms.',
       packages = ['PyDCG'],
       package_data = {'PyDCG' : ['Icons/*.*', 'config/*.*', 'point_sets/*.*', 'doc/*.*', 'options.cfg']},
       ext_modules = modules
      )
