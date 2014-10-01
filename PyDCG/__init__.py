'''
PyDCG, a collection of Discrete and Computational Geometry tools
'''
import crossing
import geometricbasics
import points
import combinatorics
import datastructures
import line
import visualizer
import visualizer2
import holes
import heuristics
import convexhull
import pointExplorer

import pickle, os
__config_file=open(os.path.join(os.path.dirname(__file__), "config/geometricbasics.config"), "r")
__config=pickle.load(__config_file)
__config_file.close()
#print "CONFIG", __config

if not __config['PURE_PYTHON']:
    import holesCpp
    import geometricbasicsCpp
    import crossingCpp
