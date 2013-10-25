import random
import math
import time
#import holes

def kirkpatrick_cooling(start_temp,alpha):
    T=start_temp
    while True:
        yield T
        T=alpha*T


def rand_move(p,t=1000000):
    """Moves point uniformly on a kxk square randomly to a new location"""
    l=1.0/max(float(t),1)
    tx=random.expovariate(l)
    l=1.0/max(float(t),1)
    ty=random.expovariate(l)
    tx=int(tx)
    ty=int(ty)
    if random.randint(0,1)==0:
        tx=-tx
    if random.randint(0,1)==0:
        ty=-ty
    p[0]=p[0]+tx
    p[1]=p[1]+ty
        
        

def P(vcurrent,vnew,T,minimize=True):
    """Computes the probability of accepting the new value.
       It also runs the corresponding probabilitic trial.
       Returns True if the solution should be accepted
       false otherwise."""
       
    df=vcurrent-vnew
    if not minimize:
        df=-df
    if df>=0:
        return True
    
    df=float(df)
    p=math.exp(df/float(T))
    #print(p)
    if random.random()<=p:
        return True
    return False
    
    
#Hay un error con holes puse f=[] pero queria poner countEmptyTriangs
#usr/lib/python2.7/site-packages/PyDCG/holes.py in <module>()
#    396     return (A,B)
#    397 
#--> 398 @accelerate_p(holesCpp.report_empty_triangles_p)
#    399 def report_empty_triangles_p(p,points):
#    400     """Returns (A,B). Where A is a list with the empty triangles
#
#AttributeError: 'module' object has no attribute 'report_empty_triangles_p'

def simmulated_annealing(n=10,pts=[],run_time=10,k=10000000,k_f=kirkpatrick_cooling(10000000,0.999),
                         t=1000000,f=[],T=kirkpatrick_cooling(100,0.999),rand_move=rand_move,minimize=True,
                         print_function=None):
    """Implementation of a simulated annealing algorithm to search for good point sets."""

    for i in range(len(pts),n):
        pts.append([random.randint(-k,k),random.randint(-k,k)])
        
    n=len(pts)
    start_time=time.time()
    vcurrent=f(pts)
    while time.time()-start_time<run_time:
        idxp=random.randint(0,n-1)
        p=pts[idxp]
        q=p[:]
        rand_move(p,int(k_f.next()))
        vnew=f(pts)
        if P(vcurrent,vnew,T.next(),minimize=minimize):
            if vnew!=vcurrent:
                if print_function==None:
                    print (vnew)
                else:
                    print_function(vnew)
            vcurrent=vnew
        else:
            p[0]=q[0]
            p[1]=q[1]
        
    return pts
    
#def simmulated_annealing_onepoint(n=10,pts=[],run_time=10,k=10000000,k_f=kirkpatrick_cooling(10000000,0.99),
#                         t=1000000,f=geometricbasicspy.count_convex_rholes,g=geometricbasicspy.count_convex_rholes_difference,
#                         T=kirkpatrick_cooling(100,0.99),r=3):
#    """Implementation of a simulated annealing algorithm to search for good point sets.
#    It takes advantage of the fact that only one point is moved."""
#
#    for i in range(len(pts),n):
#        pts.append([random.randint(-k,k),random.randint(-k,k)])
#        
#    n=len(pts)
#    start_time=time.time()
#    vcurrent=f(pts)
#    while time.time()-start_time<run_time:
#        idxp=random.randint(0,n-1)
#        p=pts[idxp]
#        q=p[:]
#        rand_move(q,int(k_f.next()))
#        vnew=vcurrent+g(p,q,pts)
#        if P(vcurrent,vnew,T.next()):
#            if vnew!=vcurrent:
#                print (vnew)
#            vcurrent=vnew
#            p[0]=q[0]
#            p[1]=q[1]
#        
#    return pts