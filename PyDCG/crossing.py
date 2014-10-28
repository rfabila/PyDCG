"""Module used to count the number of crossings in the complete
geometric graph"""

from geometricbasics import *
import os

__config_file=open(os.path.join(os.path.dirname(__file__), "config/config.cfg"), "r")
__config=pickle.load(__config_file)
__config_file.close()

if not __config['PURE_PYTHON']:
    import crossingCpp

def accelerate(cfunc):
    def bind_cfunc(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            speedup = False
            if 'speedup' in kwargs:
                speedup = kwargs['speedup']
                del kwargs['speedup']
                
            if speedup == 'try':
                speedup = safe_point_set(kwargs.get('points', args[0]))
                
            if not speedup:
#                print "Funcion de Python"
                return func(*args, **kwargs)
            else:
#                print "Funcion de C++"
                return cfunc(*args, **kwargs)
        return wrapper
    return bind_cfunc

def accelerate_list(cfunc):
    def bind_cfunc(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            speedup = False
            if 'speedup' in kwargs:
                speedup = kwargs['speedup']
                del kwargs['speedup']
                
            if speedup == 'try':
                speedup = (safe_point_set(kwargs.get('pts', args[2])) and
                           safe_point_set(kwargs.get('candidate_list',args[1])))
                
            if not speedup:
                #print "Python"
                return func(*args, **kwargs)
            else:
                #print "C++"
                return cfunc(*args, **kwargs)
        return wrapper
    return bind_cfunc

def count_k_edges(pts,k):
    """Returns the number of k edges in pts"""
    n=len(pts)
    tmp_pts=[[0,0] for i in range(n-1)]
    k_edges=0
    for i in range(n):
        #pivote
        p=pts[i]
        #We copy the points distinct from p to tmp_pts
        for j in range(0,i):
            tmp_pts[j]=pts[j][:]
        for j in range(i+1,n):
            tmp_pts[j-1]=pts[j][:]
        tmp_pts=sort_around_point(p,tmp_pts)
        j=0
        for i in range(len(tmp_pts)):
            while (turn(p,tmp_pts[i],tmp_pts[(j+1)%(n-1)])<=0 and
                    (j+1)%(n-1)!=i):
                j=j+1
                    
            ni=(j-i)%(n-1)
            if ni==k:
                k_edges+=1
        
    return k_edges

def k_edges_vector(pts):
    """Returns the number of k edges in pts"""
    n=len(pts)
    V=[0 for i in range(n-1)]
    tmp_pts=[[0,0] for i in range(n-1)]
    k_edges=0
    for i in range(n):
        #pivote
        p=pts[i]
        #We copy the points distinct from p to tmp_pts
        for j in range(0,i):
            tmp_pts[j]=pts[j][:]
        for j in range(i+1,n):
            tmp_pts[j-1]=pts[j][:]
        tmp_pts=sort_around_point(p,tmp_pts)
        j=0
        for i in range(len(tmp_pts)):
            while (turn(p,tmp_pts[i],tmp_pts[(j+1)%(n-1)])<=0 and
                    (j+1)%(n-1)!=i):
                j=j+1
                    
            ni=(j-i)%(n-1)
            V[ni]+=1
        
    return V

def count_halving_lines(pts):
    """Counts the number of $\lfoor n/2 \rfloor$ k-edges"""
    return count_k_edges(pts,(n-2)/2)

def count_crossings(pts):
    """Returns the he number of crossings in the complete
    geometric graph with vertex set pts. Runs in O(n^2logn) time"""
    n=len(pts)
    tmp_pts=[[0,0] for i in range(n-1)]
    cr=0
    for i in range(n):
        #pivote
        p=pts[i]
        #We copy the points distinct from p to tmp_pts
        for j in range(0,i):
            tmp_pts[j]=pts[j][:]
        for j in range(i+1,n):
            tmp_pts[j-1]=pts[j][:]
        tmp_pts=sort_around_point(p,tmp_pts)
        j=0
        for i in range(len(tmp_pts)):
            while (turn(p,tmp_pts[i],tmp_pts[(j+1)%(n-1)])<=0 and
                    (j+1)%(n-1)!=i):
                j=j+1
                    
            ni=(j-i)%(n-1)
            cr=cr+ni*(ni-1)/2

    total=n*(n-1)*(n-2)*(n-3)/2    
        
    return cr-(total/4)

#The C version is not working properly, I am disabling it for the time being.
#if not __config['PURE_PYTHON']:
 #   count_crossings = accelerate(crossingCpp.crossing)(count_crossings)

def count_crossings_candidate_list(point_index,candidate_list,pts):
    """Let k=len(candidate_list), n=len(pts). Returns the
       best candidate for pts[point_index] in time
       O(n^2logn)+O(k*nlogn)."""
       
    def searchpoint(p,pts):
        for i in range(len(pts)):
            if pts[i][0]==p[0] and pts[i][1]==p[1]:
                return i
    def gen_antipodal_list(q,pts_q):
        intervals_q=[]
        for x in pts_q:
            intervals_q.append([-x[0]+2*q[0],-x[1]+2*q[1], x[2], True, False ])
            intervals_q.append([x[0],x[1], x[2], True, True])
        intervals_q=sort_around_point(q,intervals_q)
        return intervals_q        
    def remove_j_sortandmark(i,pts,sortandmark=True):
        #Sort a copy the points distinct from p to tmp_pts and appened a position mark
        tmp_pts=[0 for x in range(len(pts)-1)]
        for j in range(0,i):
            tmp_pts[j]=pts[j][:]
        for j in range(i+1,len(pts)):
            tmp_pts[j-1]=pts[j][:]
        if sortandmark:    
            q=pts[i]
            tmp_pts=sort_around_point(q,tmp_pts)            
            for j in range(0,len(pts)-1):
                tmp_pts[j].append(j)
        return tmp_pts 
    def nis_for_p(p,tmp_pts):
        #save ni in num_pts[i] for each point in tmp_pts
        j=0
        num_pts=[0 for k in tmp_pts]
        for k in range(len(tmp_pts)):
            while (turn(p,tmp_pts[k],tmp_pts[(j+1)%(n-1)])<=0 and
                    (j+1)%(n-1)!=k):
                j=j+1
                    
            num_pts[k]=(j-k)%(n-1)
        return num_pts    
    def join_pts_antipodal_candidatelist(point_index,pts,central_point,tmp_pts,candidate_list):
        #We copy a distinct point from pts[point_index] with your antipodal point,
        #join candidate_list and pts[point_index]
        p=pts[point_index]
        p_index=searchpoint(p,tmp_pts)
        united_pts=remove_j_sortandmark(p_index,tmp_pts)
        united_pts=gen_antipodal_list(central_point,united_pts)
        united_pts.extend(candidate_list)
        united_pts.append(pts[point_index])
        united_pts=sort_around_point(central_point,united_pts)
        return united_pts    
    def change_of_cr_for_list(united_pts,candidate_list,position_p,nis):
        #We save in cr_list the change of patrons type A       
        sum_ni=0
        change_cr_list=[0 for x in candidate_list]
        aux_nis=nis[:]
        count_ni=0
        count_change_cr_for_q=[0 for x in candidate_list]        
        
        for k in range(1,len(united_pts)):
            pos=(position_p+k)%len(united_pts)
            if united_pts[pos][3]:
                if united_pts[pos][4]:
                    sum_ni=sum_ni+aux_nis[united_pts[pos][2]]
                    aux_nis[united_pts[pos][2]]=aux_nis[united_pts[pos][2]]+1
                    count_ni=count_ni-1

                else:
                    sum_ni=sum_ni-aux_nis[united_pts[pos][2]]+1
                    aux_nis[united_pts[pos][2]]=aux_nis[united_pts[pos][2]]-1
                    count_ni=count_ni+1
                    
            else:
                change_cr_list[united_pts[pos][2]]=change_cr_list[united_pts[pos][2]]+sum_ni
                count_change_cr_for_q[united_pts[pos][2]]=count_ni
        return [change_cr_list, count_change_cr_for_q]
    def cr_in_point_of_candidatelist(candidate_list,tmp_pts):
        cr_q_in_candidatelist=[0 for x in candidate_list]
        for q in candidate_list:
            j=0
            for k in range(len(tmp_pts)):
                while (turn(q,tmp_pts[k],tmp_pts[(j+1)%(n-1)])<=0 and
                        (j+1)%(n-1)!=k):
                    j=j+1
                        
            cr_q_in_candidatelist[q[2]]=((j-k)%(n-1))*((j-k)%(n-1)-1)/2
        return cr_q_in_candidatelist
    def index_pts_without_pointindex(point_index,pts):
        i=0
        indexes=[]
        while i<len(pts):
            if i!=point_index:
                indexes.append(i)
            i=i+1
        return indexes    
   
    candidate_list=[x[:] for x in candidate_list]
    pts=[x[:] for x in pts]
    n=len(pts)
    for i in range(len(candidate_list)):
        candidate_list[i].append(i)
        candidate_list[i].append(False)
    cr2=0
    cr3=0
    cr_list2=[0 for x in candidate_list]
    cr_list3=[0 for x in candidate_list]
    
    for i in index_pts_without_pointindex(point_index,pts):
        tmp_pts=remove_j_sortandmark(i,pts,True)
        nis=nis_for_p(pts[i],tmp_pts)
        pos_p_in_tps=searchpoint(pts[point_index],tmp_pts)
        
        # Suma 2
        for k in index_pts_without_pointindex(pos_p_in_tps,tmp_pts):
            cr2=cr2+nis[k]*(nis[k]-1)/2
        #    
        united_pts=join_pts_antipodal_candidatelist(point_index,pts,pts[i],tmp_pts,candidate_list)
        position_p=searchpoint(pts[point_index],united_pts)   
        [aux_cr_list2,count_change_of_list]=change_of_cr_for_list(united_pts,candidate_list,position_p,nis)
        for i in range(len(cr_list2)):
            cr_list2[i]=cr_list2[i]+aux_cr_list2[i]
        #print(cr_list2)    
        #-----------------------
        
        # Suma 3
        cr3=cr3+nis[pos_p_in_tps]*(nis[pos_p_in_tps]-1)/2
        #
        for j in range(len(candidate_list)): 
            cr_list3[j]=cr_list3[j]+(count_change_of_list[j]+nis[pos_p_in_tps])*(count_change_of_list[j]+nis[pos_p_in_tps]-1)/2
        #----------------------

    total=n*(n-1)*(n-2)*(n-3)/8    
    cr_list=[0 for x in candidate_list]
    for i in range(len(candidate_list)):
        cr_list2[i]=cr_list2[i]+cr2
        cr_list[i]=cr_list2[i]+2*cr_list3[i]-total

    return cr_list

if not __config['PURE_PYTHON']:
    count_crossings_candidate_list = accelerate_list(crossingCpp.count_crossings_candidate_list)(count_crossings_candidate_list)