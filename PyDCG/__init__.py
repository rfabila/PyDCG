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
import utilities

if not utilities.__config['PURE_PYTHON']:
    import holesCpp
    import geometricbasicsCpp
    import crossingCpp