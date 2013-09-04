"""Implementation of the basic geometric primitives"""

import ctypes
import pickle
import random

point_c=ctypes.c_long*2
__config_file=open("config/geometricbasics.config","r")
__config=pickle.load(__config_file)
__config_file.close()

lib_geometricbasics=ctypes.CDLL('src/geometricbasics')


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
    if t >0:
        return 1
    else:
        if t < 0:
            return -1
    return 0

def sorted(p,pts):
    """Checks whether the point set is sorted around p"""
    for i in range(len(pts)-1):
        if turn(p,pts[i],pts[i+1])>0:
            return False
    return True

def __test_sort_around_point_versions(n=100,k=10000000):
    """Tests whether the two sort_around_point functions match"""
    pts=[[random.randint(-k,k),random.randint(-k,k)] for i in range(n)]
    p=[random.randint(-k,k),random.randint(-k,k)]
    #p=[0,0]
    pts_1=sort_around_point_python(p,pts)
    pts_2=sort_around_point_C(p,pts)
    j=1
    print(j)
    while(pts_1==pts_2):
        pts=[[random.randint(-k,k),random.randint(-k,k)] for i in range(n)]
        #p=[0,0]
        p=[random.randint(-k,k),random.randint(-k,k)]
        pts_1=sort_around_point_python(p,pts)
        pts_2=sort_around_point_C(p,pts)
        j=j+1
        print j
    return (p,pts)
    
def sort_around_point_C(p,points):
    n=len(points)
    lib_geometricbasics.sort_around_point.argtypes=[point_c,ctypes.ARRAY(point_c,n),ctypes.c_long]
    
    arrpts=point_c*n
    pts_c=arrpts()
    for i in range (n):
        pts_c[i][0]=points[i][0]
        pts_c[i][1]=points[i][1]
    
    p_c=point_c()
    p_c[0]=p[0]
    p_c[1]=p[1]
        
    lib_geometricbasics.sort_around_point(p_c,pts_c,n)
    res_pts=[[pts_c[i][0],pts_c[i][1]] for i in range(n)]
    return res_pts
     
def sort_around_point(p,points,join=True,speedup=False):
    """Sorts a set of points by angle around
      a point p. If Join is set to False then a tuple
      (l,r) is returned. l contains the points to the left
      of p and r the points to the right. Both are sorted
      by angle around p. If true it returs the union
      of l and r. p should not be in points"""
    if speedup=="try":
        speedup=safe_point_set(pts)
        
    if speedup==False:
        return sort_around_point_python(p,points,join=join)
    elif speedup==True:
        pts=sort_around_point_C(p,points)
        if join:
            return pts
        else:
            l=[]
            r=[]
            for x in pts:
                if x[0]>p[0]:
                    r.append(x)
                elif x[0]<p[0]:
                    l.append(x)
                elif x[1]>p[1]:
                    r.append(x)
                else:
                    l.append(x)
            return (r,l)
                         
      
def sort_around_point_python(p,points,join=True):
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

def iterate_over_points(pts,f):
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
                
