from math import sqrt
from geometricbasics import sort_around_point, turn
from collections import deque
import utilities
from utilities import cppWrapper

if not utilities.__config['PURE_PYTHON']:
    import holesCpp

def count_four_islands(pts,colored=False):
    """Counts the number of four-islands in a point set."""
    islands=(count_non_convex_four_islands(pts,colored=colored)+
                count_convex_rholes(pts,4,mono=colored))
    return islands

def count_mono_four_islands(pts):
    return count_four_islands(pts,colored=True)

def count_non_convex_four_islands(pts,colored=False):
    """Counts the number of non convex four islands."""
    tpts=[[0,0] for i in range(len(pts)-1)]
    non_convex=0
    for p in pts:
        i=0
        for x in pts:
            if x!=p:
                tpts[i]=x[:]
                i=i+1
        non_convex=non_convex+count_non_convex_four_islands_p(p,tpts,colored=colored)
    return non_convex

def count_emptymon_triangles_p(p,points):
    """Returns (A,B). Where A is the number of monochromatic empty triangles.
        that contain p as a vertex and B the number of triangles
        that contain only contain p in their interior."""
    G=visibility_graph_around_p(p,points)
    sorted_points=sort_around_point(p,points)
    A=0
    B=0
    color=p[2]
    for q in range(len(sorted_points)):
        I=G[q][0]
        O=G[q][1]
        if color==sorted_points[q][2]:
            for x in I:
                if color==sorted_points[x][2]:
                    A=A+1
        j=0
        for i in range(len(I)):
            while (j<len(O) and turn(sorted_points[I[i]],
                                             sorted_points[q],
                                             sorted_points[O[j]])>0):
                j=j+1
            if j<len(O):
                for k in range(j,len(O)):
                    if turn(p,
                              sorted_points[I[i]],
                              sorted_points[O[k]])>=0:
                        if (I[i] in G[O[k]][1] and
                             sorted_points[I[i]][2]==
                             sorted_points[O[k]][2]==
                             sorted_points[q][2]):
                                B=B+1
    B=B/3
    return (A,B)
    
def count_non_convex_four_islands_p(p,points,colored=False):
    """Counts the number of four islands containing p. CHECK, Maybe wrong"""
    G=visibility_graph_around_p(p,points)
    sorted_points=sort_around_point(p,points)
    B=0
    if colored:
        color=p[2]
    for q in range(len(sorted_points)):
        if (not colored) or color==sorted_points[q][2]:
            I=G[q][0]
            O=G[q][1]
            j=0
            for i in range(len(I)):
                while (j<len(O) and turn(sorted_points[I[i]],
                                                 sorted_points[q],
                                                 sorted_points[O[j]])>0):
                    j=j+1
                if j<len(O):
                    for k in range(j,len(O)):
                        #print p,sorted_points[I[i]],sorted_points[O[k]]
                        if (turn(p,sorted_points[I[i]],sorted_points[O[k]])>=0):
                            #print "hola"
                            if (I[i] in G[O[k]][1]):
                                if (not colored):
                                    B=B+1
                                elif (color==sorted_points[I[i]][2] and
                                        color==sorted_points[O[k]][2]):
                                    B=B+1
        
    B=B/3
    return B


def count_four_holes(pts,colored=False):
    """counts the number of 4-holes in a point set"""
    convex=count_convex_rholes(pts,4,mono=colored)
    non_convex=count_non_convex_four_holes(pts,colored=colored)
    return convex+non_convex

def count_mono_four_holes(pts):
    """Counts the number of monochromatic four holes
        in a point set"""
    return count_four_holes(pts,colored=True)

def count_non_convex_four_holes(pts,colored=False):
    """Counts the number of non-convex four holes
        in a point set"""
    temp_pts=[[0,0]for x in range(len(pts)-1)]
    non_convex=0
    for i in range(len(pts)):
        p=pts[i]
        if colored:
            color=pts[i][2]
        j=0
        for q in pts:
            if p!=q:
                temp_pts[j]=q[:]
                j=j+1
        G=visibility_graph_around_p(p,temp_pts)
        sorted_points=sort_around_point(p,temp_pts)
        for i in range(len(G)):
            if colored:
                if color==sorted_points[i][2]:
                    for x in G[i][0]:
                        for y in G[i][1]:
                            if (color==sorted_points[x][2] and
                                 color==sorted_points[y][2] and
                                 turn(sorted_points[x],
                                        sorted_points[i],
                                        sorted_points[y])>0):
                                    non_convex=non_convex+1
            else:
                for x in G[i][0]:
                        for y in G[i][1]:
                            if turn(sorted_points[x],
                                      sorted_points[i],
                                      sorted_points[y])>0:
                                    non_convex=non_convex+1
    return non_convex

#funcion para decidir si un punto p esta al interior dentro
#de un triangulo
def pointInTriang(p, triang):
    sign1 = turn(triang[0],p,triang[1])
    sign2 = turn(triang[1],p,triang[2])
    sign3 = turn(triang[2],p,triang[0])

    #p esta en la frontera
    if sign1==0 or sign2==0 or sign3==0: 
        return False

    if sign1 > 0:
        return sign2 > 0 and sign3 > 0
    else:
        return sign2 < 0 and sign3 < 0

#verifica si dos puntos son iguales
def pointEqual(p,q):
    return (p[0]==q[0]) and (p[1]==q[1])


#verifica si algun punto del arreglo
#esta contenido en el triangulo
def pointsInTriang(points,triang):
    for p in points:
        if pointInTriang(p,triang):
            return True
    return False
                     
#cuenta el numero de triangulos
#vacios en points (tiempo O(n^4))
def slowcountemptyTriang(points):
    num = 0
    for i in range(len(points)):
        for j in range(i+1,len(points)):
            for k in range(j+1,len(points)):
                if not pointsInTriang(points,[points[i],points[j],points[k]]):
                    num=num+1
    return num


#regresa  la distnacia entre dos puntos
def distance(p,q):
    return sqrt((p[0]-q[0])*(p[0]-q[0])+
                    (p[1]-q[1])*(p[1]-q[1]))

#regresa un arreglo de punto escalado en r
def scale(p,r):
    q=[]
    for v in p:
        q.append([int(round(v[0]*r)),
                     int(round(v[1]*r))])
    return q
                    

#regresa un arreglo de los puntos ordenados por angulo alrededor de x
# en dos listas
def orderandsplit(points):
    
    orderedpoints = []
    for p in points:
        l=[]
        r=[]
        p1=[p[0],p[1]+1]
        
        for x in points:
            if not p is x:
                if turn(p,p1,x) > 0:
                    r.append(x)
                else:
                    if turn(p,p1,x) <  0:
                        l.append(x)
                    else:
                        if p[1] >= x[1]:
                            l.append(x)
                        else:
                            r.append(x)
                            
        l.sort(lambda v1,v2:turn(p,v1,v2))
        r.sort(lambda v1,v2:turn(p,v1,v2))
        orderedpoints.append([p,r,l])
        
    return orderedpoints

def sortpoints(pts):
    ptsordsplit=orderandsplit(pts)
    for p in ptsordsplit:
        p[1].extend(p[2])
        p.pop()
    return ptsordsplit

def countEmptyTriangsVertex(rpoints):
    
    triangs=0
    q=[]
    
    #sacada verbatim(casi) de searching for empty convex polygons
    #Ojo agrego aristas cuando estan alineados los puntos
    def proceed(i,j):
        tmp=0
        while q[i] and turn(rpoints[q[i][0]],rpoints[i],rpoints[j])<=0:
            tmp=tmp+proceed(q[i][0],j)
            q[i].pop(0)
        
        q[j].append(i)
        return tmp+1

    for i in range(0,len(rpoints)):
        q.append([])
    
    for i in range(0,len(rpoints)-1):
        triangs=triangs+proceed(i,i+1)
        
    return triangs

#@accelerate(holesCpp.countEmptyTriangs)
def countEmptyTriangs_py(points):
    
    ordpoints=orderandsplit(points)
    triangs=0
    
    for i in range(0,len(points)):
        triangs=triangs+countEmptyTriangsVertex(ordpoints[i][1])
    
    return triangs
    
def countEmptyTriangs(points, speedup="try"):
    name = 'countEmptyTriangs'
    pyf = countEmptyTriangs_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.countEmptyTriangs
        
    return cppWrapper(name, pyf, cppf, speedup, points=points)


def slow_count_empty_triangles_p(p,points):
    """Slow version of count_triangles_p."""
    B=slow_count_empty_triangles_containing_p(p,points)
    A=count_empty_triangles_around_p(p,points)
    return (A,B)
    
#@accelerate_p(holesCpp.count_empty_triangles_p)    
def count_empty_triangles_p_py(p,points):
    """Returns (A,B). Where A is the number of empty triangles.
        that contain p as a vertex and B the number of triangles
        that contain only contain p in their interior."""
    G=visibility_graph_around_p(p,points)
    sorted_points=sort_around_point(p,points)
    A=0
    B=0
    for q in range(len(sorted_points)):
        I=G[q][0]
        O=G[q][1]
        A=A+len(I)
        j=0
        for i in range(len(I)):
            while (j<len(O) and turn(sorted_points[I[i]],
                                             sorted_points[q],
                                             sorted_points[O[j]])>0):
                j=j+1
            if j<len(O):
                for k in range(j,len(O)):
                    if turn(p,
                            sorted_points[I[i]],
                            sorted_points[O[k]])>=0:
                        if I[i] in G[O[k]][1]:
                                B=B+1
    B=B/3
    return (A,B)
    
def count_empty_triangles_p(p, points, speedup="try"):
    name = 'count_empty_triangles_p'
    pyf = count_empty_triangles_p_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.count_empty_triangles_p
        
    return cppWrapper(name, pyf, cppf, speedup, p=p, points=points)
    
#@accelerate_p(holesCpp.report_empty_triangles_p)
def report_empty_triangles_p_py(p,points):
    """Returns (A,B). Where A is a list with the empty triangles
        that have p as a vertex and B is a list with the triangles
        that contain only contain p in their interior."""
    G=visibility_graph_around_p(p,points)
    sorted_points=sort_around_point(p,points)
    A = []
    B_idx = set()
    for q in range(len(sorted_points)):
        incoming = G[q][0]
        outgoing = G[q][1]
        for r in incoming:
            A.append([p, sorted_points[q], sorted_points[r]])
        j = 0
        for i in range(len(incoming)):
            while (j < len(outgoing) and turn(sorted_points[incoming[i]],
                                             sorted_points[q],
                                             sorted_points[outgoing[j]]) > 0):
                j += 1
            if j < len(outgoing):
                for k in range(j,len(outgoing)):
                    if (turn(p, sorted_points[incoming[i]],
                             sorted_points[outgoing[k]]) >= 0 
                        and
                        incoming[i] in G[outgoing[k]][1]):
                        t = sorted([incoming[i], q, outgoing[k]])
                        B_idx.add(tuple(t))
    B=[]
    for t in B_idx:
        a,b,c = t
        B.append([sorted_points[a],sorted_points[b],sorted_points[c]])
    return (A,B)
    
def report_empty_triangles_p(p, points, speedup="try"):
    name = 'report_empty_triangles_p'
    pyf = report_empty_triangles_p_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.report_empty_triangles_p
        
    return cppWrapper(name, pyf, cppf, speedup, p =p, points=points)

    
def count_empty_triangles_pb(p,points):
    """Returns (A,B). Where A is the number of empty triangles.
        that contain p as a vertex and B the number of triangles
        that contain only contain p in their interior.
        Very slow used only for debugging"""
    def find(q,e,oedges,start,end):
        mid=(end-start)/2+start
        if end<start:
            return False
        if turn(q,sorted_points[oedges[mid]],sorted_points[e])>0:
            return find(q,e, oedges, start, mid-1)
        if turn(q,sorted_points[oedges[mid]],sorted_points[e])<0:
            return find(q,e,oedges,mid+1, end)
        return True
        
        
    G=visibility_graph_around_p(p,points)
    sorted_points=sort_around_point(p,points)
    A=0
    B=0
    for q in range(len(sorted_points)):
        I=G[q][0]
        O=G[q][1]
        A=A+len(I)
        j=0
        for i in range(len(I)):
            while (j<len(O) and turn(sorted_points[I[i]],
                                             sorted_points[q],
                                             sorted_points[O[j]])>0):
                j=j+1
            if j<len(O):
                for k in range(j,len(O)):
                    if find(sorted_points[q],I[i],G[O[k]][1],0,len(G[O[k]][1])-1):
                        B=B+1
    B=B/3
    return (A,B)
                            
                     
def slow_count_empty_triangles_containing_p(p,points):
    """Counts the number of emptuy triangles in points
        that contain p in their interior."""
        
    r=0
    for i in range(len(points)):
        for j in range(i+1,len(points)):
            for k in range(j+1,len(points)):
                t=[points[i],points[j],points[k]]
                if not pointsInTriang(points,t):
                    if pointInTriang(p,t):
                        r=r+1
    return r
                    

def count_empty_triangles_around_p(p,points):
    """Counts the number of empty triangles of
        points union p which contain p as a vertex.
        p should not be in points."""
    G=visibility_graph_around_p(p,points)
    triangs=0
    for N in G:
        triangs=triangs+len(N[0])
    return triangs

def count_empty_triangles_for_each_p(points):
    """Sums the the number of empty triangles
        containing each vertex and divides by 3"""
    pt=points[0]
    triangs=0
    for i in range(len(points)):
        pt=points[i]
        points[i]=points[0]
        points[0]=pt
        triangs=triangs+count_empty_triangles_around_p(points[0],points[1:])
    return triangs

def debug_count_empty_triangles_around_p(points):
    L=[]
    pt=points[0]
    for i in range(len(points)):
        print "punto:",points[i]
        pt=points[i]
        points[i]=points[0]
        points[0]=pt
        c=count_empty_triangles_around_p(points[0],points[1:])
        s=slow_count_empty_triangles_around_p(points[0],points[1:])
        if c!=s:
            print "diff=",s-c          
            L.append(points[0][:])
        pt=points[i]
        points[i]=points[0]
        points[0]=pt
    return L
        

def slow_count_empty_triangles_for_each_p(points):
    """Sums the the number of empty triangles
        containing each vertex and divides by 3"""
    pt=points[0]
    triangs=0
    for i in range(len(points)):
        pt=points[i]
        points[i]=points[0]
        points[0]=pt
        triangs=triangs+slow_count_empty_triangles_around_p(points[0],points[1:])
    return triangs
        
def slow_count_empty_triangles_around_p(p,points):
    triangs=0
    for i in range(len(points)):
        for j in range(i+1,len(points)):
            if not pointsInTriang(points,[p,points[i],points[j]]):
                triangs=triangs+1
    return triangs

def visibility_graph_around_p(p,points,debug=False):
    """Computes the visibility of the point set
    around p. The point set must not include p."""
    
    def proceed(i,j,first_pass):
        k=0
        while (k<len(Q[i]) and
                 turn(sorted_points[Q[i][k]],sorted_points[i],sorted_points[j])<=0):
            if(turn(p,sorted_points[Q[i][k]],sorted_points[j])<=0):
                proceed(Q[i][k],j,first_pass)
                Q[i].pop(k)
            else:
                k=k+1

        Q[j].append(i)
        #We add ij to the graph
        if not first_pass:
            vis_graph[j][0].append(i)
            vis_graph[i][1].append(j)
         
    (sorted_points,l)=sort_around_point(p,points,join=False)
    limit=len(sorted_points)
    
    sorted_points.extend(l)
    vis_graph=[[[],[]] for x in range(len(sorted_points))]
    Q=[[] for x in range(len(sorted_points))]
    
    #We check wheter p is a convex_hull point point.
    for i in range(len(sorted_points)):
        if turn(p,sorted_points[i],
                  sorted_points[(i+1)%len(sorted_points)])>=0:
            new_sorted_points=[0 for x in range(len(sorted_points))]
            for j in range(len(sorted_points)):
                new_sorted_points[j]=sorted_points[(i+1+j)%len(sorted_points)]
            sorted_points=new_sorted_points
            for j in range(len(sorted_points)-1):
                proceed(j,j+1,False)
            return vis_graph
    
    for j in range(limit-1):
        proceed(j,j+1,True)
    
    proceed(limit-1,limit,False)
        
    for j in range(limit,len(sorted_points)-1):
        proceed(j,j+1,False)
    
    vis_graph_temp=[vis_graph[x][1] for x in range(limit)]


    
    if debug:
        print "PRIMER COLA"
    
        for x in range(len(sorted_points)):
            print "cola de", x
            for q in Q[x]:
                print "cola:",q
    
    for i in range(limit):
        vis_graph[i][1]=[]
        Q[i]=[]
    
    proceed(len(sorted_points)-1,0,False)
    
    if debug:
        print "SEGUNDA COLA"
    
        for x in range(len(sorted_points)):
            print "cola de", x
            for q in Q[x]:
                print "cola:",q
    
    for j in range(limit-1):
        if debug:
            print j
        proceed(j,j+1,False)
    
    for i in range(limit):
        vis_graph[i][1].extend(vis_graph_temp[i])
        
    return vis_graph
        
def VGp(p,points,debug=False):
    """Computes the visibility of the point set
    around p. The point set must not include p."""
    
    def proceed(i,j,first_pass):
        k=0
        while (k<len(Q[i]) and
                 turn(sorted_points[Q[i][k]],sorted_points[i],sorted_points[j])<=0):
            if(turn(p,sorted_points[Q[i][k]],sorted_points[j])<=0):
                proceed(Q[i][k],j,first_pass)
                Q[i].pop(k)
            else:
                k=k+1

        Q[j].append(i)
        #We add ij to the graph
        if not first_pass:
            vis_graph[j][0].append(i)
            vis_graph[i][1].append(j)
         
    (sorted_points,l)=sort_around_point(p,points,join=False)
    limit=len(sorted_points)
    
    sorted_points.extend(l)
    vis_graph=[[[],[]] for x in range(len(sorted_points))]
    Q=[[] for x in range(len(sorted_points))]
    
    #We check wheter p is a convex_hull point point.
    for i in range(len(sorted_points)):
        if turn(p,sorted_points[i],
                  sorted_points[(i+1)%len(sorted_points)])>=0:
            new_sorted_points=[0 for x in range(len(sorted_points))]
            for j in range(len(sorted_points)):
                new_sorted_points[j]=sorted_points[(i+1+j)%len(sorted_points)]
            sorted_points=new_sorted_points
            for j in range(len(sorted_points)-1):
                proceed(j,j+1,False)
            return vis_graph
    
    for j in range(limit-1):   
        proceed(j,j+1,True)
        
    for j in range(limit-1,len(sorted_points)-1):
        proceed(j,j+1,False)
    
    vis_graph_temp=[vis_graph[x][1] for x in range(limit)]
   
    for i in range(limit):
        vis_graph[i][1]=[]
        Q[i]=[]
    
    proceed(len(sorted_points)-1,0,False)
        
    for j in range(limit-1):
        proceed(j,j+1,False)
    
    for i in range(limit):
        vis_graph[i][1].extend(vis_graph_temp[i])
        
    return vis_graph



def compute_visibility_graph(sorted_points):
    """Computes the visibility of every
        point as described in searching for empty convex polygons"""
    
    #G are the visibity graphs
    G=[]
    
    #assumes the points are already sorted
    #We sort the points by angle around each point
    #sorted_points=orderandsplit(points)
    
    def proceed(i,j):
        while Q[i] and turn(right_points[Q[i][0]],
                                  right_points[i],
                                  right_points[j])<=0:
            proceed(Q[i][0],j)
            Q[i].pop(0)

        Q[j].append(i)
        #We add ij to the graph
        vis_graph[j][0].append(i)
        vis_graph[i][1].append(j)
        
    for i in range(len(sorted_points)):
        right_points=sorted_points[i][1]
        vis_graph=[[[],[]] for x in range(len(right_points))]
        Q=[[] for x in range(len(right_points))]
        for j in range(len(right_points)-1):
            proceed(j,j+1)
        G.append(vis_graph)
        
    return G

#@accelerate(holesCpp.count_convex_rholes)
def count_convex_rholes_py(points,r,mono=False):
    """Counts the number of rholes in points; as described
        in search for empty convex polygons"""
     
    total=0  
    sorted_points=orderandsplit(points)
    G=compute_visibility_graph(sorted_points)
    L_array=[]
    #Start of MAX CHAIN
    for p in range(len(points)):
        right_points=sorted_points[p][1]
        L={}
        idx_list=range(len(right_points))
        idx_list.reverse()
        for q in idx_list:
            outgoing_vertices=G[p][q][1]
            incoming_vertices=G[p][q][0]
            max=0
            l=len(outgoing_vertices)-1
            idx_inc=range(len(incoming_vertices))
            idx_inc.reverse()
            for vi in idx_inc:
                L[(incoming_vertices[vi],q)]=max+1
                while l>=0 and turn(right_points[incoming_vertices[vi]],
                                         right_points[q],
                                         right_points[outgoing_vertices[l]])==-1:
                    if L[(q,outgoing_vertices[l])]>max:
                        max=L[(q,outgoing_vertices[l])]
                        L[(incoming_vertices[vi],q)]=max+1
                    l=l-1
        L_array.append(L)
    #print L_array
    
    #END OF MAX CHAIN
        
    #We will implement using pythons native list
    #In later revisions we should use proper lists
    #Actually for the time being since we are only counting
    #We may ommit the use of lists for creating the
    #convex chains.
    for p in range(len(points)):
        if mono:
            color=points[p][2]
        right_points=sorted_points[p][1]
        L=L_array[p]
        #We create the sets holding the convex chains
        C={}
        #If we follow the exposition of Searching for Empty Convex Polygons
        #here would the treat proceedure (the one after chains) start.
        for q in range(len(right_points)-1):
          
            outgoing_vertices=G[p][q][1]
            incoming_vertices=G[p][q][0]
            
            idx=range(len(outgoing_vertices))
            
            idx.sort(lambda x,y:L[(q,outgoing_vertices[y])]-L[q,outgoing_vertices[x]])
            outgoing_by_W=[outgoing_vertices[i] for i in idx]
                
            for vo in outgoing_vertices:
                if L[(q,vo)]>=r-2:
                    if mono:
                        if (right_points[q][2]==color and
                             right_points[vo][2]==color):
                            C[(q,vo)]=[1]
                        else:
                            C[(q,vo)]=[]
                    else:
                        C[(q,vo)]=[1]
                else:
                    C[(q,vo)]=[]
            
            m=0
            mprime=len(outgoing_vertices)
            for vi in incoming_vertices:
                    
                while (m <len(outgoing_vertices) and
                            turn(right_points[vi],
                                right_points[q],
                                right_points[outgoing_vertices[m]])==1):
                        
                    outgoing_by_W.remove(outgoing_vertices[m])
                    mprime=mprime-1
                    m=m+1
                    
                for ch in C[(vi,q)]:
                    t=0
                    l=ch #this line is l:=LENGTH(ch) in Searchingfor
                    #while (t<mprime and
                    #        edge_weights[outgoing_by_W[t]][q]>=r-2-l):
                    while t<mprime and L[(q,outgoing_by_W[t])]>=r-2-l:
                        chprime=ch+1
                        if l==r-3:
                            if mono:
                                if right_points[outgoing_by_W[t]][2]==color:
                                    total=total+1
                            else:
                                total=total+1 #we count rather than report
                        else:
                            if mono:
                                if right_points[outgoing_by_W[t]][2]==color:
                                    C[(q,outgoing_by_W[t])].append(chprime)
                            else:
                                C[(q,outgoing_by_W[t])].append(chprime)
                        t=t+1
                            
    return total
    
def count_convex_rholes(points, r, mono=False, speedup="try"):
    name = 'count_convex_rholes'
    pyf = count_convex_rholes_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.count_convex_rholes
        
    return cppWrapper(name, pyf, cppf, speedup, points=points, r=r, mono=mono)

#@accelerate(holesCpp.report_empty_triangles)
def report_empty_triangles_py(points):
    """Reports the number of empty triangles in the point set"""
    triangles=[]
    sorted_points=orderandsplit(points)
    G=compute_visibility_graph(sorted_points)
    for p in range(len(points)):
        right_points=sorted_points[p][1]
        for q in range(len(right_points)):
            #incoming_edges=G[p][q][0]
            for r in G[p][q][0]:
                triangles.append([points[p],right_points[r],right_points[q]])
    return triangles
    
def report_empty_triangles(points, speedup="try"):
    name = 'report_empty_triangles'
    pyf = report_empty_triangles_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.report_empty_triangles
        
    return cppWrapper(name, pyf, cppf, speedup, points=points)
    
def report_convex_rholes_py(points,r,mono=False):
    """Reports the number of rholes in points; as described
        in search for empty convex polygons"""
     
    report = deque()
    sorted_points=orderandsplit(points)
    G=compute_visibility_graph(sorted_points)
    L_array=[]
    #Start of MAX CHAIN
    for p in range(len(points)):
        right_points=sorted_points[p][1]
        L={}
        idx_list=range(len(right_points))
        idx_list.reverse()
        for q in idx_list:
            outgoing_vertices=G[p][q][1]
            incoming_vertices=G[p][q][0]
            max=0
            l=len(outgoing_vertices)-1
            idx_inc=range(len(incoming_vertices))
            idx_inc.reverse()
            for vi in idx_inc:
                L[(incoming_vertices[vi],q)]=max+1
                while l>=0 and turn(right_points[incoming_vertices[vi]],
                                         right_points[q],
                                         right_points[outgoing_vertices[l]])==-1:
                    if L[(q,outgoing_vertices[l])]>max:
                        max=L[(q,outgoing_vertices[l])]
                        L[(incoming_vertices[vi],q)]=max+1
                    l=l-1
        L_array.append(L)
    
    #END OF MAX CHAIN
    
    for p in range(len(points)):
        if mono:
            color = points[p][2]
        right_points = sorted_points[p][1]
        L = L_array[p]
        #We create the sets holding the convex chains
        C={}
        #If we follow the exposition of Searching for Empty Convex Polygons
        #here would be the treat proceedure (the one after chains) start.
        
        for q in range(len(right_points)-1):
          
            outgoing_vertices = G[p][q][1]
            incoming_vertices = G[p][q][0]
            
            idx = range(len(outgoing_vertices))
            
            idx.sort(lambda x,y:L[(q,outgoing_vertices[y])]-L[q,outgoing_vertices[x]])
            outgoing_by_W = [outgoing_vertices[i] for i in idx]
                
            for vo in outgoing_vertices:
                if L[(q,vo)]>=r-2:
                    if mono:
                        if (right_points[q][2]==color and
                             right_points[vo][2]==color):
                            tmplist = [right_points[vo], right_points[q], points[p]]
                        else:
                            C[(q,vo)]=[]
                    else:
                        tmplist = [right_points[vo], right_points[q], points[p]]
                        C[(q,vo)]=[tmplist]
                        
                else:
                    C[(q,vo)]=[]
            
            m = 0
            mprime = len(outgoing_vertices)
            for vi in incoming_vertices:
                    
                while (m <len(outgoing_vertices) and
                            turn(right_points[vi],
                                right_points[q],
                                right_points[outgoing_vertices[m]])==1):
                        
                    outgoing_by_W.remove(outgoing_vertices[m])
                    mprime=mprime-1
                    m=m+1
                    
                for ch in C[(vi,q)]:
                    t=0
                    #l=ch #this line is l:=LENGTH(ch) in Searchingfor
                    l=len(ch)-2                                                 #ch.length-2
                    #print l
                    #while (t<mprime and
                    #        edge_weights[outgoing_by_W[t]][q]>=r-2-l):
                    while t<mprime and L[(q,outgoing_by_W[t])]>=r-2-l:
                        #this line is ch':=EXTEND(ch,o_t')
                        #chprime=ch+1
                        chprime = [right_points[outgoing_by_W[t]]]
                        chprime.extend(ch)
                        #We report
                        if l==r-3:
                            if mono:
                                if right_points[outgoing_by_W[t]][2]==color:
                                    report.appendleft(list(chprime))
                            else:
                                report.appendleft(list(chprime))
                        else:
                            if mono:
                                if right_points[outgoing_by_W[t]][2]==color:
                                    C[(q,outgoing_by_W[t])].append(chprime)
                            else:
                                C[(q,outgoing_by_W[t])].append(chprime)
                        t=t+1
    return list(report)
    
def report_convex_rholes(points, r, mono=False, speedup="try"):
    name = 'report_convex_rholes'
    pyf = report_convex_rholes_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.report_convex_rholes
        
    return cppWrapper(name, pyf, cppf, speedup, points=points, r=r, mono=mono)
                
                
def count_rholes_maker(r,mono=False):      
    def f(pts):
        return count_convex_rholes(pts,r,mono=mono)        
    return f

def report_rholes_maker(r,mono=False):      
    def f(pts):
        return report_convex_rholes(pts,r,mono=mono)        
    return f
    
def countEmptyMonoTriangsVertex(rpoints,color):
    
    triangs=0
    q=[]
    
    #sacada verbatim(casi) de searching for empty convex polygons
    #Ojo agrego aristas cuando estan alineados los puntos
    def proceed(i,j):
        tmp=0
        while q[i] and turn(rpoints[q[i][0]],rpoints[i],rpoints[j])<=0:
            tmp=tmp+proceed(q[i][0],j)
            q[i].pop(0)
        
        q[j].append(i)
        if color == rpoints[i][2] and color == rpoints[j][2]:
            return tmp+1
        return tmp

    for i in range(0,len(rpoints)):
        q.append([])
    
    for i in range(0,len(rpoints)-1):
        triangs=triangs+proceed(i,i+1)
        
    return triangs
        
def countEmptyMonoTriangs(points):
    
    ordpoints=orderandsplit(points)
    triangs=0
    
    for i in range(0,len(points)):
        triangs=triangs+countEmptyMonoTriangsVertex(ordpoints[i][1],points[i][2])
    
    return triangs

#funcion de tiempo O(n^3) para verificiar si un conjunto
#de puntos esta o no en posicion convexa regresa 0 si lo esta
#y en caso contrario el numero de tercias collineales
#imprime tambien las ternas colineales de momento
#def slow_generalposition(pts):
#    col=0
#    for i in range(len(pts)):
#        for j in range(i+1,len(pts)):
#            for k in range(j+1,len(pts)):
#                if turn(pts[i],pts[j],pts[k])==0:
#                    print pts[i],pts[j],pts[k]
#                    col=col+1
#    return col
#
#def general_position(points):
#    """Checks in time O(n^2logn) wheter
#        the point set is in general position"""
#    ord_points=orderandsplit(points)
#    col=0
#    for p in ord_points:
#        point=p[0] #point p
#        rpoints=p[1] #points to the right of p
#        for i in range(len(rpoints)-1):
#            col=col+slow_generalposition([point, rpoints[i], rpoints[i+1]])
#    return col
    

#Deberia mover esta funciona otro modulo
#la he movido a pointsets la dejo porque
#no recuerdo si otro modulo ya la usa.
#def HortonSet(k):
#    """construct the Horton set of 2^k vertices
#        we follow Pavel Valtr's construction (and thus Hortons)"""
#    
#    if k<=0:
#        return [[0,0]]
#    
#    if k==1:
#        return [[0,0],[1,0]]
#    
#    n=2**(k-1)
#    dn=(3**n)-1
#    previoushorton=HortonSet(k-1)
#    newhorton=[]
#    
#    for p in previoushorton:
#        newhorton.append([2*p[0],p[1]])
#        newhorton.append([2*p[0]+1,p[1]+dn])
#
#    return newhorton
                              

def slow_count_monoquad(points):
    """Counts in time n^5 the number of empty monochromatic cuadrilaterals."""
    quads=0
    for i in range(len(points)):
        color=points[i][2]
        for j in range(i+1,len(points)):
            if color==points[j][2]:
                for k in range(j+1,len(points)):
                    if color==points[k][2]:
                        for l in range(k+1,len(points)):
                            if color==points[l][2]:
                                empty=False
                                if not pointsInTriang(points,[points[i],points[j],points[k]]):
                                    if not pointsInTriang(points,[points[i],points[j],points[l]]):
                                        if not pointsInTriang(points,[points[i],points[k],points[l]]):
                                            if not pointsInTriang(points,[points[j],points[k],points[l]]):
                                                empty=True
                                convex=True
                                if pointInTriang(points[i],[points[j],points[k],points[l]]):
                                    convex=False
                                if pointInTriang(points[j],[points[i],points[k],points[l]]):
                                    convex=False
                                if pointInTriang(points[k],[points[i],points[j],points[l]]):
                                    convex=False
                                if pointInTriang(points[l],[points[i],points[j],points[k]]):
                                    convex=False
                            
                                if convex and empty:
                                    quads=quads+1
                                    print points[i],points[j],points[k],points[l]
    return quads
    
##TALLER DE OAXACA CAMBIAR A OTRO MODULO LO RESCATABLE
    
    
def count_deg_triang_vertex(rpoints,degs,k,points):
    
    #print degs
    triangs=0
    q=[]
    #sacada verbatim(casi) de searching for empty convex polygons
    #Ojo agrego aristas cuando estan alineados los puntos
    def proceed(i,j,degs,k):
        tmp=0
        while q[i] and turn(rpoints[q[i][0]],rpoints[i],rpoints[j])<=0:
            tmp=tmp+proceed(q[i][0],j,degs,k)
            q[i].pop(0)
        l=points.index(rpoints[i])
        m=points.index(rpoints[j])
        q[j].append(i)
        degs[l][m]=degs[l][m]+1
        degs[m][l]=degs[m][l]+1
        degs[l][k]=degs[l][k]+1
        degs[k][l]=degs[k][l]+1
        degs[m][k]=degs[m][k]+1
        degs[k][m]=degs[k][m]+1
        return tmp+1

    for i in range(0,len(rpoints)):
        q.append([])
    
    for i in range(0,len(rpoints)-1):
        triangs=triangs+proceed(i,i+1,degs,k)
        
    return triangs
        
def count_deg_triang(points):
    
    ordpoints=orderandsplit(points)
    triangs=0
    degs=[]
    max=0
    for i in range(len(points)):
        s=[0 for j in range(len(points))]
        #print s
        degs.append(s)
    
    for i in range(0,len(points)):
        triangs=triangs+count_deg_triang_vertex(ordpoints[i][1],degs,i,points)
    for i in range(0,len(points)):
        for j in range(0,len(points)):
            if degs[i][j]> max:
                max=degs[i][j]
    
    return max
  
def count_deg_triang_degs(points):
    
    ordpoints=orderandsplit(points)
    triangs=0
    degs=[]
    max=0
    I=0
    J=0
    for i in range(len(points)):
        s=[0 for j in range(len(points))]
        #print s
        degs.append(s)
    
    for i in range(0,len(points)):
        triangs=triangs+count_deg_triang_vertex(ordpoints[i][1],degs,i,points)
    for i in range(0,len(points)):
        for j in range(0,len(points)):
            if degs[i][j]> max:
                max=degs[i][j]
                I=i
                J=j
    
    return (I,J)
    

def count_convex_rholes_maker(r, colored=False):
    def f(pts):
        return count_convex_rholes(pts,r,mono=colored)
    return f

def count_convex_rholes_p_maker(r, mono=False):
    def f(p,pts):
        return count_convex_rholes_p(p,pts,r,mono=mono)
    return f

def count_convex_rholes_difference_maker(r,colored=False):
    def f(p,q,pts):
        return count_convex_rholes_difference(p,q,pts,r,colored=False)
    return f

def count_convex_rholes_difference(p,q,pts,r,colored=False):
    """Computes the change in the number of rholes when
       moving p to q in pts."""
    
    n=len(pts)
    if colored:
        points_temp=[[0,0,0]for i in range(n-1)]
    else:
        points_temp=[[0,0]for i in range(n-1)]
        
    k=0
    for j in range(n):
            if pts[j]!=p:
                points_temp[k]=pts[j][:]
                k+=1
    if r==3:
        (Ap,Bp)=count_empty_triangles_p(p,points_temp)
        (Aq,Bq)=count_empty_triangles_p(q,points_temp)  
    else:
        (Ap, Bp)=count_convex_rholes_p(p, points_temp, r, mono=colored)
        (Aq, Bq)=count_convex_rholes_p(q, points_temp, r, mono=colored)
    return -Ap+Aq+Bp-Bq

############################################################################
#@accelerate_p(holesCpp.count_convex_rholes_p)
def count_convex_rholes_p_py(p, points, r, mono = False):
    '''
    Returns (A,B). Where A is the number of empty r-holes that contain p as
    a vertex and B the number of r-holes that contain only contain p in 
    their interior.
    '''
    rA, rB = r, r+1
    resA, resB = 0, 0
    rp, lp =sort_around_point(p, points, False)
    sorted_points=sort_around_point(p, points, True)

    il=[]
    ir=[]

    for punto in rp:
        ir.append(sorted_points.index(punto))

    for punto in lp:
        il.append(sorted_points.index(punto))
    
    indices=[]    
    
    q = p[:]
    qp = p[:]
    
    for i in reversed(ir):
        indices.append(i)
        if sorted_points[i][1] > q[1]:
            q[1]=sorted_points[i][1]
        if sorted_points[i][1] < qp[1]:
            qp[1]=sorted_points[i][1]
            
    for i in reversed(il):
        indices.append(i)
        if sorted_points[i][1] > q[1]:
            q[1]=sorted_points[i][1]
        if sorted_points[i][1] < qp[1]:
            qp[1]=sorted_points[i][1]
                    
    q[1]+=1
    qp[1]-=1
    
    #MAX_CHAIN_1
    VG=visibility_graph_around_p(p, points)    
    #L contiene los pesos de cada arista
    L={}
        
    for v in indices:
        inc=VG[v][0]
        out=VG[v][1]
        
        pt=sorted_points[v]
        l=len(out)-1
        m=0
        for i in reversed(inc):
            L[i, v]=m+1
            #Checar si es arista prohibida
            if(turn(p, q, sorted_points[i]) != turn(p, q, sorted_points[v])) and \
            (turn(sorted_points[v], sorted_points[i], p) != turn(sorted_points[v], sorted_points[i], q)) and turn(p, q, sorted_points[v])!=0:
                L[i, v]=0 
            
            while l>=0 and turn(sorted_points[i], pt, sorted_points[out[l]])<0:
                if ((v, out[l]) in L) and L[v, out[l]]>m and L[i, v]>0:
                    m=L[v, out[l]]
                    L[i, v]=m+1
                l-=1
    #END MAX_CHAIN_1
    
    #REPORTING_1
    ChainsA={}
    ChainsB={}    
    
    for x in range(len(VG)):
        for v in VG[x][0]:
            ChainsA[v, x]=[]
            ChainsB[v, x]=[]
            
    for v in reversed(indices):
        #Indice del punto que se esta tratando
        pt=sorted_points[v]
        Si, So, Sop = [], [], []

        def comp(v1, v2):
            if L[v, v1] > L[v, v2]:
                return -1
            elif L[v, v1] < L[v, v2]:
                return 1
            return 0

        Si.extend(VG[v][0])
        So.extend(VG[v][1])
        Sop.extend(VG[v][1])
        Sop.sort(comp)
        
        for out in So:
            if L[v, out]>=rA-2:
                if mono:                
                    if pt[2] == p[2] and sorted_points[out][2]==p[2]:
                        ChainsA[v, out].append([v, out])
                else:
                    ChainsA[v, out].append([v, out])
            if L[v, out]>=rB-2:
                if mono:
                    if pt[2]==sorted_points[out][2]:
                        ChainsB[v, out].append([v, out])
                else:
                    ChainsB[v, out].append([v, out])
        
        #Para las cadenas de longitud r-2 con p como vertice:
                
        m=0
        mp=len(So)-1
        
        for inc in Si:
            while m<len(So) and turn(sorted_points[inc], sorted_points[v], sorted_points[So[m]])>0:
                ind=Sop.index(So[m])
                Sop.pop(ind)
                mp-=1
                m+=1
            for ch in ChainsA[inc, v]:
                t=0
                l=len(ch)-1
                while(t<=mp and L[v, Sop[t]]>=rA-2-l):
                    chp=[]
                    chp.extend(ch)
                    chp.append(Sop[t])
                    if l==rA-3:
                        #CHECAR SI TODAS LAS CONDICIONES SON NECESARIAS
                        if turn(sorted_points[chp[-1]], p, sorted_points[chp[0]])<0 and \
                        (turn(sorted_points[chp[-2]], sorted_points[chp[-1]], p)<0 and \
                        turn(p, sorted_points[chp[0]], sorted_points[chp[1]])<0 ):
                            if mono:
                                if sorted_points[Sop[t]][2]==p[2]:
                                    #Se checa si forma un r-hoyo convexo con p
                                    resA+=1
                            else:
                                #Se checa si forma un r-hoyo convexo con p
                                resA+=1
                    else:
                        if mono:
                            if sorted_points[Sop[t]][2]==p[2]:
                                ChainsA[v, Sop[t]].append(chp)
                        else:
                            ChainsA[v, Sop[t]].append(chp)
                    t+=1
                    
        #Para las cadenas de longitud r-1 con p en su interior
        
        m=0
        mp=len(So)-1
        
        Sop=[]
        Sop.extend(So)
        Sop.sort(comp)
        
        for inc in Si:
            while m<len(So) and turn(sorted_points[inc], sorted_points[v], sorted_points[So[m]])>0:
                ind=Sop.index(So[m])
                Sop.pop(ind)
                mp-=1
                m+=1
            for ch in ChainsB[inc, v]:
                t=0
                l=len(ch)-1
                while(t<=mp and L[v, Sop[t]]>=rB-2-l):
                    chp=[]
                    chp.extend(ch)
                    chp.append(Sop[t])
                    if l==rB-3:
                        #CHECAR SI TODAS LAS CONDICIONES SON NECESARIAS
                        if turn(sorted_points[chp[-1]], sorted_points[chp[0]], p)<0 and \
                        (turn(sorted_points[chp[-2]], sorted_points[chp[-1]], sorted_points[chp[0]])<0 and \
                        turn(sorted_points[chp[-1]], sorted_points[chp[0]], sorted_points[chp[1]])<0) and \
                        L.has_key((chp[-1], chp[0])):
                            if mono:
                                if sorted_points[ch[0]][2]==sorted_points[Sop[t]][2]:
                                    #Se checa si forma un r-hoyo convexo con p en su interior
                                    #resB.append(chp)
                                    resB+=1
                            else:
                                #Se checa si forma un r-hoyo convexo con p en su interior
                                #resB.append(chp)
                                resB+=1
                    else:
                        if mono:
                            if sorted_points[ch[0]][2]==sorted_points[Sop[t]][2]:
                                ChainsB[v, Sop[t]].append(chp)
                        else:
                            ChainsB[v, Sop[t]].append(chp)
                    t+=1
                    
    #END_REPORTING_1
    
    #Se vuelve a tratar a los puntos para encontrar cadenas 
    #omitidas al tomas como referencia a q.
    
    def cruza_q(ch):
        for i in range(len(ch)-1):
            v1 = sorted_points[ch[i]]
            v2 = sorted_points[ch[i+1]]
            if (turn(v1, v2, q) != turn(v1, v2, p)) and (turn(p, q, v1) != turn(p, q, v2)) and turn(v2, p, q) != 0:
                return True
        return False
    
    indices=[]
    
    for i in reversed(il):
        indices.append(i)
        
    for i in reversed(ir):
        indices.append(i)
    
    #MAX_CHAIN_2
    L={}
        
    for v in indices:
        inc=VG[v][0]
        out=VG[v][1]
        
        pt=sorted_points[v]
        l=len(out)-1
        m=0
        for i in reversed(inc):
            L[i, v]=m+1
            #Checar si es arista prohibida
            if(turn(p, qp, sorted_points[i]) != turn(p, qp, sorted_points[v])) and \
            (turn(sorted_points[v], sorted_points[i], p) != turn(sorted_points[v], sorted_points[i], qp)):
                L[i, v]=0 
            
            while l>=0 and turn(sorted_points[i], pt, sorted_points[out[l]])<0:
                if ((v, out[l]) in L) and L[v, out[l]]>m and L[i, v]>0:
                    m=L[v, out[l]]
                    L[i, v]=m+1
                l-=1
    #END MAX_CHAIN_2
    
    #REPORTING_2
    ChainsA={}
    
    for x in range(len(VG)):
        for v in VG[x][0]:
            ChainsA[v, x]=[]
            
    del comp
            
    for v in reversed(indices):
        #Indice del punto que se esta tratando
        pt=sorted_points[v]
        Si, So, Sop = [], [], []

        def comp(v1, v2):
            if L[v, v1] > L[v, v2]:
                return -1
            elif L[v, v1] < L[v, v2]:
                return 1
            return 0

        Si.extend(VG[v][0])
        So.extend(VG[v][1])
        Sop.extend(VG[v][1])
        Sop.sort(comp)
        
        for out in So:
            ChainsA[v, out]=[]
            if L[v, out]>=rA-2:
                if mono:
                    if pt[2]==p[2] and sorted_points[out][2]==p[2]:
                        ChainsA[v, out].append([v, out])
                else:
                    ChainsA[v, out].append([v, out])
        
        #Para las cadenas de longitud r-2 con p como vertice:
                
        m=0
        mp=len(So)-1
        
        for inc in Si:
            while m<len(So) and turn(sorted_points[inc], sorted_points[v], sorted_points[So[m]])>0:
                ind=Sop.index(So[m])
                Sop.pop(ind)
                mp-=1
                m+=1
            for ch in ChainsA[inc, v]:
                t=0
                l=len(ch)-1
                while(t<=mp and L[v, Sop[t]]>=rA-2-l):
                    chp=[]
                    chp.extend(ch)
                    chp.append(Sop[t])
                    if l==rA-3: 
                        #CHECAR LAS ULTIMAS 2 CONDICIONES SON NECESARIAS
                        if turn(sorted_points[chp[-1]], p, sorted_points[chp[0]])<0 and \
                        cruza_q(chp) and \
                        (turn(sorted_points[chp[-2]], sorted_points[chp[-1]], p)<0 and \
                        turn(p, sorted_points[chp[0]], sorted_points[chp[1]])<0) :
                            if mono:
                                if p[2]==sorted_points[Sop[t]][2]:
                                    #Se checa si forma un r-hoyo convexo con p y no ha sido
                                    #encontrada
                                    resA+=1
                            else:
                                resA+=1
                    else:
                        if mono:
                            if p[2]==sorted_points[Sop[t]][2]:
                                ChainsA[v, Sop[t]].append(chp)
                        else:
                            ChainsA[v, Sop[t]].append(chp)
                    t+=1
    return resA, resB
    
def count_convex_rholes_p(p, points, r, mono=False, speedup="try"):
    name = 'count_convex_rholes_p'
    pyf = count_convex_rholes_p_py    
    if utilities.__config['PURE_PYTHON']:
        cppf = None
    else:
        cppf = holesCpp.count_convex_rholes_p
        
    return cppWrapper(name, pyf, cppf, speedup, p=p, points=points, r=r, mono=mono)
