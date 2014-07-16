# -*- coding: utf-8 -*-
"""Implementation of the basic geometric primitives"""

import pickle
import random
import os
from functools import wraps

__config_file=open(os.path.join(os.path.dirname(__file__), "config/geometricbasics.config"), "r")
__config=pickle.load(__config_file)
__config_file.close()

sort_around_point_C = None
if not __config['PURE_PYTHON']:
    import geometricbasicsCpp as gbCpp
    sort_around_point_C = gbCpp.sort_around_point


def safe_point_set(pts):
    """True if the it is safe to speed up with the given point set."""
    for p in pts:
        if (not safe_val(p[0])) or (not safe_val(p[1])):
            return False
    return True
        

def safe_val(n):
    """True if the it is safe to speed up with the given integer."""
    n=abs(n)
    if __config["MAX_INT"]>=n:
        return True
    return False

def turn(p0,p1,p2):
    """Consider the walk form p0 to p1 to p2. Returns
        -1 if it is a turn to the left, 1 if it is to the right
        and 0 otherwise"""
    t=((p2[0]-p0[0])*(p1[1]-p0[1]))-((p1[0]-p0[0])*(p2[1]-p0[1]))
    if t > 0:
        return 1
    elif t < 0:
        return -1
    return 0

def sorted(p,pts):
    """Checks whether the point set is sorted around p"""
    for i in range(len(pts)-1):
        if turn(p,pts[i],pts[i+1])>0:
            return False
    return True
    
#if __config['PURE_PYTHON']:
#    sort_around_point_C = sort_around_point

def __test_sort_around_point_versions(n=100,k=10000000):
    """Tests whether the two sort_around_point functions match"""
    pts=[[random.randint(-k,k),random.randint(-k,k)] for i in range(n)]
    p=[random.randint(-k,k),random.randint(-k,k)]
    #p=[0,0]
#    pts_1=sort_around_point_python(p,pts)
    pts_1=sort_around_point(p,pts)
    pts_2=sort_around_point_C(p,pts)
    j=1
    print(j)
    while(pts_1==pts_2):
        pts=[[random.randint(-k,k),random.randint(-k,k)] for i in range(n)]
        #p=[0,0]
        p=[random.randint(-k,k),random.randint(-k,k)]
#        pts_1=sort_around_point_python(p,pts)
        pts_1=sort_around_point(p,pts)
        pts_2=sort_around_point_C(p,pts)
        j=j+1
        print j
    return (p,pts)

#General decorator
def accelerate(cfunc):
    def bind_cfunc(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            speedup = False
            join = True
            if 'speedup' in kwargs:
                speedup = kwargs['speedup']
                del kwargs['speedup']
            if 'join' in kwargs:
                join = kwargs['join']
                
            if speedup == 'try':
                speedup = safe_point_set(kwargs['points'] if 'points' in kwargs else args[1])
                
#            print "Speedup", speedup
            if speedup and not join:
#                print "Llamando función de C++", func.func_name
                return cfunc(*args, **kwargs)
            else:
#                print "Llamando función de Python"
                return func(*args, **kwargs)
        return wrapper
    return bind_cfunc
    
#Signature specific decorator
#def accelerate(cfunc):
#    def bind_cfunc(func):
#        @wraps(func)
#        def wrapper(p, points, join=True, speedup=False):
#            
#            if speedup == 'try':
#                speedup = safe_point_set(points)
#            if not speedup:
#                print "Llamando función de Python", func.func_name
#                return func(p, points, join=True)
#            else:
#                print "Llamando función de C++"
#                return cfunc(p, points)
#        return wrapper
#    return bind_cfunc
    
     
#def sort_around_point(p,points,join=True,speedup=False):
#    """Sorts a set of points by angle around
#      a point p. If Join is set to False then a tuple
#      (l,r) is returned. l contains the points to the left
#      of p and r the points to the right. Both are sorted
#      by angle around p. If true it returs the union
#      of l and r. p should not be in points"""
#    if speedup=="try":
#        speedup=safe_point_set(points)
#        
#    if speedup==False:
#        return sort_around_point_python(p,points,join=join)
#    elif speedup==True:
#        pts=sort_around_point_C(p,points)
#        if join:
#            return pts
#        else:
#            l=[]
#            r=[]
#            for x in pts:
#                if x[0]>p[0]:
#                    r.append(x)
#                elif x[0]<p[0]:
#                    l.append(x)
#                elif x[1]>p[1]:
#                    r.append(x)
#                else:
#                    l.append(x)
#            return (r,l)
                         
#@accelerate(gbCpp.sort_around_point)
def sort_around_point(p,points,join=True, checkConcave = True):
    """Sorts each element of `points` around `p` in CCW order"""
    l=0
    r=0
    p1=[p[0],p[1]+1]
    for x in points:
       if turn(p,p1,x) > 0:
          r=r+1
       else:
          if turn(p,p1,x) <  0:
             l=l+1
          else:
             if p[1] >= x[1]:
                l=l+1
             else:
                r=r+1
    r=[[0,0] for i in range(r)]
    l=[[0,0] for i in range(l)]
    ir=0
    il=0
    for x in points:
       if turn(p,p1,x) > 0:
          r[ir]=x[:]
          ir=ir+1
       else:
          if turn(p,p1,x) <  0:
             l[il]=x[:]
             il=il+1
          else:
             if p[1] >= x[1]:
                l[il]=x[:]
                il=il+1
             else:
                r[ir]=x[:]
                ir=ir+1
                     
    l.sort(lambda v1,v2:turn(p,v1,v2))
    r.sort(lambda v1,v2:turn(p,v1,v2))
   
    if join:
       tpts=[[0,0] for i in range(len(points))]
       for i in range(len(r)):
          tpts[i]=r[i][:]
       for j in range(len(l)):
          tpts[len(r)+j]=l[j][:]
          
       if not checkConcave:
           return tpts
           
       concave=False
       for i in range(len(tpts)):
          if turn(tpts[i],p,tpts[(i+1)%len(tpts)])<0:
             concave=True
             break
       if concave:
          start=(i+1)%len(tpts)
          tpts=[tpts[(start+i)%len(tpts)][:] for i in range(len(tpts))]
      
      
       return tpts
    else:
       return (r,l)

############################## This used to be a decorator ###################
if not __config['PURE_PYTHON']:
    sort_around_point = accelerate(gbCpp.sort_around_point)(sort_around_point)
##############################################################################

def iterate_over_points(pts,f):                              #Se puede uar map (o alguna de esas)
    """Takes a function and a point set as a parameter.
       It applies f(p,pts-p) for every point p in pts"""
    res=[]
    tmp=[x[:] for x in pts[1:]]
    for i in range(len(pts)):
        for j in range(i):
            tmp[j]=pts[j][:]
        for j in range(i+1,len(pts)):
            tmp[j-1]=pts[j][:]
        res.append(f(pts[i],tmp))
    return res
                
    
def general_position(pts,report=False):
    """Tests whether the point set is in general position or not.
       If report is set to True it return all triples of points not in general position"""
    def f(p,pts):
        triples=[]
        tmp_pts=sort_around_point(p,pts)
        for i in range(len(tmp_pts)-1):
            if turn(p,tmp_pts[i],tmp_pts[i+1])==0:
                if report:
                    triples.append((p,tmp_pts[i],tmp_pts[i+1]))
                else:
                    return False
        if report:
            return triples
        else:
            return True
        
    res=iterate_over_points(pts,f)
    if report:
        return res
    else:
        for x in res:
            if not x:
                return False
        return True
                
