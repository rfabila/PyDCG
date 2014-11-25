"""Module providing point set generators to many families of point sets.
   It also provides access to Graz's order point database for n=6,7,8,9,10"""
import struct
import geometricbasics
import math
import os
import pickle

def horton_set(n):
    """Returns a set of n points with the same order type
    as the Horton Set. It should be pointed out that horton
    sets have 2^k points in the case for when n is not a power
    of 2 we compute the Horton set of 2^k points for the first
    value of k such that 2^k>=n. Afterwards we just return
    the first n points.
    
    For more details see our paper: Drawing the Horton Set in an Integer Grid of Minimum Size """
    
    k=int(math.ceil(math.log(n,2)))
    
    H=_horton_exp(k)
    return H[:n]
    
    
def _horton_exp(k):
    """Returns the Horton set of 2^k points."""
    
    if k<=0:
        return [[0,0]]
    
    if k<=1:
        g_k=0
        
    else:
        f_k=2**((k*(k-1)/2)-1)
        if k<=2:
            f_k_1=0
        else:
            f_k_1=2**(((k-1)*(k-2)/2)-1)
        g_k=f_k-f_k_1
        
    H_k_1=_horton_exp(k-1)
    H_even=[[2*x[0],x[1]] for x in H_k_1]
    H_odd=[[2*x[0]+1,x[1]+g_k] for x in H_k_1]
    H=[]
    for i in range(len(H_even)):
        H.append(H_even[i])
        H.append(H_odd[i])
        
    return H

#Access to the Graz order type database
def point_set_iterator(n):
    """Returns an iterator that provides integer coordinate realizations
        of every ordertype  n points"""
        
    def read_point_set():
        pts=[]
        for i in range(n):
            s=pts_file.read(b)
            if s=='':
                return "EOF"
            point=struct.unpack(t,s)
            pts.append([point[0],point[1]])
        return pts
    
    file_name = os.path.join(os.path.dirname(__file__), "point_sets/otypes")
    
    if n<3 or n>10:
        raise OutOfBoundsError()
    
    if n<10:
        file_name+="0"+str(n)
    elif n==10:
        file_name+="10"
    
    if n<9:
        file_name+=".b08"
        b=2
        t="BB"
    else:
        file_name+=".b16"
        b=4
        t="HH"
    
    pts_file=open(file_name,"rb")  
    pts=read_point_set()
    while pts!="EOF":
        yield pts
        pts=read_point_set()
    pts_file.close()  

def point_set_array(n):
    """Returns an an array with integer coordinate realizations of every
        ordertype of n points"""
    pts=[]
    pts_n=point_set_iterator(n)
    for P in pts_n:
        pts.append(P)
    return pts
        
def three():
    """Returns an array with integer coordinate realizations of every
        ordertype of 3 points"""
    return point_set_array(3)

def four():
    """Returns an array with integer coordinate realizations of every
        ordertype of 4 points"""
    return point_set_array(4)
     
def five():
    """Returns an array with integer coordinate realizations of every
        ordertype of 5 points"""
    return point_set_array(5)

def six():
    """Returns an array with integer coordinate realizations of every
        ordertype of 6 points"""
    return point_set_array(6)
    
def seven():
    """Returns an array with integer coordinate realizations of every
        ordertype of 7 points"""
    return point_set_array(7)

def eight():
    """Returns an array with integer coordinate realizations of every
        ordertype of 8 points"""
    return point_set_array(8)

def nine():
    """Returns an array with integer coordinate realizations of every
        ordertype of 9 points"""
    return point_set_array(9)

def ten():
    """Returns an iterator that provides integer coordinate realizations of every
       ordertype of 10 points. It uses a LOT of memory; use at your own risk.
       Perhaps you should use the iterator point_set_iterator(10) instead"""
    return point_set_array(10)   
        
class OutOfBoundsError(Exception):
    pass

#Point set Generators.

def _jarnik_polygon(V):
    """Constructs a point set using the set of vectors V."""
    points=[[0,0] for i in range(len(V))]
    for i in range(1,len(V)):
        points[i][0]=points[i-1][0]+V[i-1][0]
        points[i][1]=points[i-1][1]+V[i-1][1]
    return points

#def _gcd(a,b):
 #   if a == 0:
  #      return b
   # return _gcd(b % a, a)

def _gcd_dict(n):
    m=int(math.ceil(1.5*math.sqrt(float(n))))
    #m=m/2
    #print m
    gcd=[[0 for i in range(m)] for j in range(m)]
    for i in range(1,m):
        gcd[i][i]=i
    for i in range(1,m):
        for j in range(i+1,m):
            if i<=j-i:
                gcd[i][j]=gcd[i][j-i]
                gcd[j][i]=gcd[i][j-i]
            else:
                gcd[i][j]=gcd[j-i][i]
                gcd[j][i]=gcd[j-i][i]
    return gcd
    
def _visible_points(n):        
    """Returns the first n points visibible from
        the origin in the integer grid."""
    V=[[1,0],[-1,0],[0,1],[0,-1]]
    gcd=_gcd_dict(n)
    k=2
    while len(V)<n:
        for i in range(1,k):
            j=k-i
            if gcd[i][j]==1:
                #V=V+[[i,j],[-i,-j]]
                V.append([i,j])
                V.append([-i,-j])
                if len(V)==n:
                    break
                #V=V+[[-i,j],[i,-j]]
                V.append([-i,j])
                V.append([i,-j])
                if len(V)==n:
                    break
        k=k+1
    #print k
    V=V[:n]
    return geometricbasics.sort_around_point([0,0],V)
    
def convex_position(n):
    """Returns a set of n points in convex and general
        position"""
    m=n+(-(n%4)%4)
    V=_visible_points(m)
    pts=_jarnik_polygon(V)
    return pts[:n]

def _check_convex_position(pts):
    """Checks whether the point set(in the given order) is in convex position."""
    n=len(pts)
    if n<3:
        return True
    
    for i in range(n):
        if geometricbasics.turn(pts[i],
                                pts[(i+1)%n],
                                pts[(i+2)%n])!=-1:
            return False
    return True
                                    

def _to_double_circle(V):
    W=[]
    for i in range(0,len(V),2):
        W.append(V[i+1])
        W.append(V[i])
    return W

def double_circle_test_BS(pts,debug=True):
    n=len(pts)
    for i in range(0,n,2):
        inicio=(i+3)%n
        fin=(i-1)%n
        if fin<inicio:
            fin = fin + n
        while inicio<=fin:
            j=(inicio+fin)/2
            if geometricbasics.turn(pts[i],pts[(i+1)%n],pts[j%n])<0:
                fin=j-1
            else:
                return False
        inicio=(i+1)%n
        fin=(i-3)%n
        if fin<inicio:
            fin = fin + n
        while inicio<=fin:
            j=(inicio+fin)/2
            if geometricbasics.turn(pts[i],pts[(i-1)%n],pts[j%n])>0:
                inicio=j+1
            else:
                return False

    return True


def double_circle(n):
    if n%2==1:
        n+=1
    
    V=_visible_points(n)
    V=_to_double_circle(V)
    W=[]
    for i in range(0,n,2):
        u=[3*V[i][0],3*V[i][1]]
        v=[V[(i+1)%n][0]-V[i][0],V[(i+1)%n][1]-V[i][1]]
        
        w=[u[0]+v[0],u[1]+v[1]]
        W.append(w)
        
        x=[u[0]+3*V[i+1][0],u[1]+3*V[i+1][1]]
        W.append([x[0]-w[0],x[1]-w[1]])
        
    pts=_jarnik_polygon(W)
    if n%2==1:
        pts.pop()
    
    return pts

def overmars_sets():
    prefix = os.path.join(os.path.dirname(__file__), "point_sets/set29_")
    P=[]
    for i in range(1,8):
        file_name=prefix+str(i)+".pkl"
        file=open(file_name,"r")
        pts=pickle.load(file)
        P.append(pts)
        file.close()
    return P
