#!/usr/bin/env python

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

from fractions import *
import geometricbasics

def dual_point_to_line(point):
    l=Line(p=[0,point[1]],q=[1,point[0]+point[1]])
    return l

class Line:
    
    def __init__(self,p=[0,0],q=[1,1],color="grey",inf_precision=True):
        """constructs a line with passing
           through p and q"""
        delta_x=p[0]-q[0]
        delta_y=p[1]-q[1]
        if delta_x!= 0:
            if (delta_x.__class__==Fraction or
                delta_y.__class__==Fraction):
                if inf_precision:
                    self.m=delta_y/delta_x
                else:
                    self.m=float(delta_y)/float(delta_x)
            else:
                if inf_precision:
                    self.m=Fraction(delta_y,delta_x)
                    
                else:
                    self.m=float(delta_y)/float(delta_x)
            if inf_precision:
                self.b=p[1]-self.m*p[0]
            else:
                self.b=float(p[1]-self.m*p[0])
        else:
            self.m=None
            if inf_precision:
                self.b=p[0]
            else:
                self.b=float(p[0])
                    
            
        self.color=color
        
    
    def line_intersection(self,l):
        """Computes the intersection
           of this line with l. Returns
           None if the lines are parallel"""
        
        if self.m == l.m:
            return None
    
         #If one of them is vertical
        if self.m==None or l.m==None:
            if self.m==None:
                x=self.b
                y=l.m*x+l.b
                return [x,y]
            if l.m==None:
                x=l.b
                y=self.m*x+self.b
                return [x,y]
        
        #General case
        x=(l.b-self.b)/(self.m-l.m)
        y=self.m*x+self.b
        
        return [x,y]
    
        
    def point_in_line(self,point):
        """Test wheter a point is: above, below
            or in the line. returns -1,1 and 0
            respectively"""
        
        if self.m!=None:
            p=[0,self.b]
            q=[1,self.m+self.b]
        else:
            p=[self.b,0]
            q=[self.b,1]
        
        inline=geometricbasics.turn(p,q,point)
        return inline
    
    def point_in_self(self,point):
        if self.point_in_line(point)==0:
            return True
        return False
        
    def intersection(self,l):
        """Computes the point of intersection of object with l.
        If there are none or an infinity of them return False."""
        r=self.line_intersection(l)
        if r==None:
            return None
        if (self.point_in_self(r) and
            l.point_in_self(r)):
            return r
        return None
        
    
    def __str__(self):
        return "m="+self.m.__str__()+",b="+self.b.__str__()
    
    def vertical_distance(self,p):
        """Computes the vertical distance from point p to the line."""
        y=self.m*p[0]+self.b
        return abs(p[1]-y)
    
    def horizontal_distance(self,p):
        """Computes the horizontal distance from point p to the line."""
        x=(p[1]-self.b)/self.m
        return abs(p[0]-x)
    
class Ray(Line):
    """An infinite ray, with apex p and passing through
        q."""
    
    def __init__(self,p=[0,0],q=[1,1],color="grey",inf_precision=True):
        
        Line.__init__(self,p=p,q=q,color=color,inf_precision=inf_precision)
        self.apex=p
        self.q=q
    
    def point_in_self(self,p):
        
        if self.point_in_line(p)!=0:
            return False
        q_trans=[self.q[0]-self.apex[0],self.q[1]-self.apex[1]]
        p_trans=[p[0]-self.apex[0],p[1]-self.apex[1]]
        if (q_trans[0]*p_trans[0]<0 or
            q_trans[1]*p_trans[1]<0):
            return False
        return True
    
class LineSegment(Line):
    
    def __init__(self,p=[0,0],q=[1,1],color="grey",inf_precision=True):
        """Line segment with end points p and q"""
        Line.__init__(self,p=p,q=q,color=color,inf_precision=inf_precision)
        self.p=p
        self.q=q
        self.inf_precision=inf_precision
        
    def point_in_self(self,r):
        
        ray_self=Ray(p=self.p,q=self.q,inf_precision=self.inf_precision)
        if ray_self.point_in_self(r):
            q_trans=[self.q[0]-self.p[0],self.q[1]-self.p[1]]
            r_trans=[r[0]-self.p[0],r[1]-self.p[1]]
            if (abs(r_trans[0])<=abs(q_trans[0]) and
                abs(r_trans[1])<=abs(q_trans[1])):
                return True
        return False
    
def ConvexPolygon():
    
    def __init__(self,points=[],bounded=True,inf_precision=True):
        """Constructor for a convex polygon. The points
        should be given in clockwise order."""
        
        self.points=points
        if len(self.points)==0:
            self.bounded=False
            self.whole_plane=True
        else:
            self.bounded=bounded
            self.whole_plane=False
        
        self.inf_precision=inf_presicion    
        self.boundary_edges=[]
        if not self.bounded:
            p=self.points[0]
            q=self.points[1]
            q=[q[0]-p[0],q[1]-p[1]]
            q=[-q[0],-q[1]]
            q=[q[0]+p[0],q[0]+p[1]]
            ray=Ray(p=p,q=q,inf_precision=self.inf_precision)
            self.boundary_edges.append(ray)
        for i in range(len(self.points)-1):
            p=self.points[i]
            q=self.points[i+1]
            s=LineSegment(p=p,q=q,inf_precision=self.inf_precision)
            self.boundary_edges.append(s)
        if self.bounded:
            p=self.points[len(points)-1]
            q=self.points[0]
            s=LineSegment(p=p,q=q,inf_precision=self.inf_precision)
            self.boundary_edges.append(s)
        else:
            p=self.points[len(self.points)-1]
            q=self.points[len(self.points)-2]
            q=[q[0]-p[0],q[1]-p[1]]
            q=[-q[0],-q[1]]
            q=[q[0]+p[0],q[0]+p[1]]
            ray=Ray(p=p,q=q,inf_precision=self.inf_precision)
            self.boundary_edges.append(ray)
                
                                
    def intersection(self,l):
        """Computes the intersections with an object
           of the line family"""
        boundary_intersections=[]
        for li in self.boundary_edges:
            r=li.intersection(l)
            if r!=None:
                boundary_intersections.append(r)
        return boundary_intersections
    
#class ConvexWedge(ConvexPolygon):
#    
#    def poylgon_intersection(pol):
#        """Intersects this wedge with a polygon.
#           This intersections is either None or a polygon"""
#        pass
                
            
            
    
            
