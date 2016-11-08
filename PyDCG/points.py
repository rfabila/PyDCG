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

"""Module providing point set generators to many families of point sets.
   It also provides access to Graz's order point database for n=6,7,8,9,10"""
import struct
import geometricbasics
import crossing
import math
import os
import pickle
import datetime
import ConfigParser
import random
import string
import holes
import kgons
import line
import fractions
from fractions import gcd

sqrt_3=fractions.Fraction(173205,100000)

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
    
    file_name = os.path.join(config.pydcgDir, "point_sets/otypes")
    
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
    
    try:
        pts_file=open(file_name,"rb")
        pts=read_point_set()
        while pts!="EOF":
            yield pts
            pts=read_point_set()
        pts_file.close()
    except IOError:
        #TODO: finish this!
        pass


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

def koshelev_set():
    """Returns the two-colored set of 46 points with no monochromatic convex four holes
       found by Koshelev."""
    prefix = os.path.join(os.path.dirname(__file__), "point_sets/")
    file_name=prefix+"koshelev.pkl"
    file_pts=open(file_name,"r")
    pts=pickle.load(file_pts)
    file_pts.close()
    return pts

#Point set zoo functions. This are the best sets that optimize a certain parameter.
#The format is {n:{"val":xxxx},{"pts",xxxx},{"user",xxxx},{"comment",}}
def read_species(name):
    name = os.path.join(os.path.dirname(__file__),"point_sets/"+name+".pkl")
    file_pts=open(name,"r")
    D=pickle.load(file_pts)
    file_pts.close()
    return D
    

def best_specimen(name,n):
    D=read_species(name)
    return D[n]["pts"]
    
#functions for specific species

def best_rectilinear_crossing_number_pts(n):
    """Returns the best known example for rectilinear crossing number."""
    return best_specimen("rectilinear_crossing_number",n)

def best_empty_convex_pentagons_pts(n):
    """Returns the best known example for empty convex pentagons."""
    return best_specimen("empty_convex_pentagons",n)

def best_empty_triangles_pts(n):
    """Returns the best known example for empty triangles."""
    return best_specimen("empty_triangles",n)

def best_empty_convex_quadrilaterals_pts(n):
    """Returns the best known example for empty convex quadrilaterals."""
    return best_specimen("empty_convex_quadrilaterals",n)

def best_empty_convex_hexagons_pts(n):
    """Returns the best known example for empty convex hexagons."""
    return best_specimen("empty_convex_hexagons",n)

def best_halving_lines_pts(n):
    """Returns the best known example for halving lines."""
    return best_specimen("halving_lines",n)

#submitting functions
def _pack_sp(pts,species,comment="",user_id=None):
    if not geometricbasics.general_position(pts):
        #this should probably be an exception
        print "Point set not in general position!! I ain't sending nothing."

        return None
    sp={}
    sp['comment']=comment
    sp['pts']=pts
    date_discovered=datetime.datetime.today()
    sp['date_discovered']=date_discovered
    if user_id==None:
        config=ConfigParser.RawConfigParser()
        home=os.path.expanduser("~")
        print home+'.pydcg/pydcg.cfg'
        config.read(home+'/.pydcg/pydcg.cfg')
        user_id=config.get('user info','user_id')
        print user_id
    sp['user_id']=user_id
    return sp

def _submit_point_set_list(P,species,comment=" ",user_id=None):
    os.system("mkdir temp_subs")
    for pts in P:
        sp=_pack_sp(pts,species,comment=comment,user_id=user_id)
        #to avoid collisions
        date_discovered=datetime.datetime.today()
        idx=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        name=str(len(pts))+"_"+species+"_"+str(date_discovered.date())+"_"+idx+".sp"
        name="temp_subs/"+name
        print name
        file_sp=open(name,"w")
        pickle.dump((species,sp),file_sp)
        file_sp.close()
    com="scp temp_subs/* naturalist@monk.math.cinvestav.mx:~/naturalist/captured_specimens/"
    os.system(com)
    os.system("rm temp_subs/*")
    os.system("rmdir temp_subs")
        

def _submit_point_set(pts,species,comment=" ",user_id=None):
    sp=_pack_sp(pts,species,comment=comment,user_id=user_id)
    #to avoid collisions
    date_discovered=datetime.datetime.today()
    idx=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    name=str(len(pts))+"_"+species+"_"+str(date_discovered.date())+"_"+idx+".sp"
    file_sp=open(name,"w")
    pickle.dump((species,sp),file_sp)
    file_sp.close()
    com="scp "+name+" naturalist@monk.math.cinvestav.mx:~/naturalist/captured_specimens/"
    os.system(com)
    #print com
    os.system("rm "+name)

#submitting functions for specific species
def submit_rectilinear_crossing_number(pts,user_id=None,comment=None):
    _submit_point_set(pts,"rectilinear_crossing_number",comment=comment,user_id=user_id)

def submit_empty_convex_pentagons(pts,user_id=None,comment=None):
    _submit_point_set(pts,"empty_convex_pentagons",comment=comment,user_id=user_id)

def submit_empty_triangles(pts,user_id=None,comment=None):
    _submit_point_set(pts,"empty_triangles",comment=comment,user_id=user_id)

def submit_empty_convex_quadrilaterals(pts,user_id=None,comment=None):
    _submit_point_set(pts,"empty_convex_quadrilaterals",comment=comment,user_id=user_id)

def submit_empty_convex_hexagons(pts,user_id=None,comment=None):
    _submit_point_set(pts,"empty_convex_hexagons",comment=comment,user_id=user_id)
    
def submit_halving_lines(pts,user_id=None,comment=None):
    _submit_point_set(pts,"halving_lines",comment=comment,user_id=user_id)
    
#SQUARED HORTON SET FUNCTIONS

def random_tree(k):
    """Creates a random tree for the creation of the random Horton set."""
    
    if random.randint(0,1)==0:
            val=True
    else:
        val=False
    
    if k<=0:
        return [val,None,None]
    
    T1=random_tree(k-1)
    T2=random_tree(k-1)
    return [val,T1,T2]

def canonic_tree(k):
    val=False
    if k<=0:
        return [val,None,None]
    
    T1=canonic_tree(k-1)
    T2=canonic_tree(k-1)
    return [val,T1,T2]
    
    
def _horton_tree(k,tree):
    """Returns the Horton set of 2^k points."""
    
    if k<=0:
        return [[0,0]]
    
    if k<=1:
        g_k=0
        f_k=0
        
    else:
        f_k=2**((k*(k-1)/2)-1)
        if k<=2:
            f_k_1=0
        else:
            f_k_1=2**(((k-1)*(k-2)/2)-1)
        g_k=f_k-f_k_1
        g_k=g_k**2
        
    if tree[0]:
        g_k=-g_k

    
    H_even=_horton_tree(k-1,tree[1])
    H_odd=_horton_tree(k-1,tree[2])
    H_even=[[2*x[0],x[1]] for x in H_even]
    H_odd=[[2*x[0]+1,x[1]+g_k] for x in H_odd]
    H=[]
    for i in range(len(H_even)):
        H.append(H_even[i])
        H.append(H_odd[i])
        
    return H

def _check_hortoness(pts):

    if len(pts)<=2:
        return True
    
    H_even=[]
    H_odd=[]
    n=len(pts)
    
    for i in range(n):
        if i%2==0:
            H_even.append(pts[i])
        else:
            H_odd.append(pts[i])
    
    sign=geometricbasics.turn(H_even[0],H_even[1],H_odd[0])
    for i in range(len(H_even)):
        for j in range(i+1,len(H_even)):
            for k in range(len(H_odd)):
                sign2=geometricbasics.turn(H_even[i],H_even[j],H_odd[k])
                if sign*sign2<=0:
                    print (H_even[i],H_even[j],H_odd[k])
                    return False
                    
    sign=geometricbasics.turn(H_odd[0],H_odd[1],H_even[0])
    for i in range(len(H_odd)):
        for j in range(i+1,len(H_odd)):
            for k in range(len(H_even)):
                sign2=geometricbasics.turn(H_odd[i],H_odd[j],H_even[k])
                if sign*sign2<=0:
                    print (H_odd[i],H_odd[j],H_even[k])
                    return False
                
    if check_hortoness(H_even) and check_hortoness(H_odd):
        return True
    else:
        return False

def minkowski_sum(P,Q):
    M=[]
    for p in P:
        for q in Q:
            M.append([p[0]+q[0],p[1]+q[1]])
    return M

def _get_CX(pts):
    """Constructs the X component for the minkowski sum from the given point set"""
    
    max_y=max(pts,key=lambda x:x[1])
    min_y=min(pts,key=lambda x:x[1])
    h=abs(max_y[1]-min_y[1])
    return (10*len(pts)*h+1)/2

def _get_CY(pts):
    """Constructs the Y component for the minkowski sum from the given point set"""
    
    max_y=max(pts,key=lambda x:x[1])
    min_y=min(pts,key=lambda x:x[1])
    h=abs(max_y[1]-min_y[1])
    k=0
    n=len(pts)
    while n>1:
        n=n/2
        k=k+1
    n=len(pts)
    return ((20*n*((n+1)**(k+1)))*h+1)/2

def _squared_Horton_set_from_trees(k,T1,T2):
    H1=_horton_tree(k,T1)
    H2=_horton_tree(k,T2)
    CX=_get_CX(H1)
    CY=_get_CY(H2)
    H1=[[CX*CY*x[0],CY*x[1]] for x in H1]
    H2=[[CX*CY*x[0],CX*x[1]] for x in H2]
    #reflect points
    H2=[[p[1],p[0]] for p in H2]
    
    return minkowski_sum(H1,H2)



def random_squared_Horton_set(n):
    """Returns a random squared horton_set of size nxn"""
    k=1
    m=n
    while m>1:
        m=m/2
        k=k+1
        
    T1=random_tree(k)
    T2=random_tree(k)
    H1=_horton_tree(k,T1)
    H2=_horton_tree(k,T2)
    CX=_get_CX(H1)
    CY=_get_CY(H2)
    H1=[[CX*CY*x[0],CY*x[1]] for x in H1]
    H2=[[CX*CY*x[0],CX*x[1]] for x in H2]
    H1=H1[:n]
    H2=H2[:n]
    #H2=reflect_pts(H2)
    H2=[[p[1],p[0]] for p in H2]
    return minkowski_sum(H1,H2)

def _canonic_tree(k):
    val=False
    if k<=0:
        return [val,None,None]
    
    T1=_canonic_tree(k-1)
    T2=_canonic_tree(k-1)
    return [val,T1,T2]

#ERDOS-SZEKERES constructions

def _split_index(k,l):
    idx=math.factorial(k+l-5)/(math.factorial(l-2)*(math.factorial(k-3)))
    return (idx-1,idx)

def _separate_sets(L,R,k,l,dx):
    
    max_dy=1
    #print "separating",k,l,dx
    if len(L)>=2:
        (i,j)=_split_index(k-1,l)
        lx=R[-1][0]
        ly=R[-1][1]
        ll=line.Line(p=L[i],q=L[j], inf_precision=True)
        dy=int(ll.m*(lx+dx)+ll.b-ly+1)
        #print "L", i,j
        #print "dy",dy
        if dy>max_dy:
            max_dy=dy
    
    R=[[x[0]+dx,x[1]] for x in R]
    
    if len(R)>=2:
        (i,j)=_split_index(k,l-1)
        ll=line.Line(p=R[i],q=R[j], inf_precision=True)
        dy=abs(ll.b)+1
        #print dy
        dy=int(dy)
        #print dy
        #print R[i], R[j]
        #print L[0]
        #print "R", i,j
        #print "dy",dy
        if dy>max_dy:
            max_dy=dy
    
    R=[[x[0],x[1]+max_dy] for x in R]
    L=[x[:] for x in L]
    L.extend(R)
    return L



def _X_kl_array(s,test=False):
    """Auxiliary function to construct the sets described by Erdos and Szkeres with no k_cup or k_cap.
       It returns an array that contains each set $X_{i,j}$ with $i+j\le k+l$."""
    P=[[None for i in range(s+1)] for j in range(s+1)]
    
    for i in range(3):
        for j in range(s+1):
            P[i][j]=[[0,0]]
            
    for j in range(3):
        for i in range(s+1):
            P[i][j]=[[0,0]]
    
    P[3][3]=[[0,0], [1,0]]
            
    for t in range(3,s+1):
        for i in range(3,t-2):
            #print "%%%%%"
            j=t-i
            #print i,j
            if P[i][j]==None:
                L=[x[:] for x in P[i-1][j]]
                R=[x[:] for x in P[i][j-1]]
                
                if t!=s:
                    dx=(L[-1][0]+R[-1][0])/2+1
                    #print dx
                    dx=sqrt_3*dx+L[-1][0]
                    #print float(dx)
                    dx=int(dx)
                    #print dx
                else:
                    #print "t=",s
                    #print i,j
                    dx=1+L[-1][0]
                    #print dx
                    
                pts=_separate_sets(L,R,i,j,dx)
                
                if test:
                    if not geometricbasics.general_position(pts):
                        print "GENERAL POSITION FAILED!"
                        print i,j
                    if (kgons.max_cup(pts)!=i-1 or
                        kgons.max_cap(pts)!=j-1):
                        print "CAPS and CUPS FAILED!"
                        print i,j
                        
                P[i][j]=pts
                
    return P

def _get_origins(lstP):
    """Auxiliary function used to construct the set by Erdos and Szekeres.
       It creates the points by which we translate copies of X_{k,l},"""
    V=[]
    v=[0,0]
    for i in range(1,len(lstP)):
       # print "corner",v
        v=[v[0]-1,v[1]-1]
        tx=lstP[i][-1][0]
        ty=lstP[i][-1][1]
        v=[v[0]-tx,v[1]-ty]
        #print "origin",v
        V.append(v)
        tx=lstP[i-1][-1][0]
        ty=lstP[i-1][-1][1]
        v=[v[0]-tx,v[1]-ty]
        
    
    #print V
    
    dx=-v[0]+1
    V=[[x[0]+dx,x[1]-1] for x in V]
    
    origins=[[0,0]]
    for v in V:
        u=origins[-1]
        u=[u[0]+v[0],u[1]+v[1]]
        origins.append(u)
    
    #print V
    #print origins
    
    return origins
def X(k,l):
    """Returns the set $X_{k,l}$ described by Erdos and Szekers. It does not contain
    a k-cup nor a l-cap"""
    P=_X_kl_array(k+l)
    return P[k][l]

def ES(r):
    """Constructs the set of $2^{r-2}$ points described by Erdos and Szekeres with
    no $r$-gon."""
    P=_X_kl_array(r+2)
    lstP=[P[r-i][i+2] for i in range(r)]
    #print [x[-1] for x in lstP]
    origins=_get_origins(lstP)
    Q=[]
    T=[]
    for i in range(r-1):
        o=origins[i]
        pts=[[x[0]+o[0],x[1]+o[1]] for x in P[r-i][i+2]]
        Q.extend(pts)
        T.append(pts)
    #print T
    return Q

############################################################################

def createUpperVisibleVectors(n):
    vectors = []
    k = 1
    vectors += [[1,0], [0,1]]
    while True:
        k += 1
        for i in xrange(1, k):
            j = k - i
            if (gcd(i, j) == 1):
                if len(vectors) < n:
                    vectors.append([i,j])
                else:
                    break
                if len(vectors) < n:
                    vectors.append([-i, j])
                else:
                    break
        if len(vectors) >= n:
            break
    vectors = geometricbasics.sort_around_point_py([0,0], vectors)
    return vectors

def createVisibleVectors(n):
    vectors = createUpperVisibleVectors(n)
    for i in xrange(n):
        p = vectors[i][:]
        p[0]-=1
        p[1]-=1
        vectors.append(p)
    return vectors

def zigzagVectors(vectors):
    for i in xrange(len(vectors)-1, 2):
        w_i_3 = [vectors[i+1][0]*2 + vectors[i][0], vectors[i+1][1]*2 + vectors[i][1]]
        w_i1_3 = [vectors[i+1][0] + vectors[i][0]*2, vectors[i+1][1] + vectors[i][1]*2]
        vectors[i] = w_i_3
        vectors[i+1] = w_i1_3

def generateDoubleCirclePoints(set_size):
    points = []
    if set_size % 2:
        return #not implemented

    vectors = createVisibleVectors(set_size/2)
  
    zigzagVectors(vectors)
    points.append([0,0])
    set_size -= 1

    it = 0
    x_smallest = 0
    while set_size:
        p = [0,0]
        p[0] = points[-1][0] + vectors[it][0]
        p[1] = points[-1][1] + vectors[it][1]
        if p[0] < x_smallest:
            x_smallest = p[0]
        points.append(p);
        it += 1
        set_size -= 1

    for p in points:
        p -= x_smallest

    return points

def generateDoubleChain(a, b, zigzag = False):
    points = []
    if a < b:
        a, b = b, a

    vectors = createUpperVisibleVectors(a*2)

    points_a = []
    points_b = []
  
    if zigzag:
        zigzagVectors(vectors)
  
    points_a.append([0,0])
    it = a/2+1
    if zigzag:
        it -= (a/2 + 1) % 2
    for i in xrange(a-1):
        points_a.append([points_a[-1][0]+vectors[it][0], points_a[-1][1]+vectors[it][1]])
        it += 1
    points_b.append([0,0])
    it = a - (b-1)/2
    if zigzag:
        it += (a - (b-1)/2) % 2

    for i in xrange(b-1):
        points_b.append([points_b[-1][0] - vectors[it][0], points_b[-1][1] + vectors[it][1]])
        it += 1
  
    diff = points_a[-1][1] - points_b[-1][1];
    diff /= 2;
    for pb in points_b:
        pb[1] += diff
        pb[0] += points_a[-1][1]+1
    
    return points_a+points_b