#    PyDCG
#
#    A Python library for Discrete and Combinatorial Geometry.
#
#    Copyright (C) 2018 Ruy Fabila Monroy
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


import fractions
import math

"""This module is used to create objects to be drawn in the visualizer
    There are base classes and functions that return lists
    of bases clases."""
class LineSegment():
    """A line segment given the two endpoints. It is a wrapper to
        create_line. Thus it receives the same keyword arguments"""
    def __init__(self,p,q,**keywords):
        self.p=p
        self.q=q
        self.keywords=keywords
        
        if "fill" not in self.keywords:
            self.keywords["fill"]="gray"
            
        if "width" not in self.keywords:
            self.keywords["width"]=2
        
        self.f="create_line"
    
    def compute_arguments(self,convert_to_screen_coords):
        p=convert_to_screen_coords(self.p)
        q=convert_to_screen_coords(self.q)
        args=[p[0],p[1],q[0],q[1]]
        return args
        
        
        
class Point():
    """ A class for drawing points. It is a wrapper to the create_oval
    methods and thus it accepts the same keyword arguments. Only use it if you
    are going to do fancy stuff. It receives the point and the thicknes
    of the point as arguments."""
    
    def __init__(self,p,t,**keywords):
        self.p=p
        self.t=t
        self.keywords=keywords
        if "fill" not in self.keywords:
            self.keywords["fill"]="black"
        self.f="create_oval"
        
    def compute_arguments(self,convert_to_screen_coords):
        q=convert_to_screen_coords(self.p)
        args=[q[0]-self.t,q[1]-self.t,q[0]+self.t,q[1]+self.t]
        return args
        

class Polygon():
    """A polygon with the given set of vertices. It is a wrapper
    to tye create_polygon method, so it accepts the same keyword arguments."""
    def __init__(self,vertices,**keywords):
        self.vertices=vertices
        self.keywords=keywords
        
        if "fill" not in self.keywords:
            self.keywords["fill"]=""
            
        if "outline" not in self.keywords:
            self.keywords["outline"]="gray"
        
        if "width" not in self.keywords:
            self.keywords["width"]=2
            
        self.f="create_polygon"
        
    def compute_arguments(self,convert_to_screen_coords):
        args=[]
        for p in self.vertices:
            q=convert_to_screen_coords(p)
            args.append(q[0])
            args.append(q[1])
        return args
    
    
class RegularPolygon(Polygon):
    """A regular polygon with the given the number of sides,
     center and circumradius."""
     
    def __init__(self,n,center,R,**keywords):
        vertices=[[fractions.Fraction(R*math.cos(2*math.pi*i/n)+center[0]),
            fractions.Fraction(R*math.sin(2*math.pi*i/n))+center[1]] for i in range(n)]
        Polygon.__init__(self,vertices,**keywords)
     
class Circle():
    """A circle with given center and radius"""
    def __init__(self,center,radius,**keywords):
        self.center=center
        self.r=radius
        self.keywords=keywords
        self.f="create_oval"
    
    def compute_arguments(self,convert_to_screen_coords):
        corner_1=[self.r+self.center[0], self.r+self.center[1]]
        corner_2=[-self.r+self.center[0], -self.r+self.center[1]]
        c_1=convert_to_screen_coords(corner_1)
        c_2=convert_to_screen_coords(corner_2)
        args=c_1
        args.extend(c_2)
        return args

#The following are compound functions, they return a list of the base drawing
#    classes.
def create_regular_polygon(n,center,R,show_vertices=True,t=2,polygon_keywords={},point_keywords={}):
    P=RegularPolygon(n,center,R,**polygon_keywords)
    if show_vertices:
        pts=[Point(p,t,**polygon_keywords) for p in P.vertices]
        pts.insert(0,P)
        return pts
    return [P]
        
        
        
        
        