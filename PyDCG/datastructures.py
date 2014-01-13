# -*- coding: utf-8 -*-
#!/usr/bin/env python
import random
import line
import fractions
from geometricbasics import turn

objs=[]
"""Module implementing various data structures"""

def count_list_elements(list):
    """O(n) function to count the
       number of elements of a list"""
    total=0
    while not list.empty:
        total=total+1
        list=list.cdr
    return total
           
#rewrite it as a class function as so
#so that it works directly with print
def print_list_elements(list):
    """O(n) function to print the elements of a list"""
    while not list.empty:
        print list.car
        list=list.cdr

class List:
    """linked list. Be careful when using the lenght
       field it does not get updated automatically.
       Its current use is for a queue for example."""
    
    #A la scheme
    def __init__(self,car=None):
        self.car=car
        if self.car==None:
            self.empty=True
            self.length=0
            self.cdr=None
        else:
            self.empty=False
            self.cdr=List()
            self.length=1
    
    def to_front(self,elem):
        tmplist=List(car=self.car)
        tmplist.cdr=self.cdr
        tmplist.length=self.length
        
        self.car=elem
        self.cdr=tmplist
        self.length=tmplist.length+1
        self.empty=False
    
    

#I feel the class slow. It is not clear
#whether the complexity is wrong or is just
#the overhead of constructing the Node objects.
#Or I am just a bad programmer.
#This could be a source for big improvement in the future.
#Seems to be working ok though.
class Treap(object):
    """An implementation of a treap. Note that
       lower priority elements are at the top.
       Loosely based on the description in "Randomized Algorithms"
       by Motwani and Raghavan. All mistakes are mine"""
    
    def __init__(self,compare=lambda x,y:x-y,max_size=1000):
        
        self.compare=compare
        self.root=None
        self.empty=True
        
        #self.max_size=max_size
        #self.free_nodes=[self.Node() for i in range(self.max_size)]
        #self.start_node=0
        #self.end_node=max_size-1
        #self.nodes=self.free_nodes[:]
    
    #def clear(self):
     #   self.root=None
     #   self.empty=True
     #   self.free_nodes=self.nodes[:]
    
    def find(self,key):
        if self.empty:
            return None
        else:
            node=self.root
            while(node!=None):
                #if its smaller
                if self.compare(key,node.key) < 0:
                    node=node.left
                elif self.compare(key,node.key) > 0:
                    node=node.right
                else:
                    return node
            return node
    
    def delete(self,key):
        node=self.find(key)
        self.delete_node(node)
        return node
               
    def delete_node(self,node):
        if node==None:
            return None
        while node.left!=None or node.right!=None:
            if node.left==None or node.right==None:
                if node.left==None:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)   
            else:
                if self.compare_priorities(node.left,node.right) > 0:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)
                
        if  node.parent!=None:        
            if node.parent.left==node:
                node.parent.left=None
            else:
               node.parent.right=None
        else:
            self.root=None
            self.empty=True
        
        
        return node            
    
    def insert(self,key,obj=None):
        node=self.Node(key=key,obj=obj)
        self.insert_node(node)
    
    def insert_node(self,node):    
        if self.empty:
            self.root=node
            self.empty=False
        else:
            leaf=self.root
            parent=self.root
            while(leaf!=None):
                #if its smaller
                parent=leaf
                if self.compare(node.key,leaf.key) < 0:
                   leaf=leaf.left
                else:
                    leaf=leaf.right
            node.parent=parent
            if self.compare(node.key,parent.key) < 0:
                parent.left=node
            else:
                parent.right=node
            self.restore_heap(node)

    
    def restore_heap(self,node):
        """Restores the heap property by
           rotating the node upwards if necessary"""
        if node.parent==None:
            return False
        
        while self.compare_priorities(node.parent,node)>0:
            if node==node.parent.left:
                self.rotate_right(node.parent)
            else:
                self.rotate_left(node.parent)
            if node.parent==None:
                break
    def restore_heap_downwards(self,node):
        """Restores the heap property by rotating
           the node downwards if necessary."""
        while(self.compare_priorities(node,node.left))>=1 or (self.compare_priorities(node,node.right)) >=1:
            if self.compare_priorities(node.left,node.right)>=1 or node.left==None:
                #right must go above
                self.rotate_left(node)
            else:
                #left must go above
                self.rotate_right(node)
            
        
    def show(self):
        print self.root.__str__()

    def compare_priorities(self,x,y):
        if x==y or x==None or y==None:
            return 0
        prx=x.priority
        pry=y.priority
        while prx.car==pry.car:
            if prx.cdr.empty:
                prx.cdr=List(car=random.random())
            prx=prx.cdr
            if pry.cdr.empty:
                pry.cdr=List(car=random.random())
            pry=pry.cdr
                
        if prx.car < pry.car:
            return -1
        else:
            return 1
    
    def min(self):
        return self.min_tree(self.root)
        
    def min_tree(self,node):
        """Returns the minimum value
           at the tree hanging from node
           as a root"""
        if node==None:
            return None
        return_node=node
        while return_node.left!=None:
            return_node=return_node.left
        return return_node
    
    def max(self):
        return self.max_tree(self.root)
        
    def max_tree(self,node):
        """Returns the maximum value
           at the tree hanging from node
           as a root"""
        if node==None:
            return None
        return_node=node
        while return_node.right!=None:
            return_node=return_node.right
        return return_node
    
    def rotate_left(self,node):
        if node.right!=None:
            grandpa=node.parent
            nnode=node.right
            nnode.parent=grandpa
            node.parent=nnode
            
            if grandpa!=None:
                if grandpa.left==node:
                    grandpa.left=nnode
                else:
                    grandpa.right=nnode
            else:
                self.root=nnode
                
            node.right=nnode.left
            nnode.left=node
            
            if node.right!=None:
              node.right.parent=node
            
    
    def rotate_right(self,node):
        if node.left!=None:
            grandpa=node.parent
            nnode=node.left
            nnode.parent=grandpa
            node.parent=nnode
            
            if grandpa!=None:
                if grandpa.left==node:
                    grandpa.left=nnode
                else:
                    grandpa.right=nnode
            else:
                self.root=nnode
            
            node.left=nnode.right
            nnode.right=node
            
            if node.left!=None:
              node.left.parent=node
                        
                                        
    
    def check_priority(self,node):
        if node==None:
            return True
        if (not self.check_priority(node.left)) or (not self.check_priority(node.right)):
            return False
        if node.left!=None or node.right!=None:
            if node.left!=None:
                if self.compare_priorities(node,node.left) > 0:
                    return False
            if node.right!=None:    
                if self.compare_priorities(node,node.right) > 0:
                    return False
        return True
    
    def count_elements(self,node=0):
        if node==0:
            node=self.root
            
        if node==None:
            return 0
        else:
            num=self.count_elements(node.left)+self.count_elements(node.right)+1
            return num
    
    def move_node_to_root(self,node):
        """Moves the node to the root, but
           breaks the heap property in the proccess.
           Afterwards a splitting a this vertex is trivial"""
        parent=node.parent
        while parent!=None:
            if parent.left==node:
                self.rotate_right(parent)
            else:
                self.rotate_left(parent)
            parent=node.parent
    
    def split_at_node(self,node):
        """Splits the treap a the given node."""
        self.move_node_to_root(node)
        left_treap=Treap(compare=self.compare)
        right_treap=Treap(compare=self.compare)
        root=self.root
        if root.left!=None:
            left_treap.empty=False
            left_treap.root=root.left
            left_treap.root.parent=None
        if root.right!=None:
            right_treap.empty=False
            right_treap.root=root.right
            right_treap.root.parent=None
        root.left=None
        root.right=None
        return (left_treap,root,right_treap)
    
    def split(self,key):
        """Splits the treap at the given key
           value. Note that the old treap no longer
           satisfies the heap property; should
           be destroyed but it is difficult and
           undesirable to do so in Python."""
        node=self.find(key)
        if node!=None:
            return self.split_at_node(node)
        print "NONE"
        return (self,None,None)
            
    
    def paste(self,node,T2):
        """Returns a new treap conaining self, the node and the
           treap T2. The original treaps, self and T2 no longer
           satisfy the heap property."""
        treap=Treap(compare=self.compare)
        treap.empty=False
        treap.root=node
        treap.root.left=self.root
        treap.root.right=T2.root
        if treap.root.left!=None:
             treap.root.left.parent=treap.root
        if treap.root.right!=None:
             treap.root.right.parent=treap.root
        treap.root.parent=None
        treap.restore_heap_downwards(treap.root)
        return treap
    
    def join(self,T2):
        """Returns the join of self and T2, destroys
           the heap property of both in the proccess. It
           assumes T1<=T2"""
        if self.empty:
            return T2
        elif T2.empty:
            return self
        else:
            max_node=self.max()
            self.delete_node(max_node)
            return self.paste(max_node,T2)
        
    def compute_height(self,node):
        if node==None:
            return 0
        left=self.compute_height(node.left)
        right=self.compute_height(node.right)
        h=max(left,right)
        return h+1
    
    def successor(self,node):
        """Returns the succesor of node"""
        if node.right!=None:
            return self.min_tree(node.right)
        elif node.parent!=None:
            parent_node=node.parent
            son_node=node
            while parent_node.parent!=None and parent_node.left!=son_node:
                son_node=parent_node
                parent_node=parent_node.parent
            if parent_node.left!=son_node:
                return None
            else:
                return parent_node
        else:
            return None
        
    def predecessor(self,node):
        """Returns the predecessor of a node"""
        if node.left!=None:
            return self.max_tree(node.left)
        elif node.parent!=None:
            parent_node=node.parent
            son_node=node
            while parent_node.parent!=None and parent_node.right!=son_node:
                son_node=parent_node
                parent_node=parent_node.parent
            if parent_node.right!=son_node:
                return None
            else:
                return parent_node
        else:
            return None
        
   
    class Node(object):
        
        def __init__(self,key=0,obj=None):
        
            self.key=key
            self.obj=obj
            self.priority=List(car=random.random())
            self.parent=None
            self.right=None
            self.left=None

        
        #for debugging purposes
        def __str__(self):
            
            if self.left==None:
                sleft="()"
            else:
                sleft=self.left.__str__()
                
            if self.right==None:
                sright="()"
            else:
                sright=self.right.__str__()
            snode="(key="+self.key.__str__()+",pr="+self.priority.car.__str__()+","+self.obj.__str__()+")"
            s="("+snode+"("+sleft+","+sright+")"+")"
            return s
                
                

#Test functions
def treap_sort(s,t=100):
    treap=Treap(max_size=s)
    for i in range(t):
#        print "sort",i
        for j in range(s):
            treap.insert(random.randint(0,2*s))
        while not treap.empty:
            node=treap.min()
#            print node.key
            treap.delete(node.key)
            
        
#Maintainers

#This is an implementation of an Algorithm"
#in "Maintenance of Configurations in the Plane
#by Overmars and Leeuwen
#I am assuming that all lines have a defines slope
class Envelope_Mantainer(Treap):
    """Mantains the Lower or Upper envelope of a set of lines"""
    
    @staticmethod
    def compare_lines(l1,l2):
                if l1.m<l2.m:
                    return -1
                elif l1.m>l2.m:
                    return 1
                return 0
    
    @staticmethod
    def point_of_intersection(T1,T2):
            """Given two convex treaps of lines T1 and T2,
               such that all the lines of T1 have
               smaller  slope that those of T2, it returns
               their point of intersection."""
            
            #Quick check for especial cases
            if T1.empty or T2.empty:
                return (T1.max(),T2.min())
                
            def get_point(T,node1):
                node2=T.predecessor(node1)
                if node2==None:
                    node2=T.successor(node1)
                p=node1.obj.line_intersection(node2.obj)
                if p==None:
                    print "Error en get_point"
                    print "m1=",node1.obj.m,"b1=",node1.obj.b
                    print "m2=",node2.obj.m,"b2=",node2.obj.b              
                return p
            
            def found_node(node):
                if node.left==None and node.right==None:
                    return True
                return False
            
            #Following Overmars and Leeuwen
            #Check special cases!!
            def get_case(l,m,q):
                side_l=l.point_in_line(q)
                side_m=m.point_in_line(q)
                
                #print "get case"
                #print side_m
                #print side_l
                
                if side_m<=0:
                    if side_l<=0:
                        return "C2"
                    else:
                        return "A2"
                else:
                    if side_l<=0:
                        return "A1"
                    else:
                        return "C1"
                    
            #check wheter this is the proposed intersection
            def check_int(l1_node,l2_node):
                p=l1_node.obj.line_intersection(l2_node.obj)
                suc1=T1.successor(l1_node)
                pre1=T1.predecessor(l1_node)
                suc2=T2.successor(l2_node)
                pre2=T2.predecessor(l2_node)
                
                if suc1!=None:
                    #print "suc1"
                    #print suc1.obj.m
                    if suc1.obj.point_in_line(p)>0:
                        return False
                if suc2!=None:
                    #print "suc2"
                    #print suc2.obj.m
                    if suc2.obj.point_in_line(p)>0:
                        return False
                if pre1!=None:
                    #print "pre1"
                    #print pre1.obj.m
                    if pre1.obj.point_in_line(p)>0:
                        return False
                if pre2!=None:
                    #print "pre2"
                    #print pre2.obj.m
                    if pre2.obj.point_in_line(p)>0:
                        return False
                    
                return True
            
            #An ugly workaoround
            def fix_int(l1_node,l2_node):
                #print "fixing"
                l2_nodes=[l2_node]
                
                suc2=T2.successor(l2_node)
                pre2=T2.predecessor(l2_node)
                
                if suc2!=None:
                    l2_nodes.append(suc2)
                if pre2!=None:
                    l2_nodes.append(pre2)
                for n2 in l2_nodes:
                    if check_int(l1_node,n2):
                        return (l1_node,n2)
                return (None,None)    
                               
            def print_intervals():
                print "intervals"
                print l1_min,l1_max
                print l2_min,l2_max
            
            foundT1=found_node(T1.root)
            foundT2=found_node(T2.root)
            
            l1_node=T1.root
            l2_node=T2.root
            
            l1_min=None
            l2_min=None
            l1_max=None
            l2_max=None
            
            while (not foundT1) or (not foundT2):
                
                if check_int(l1_node,l2_node):
                    return (l1_node,l2_node)
                
                #print "not foundT1 or not found T2"
                #print l1_node.obj.m
                #print l2_node.obj.m
                
                while foundT1 and (not foundT2):
                    #print "foundT1 but not T2"
                    #print l1_node.obj.m
                    #print l2_node.obj.m
                    #print_intervals()
                    l1_nodes=[l1_node]
                    suc1=T1.successor(l1_node)
                    pre1=T1.predecessor(l1_node)
                    if suc1!=None:
                        l1_nodes.append(suc1)
                    if pre1!=None:
                        l1_nodes.append(pre1)
                    
                    start_n2=l2_node
                    for l1_node in l1_nodes:
                        l2_node=start_n2
                        foundT2=False
                        while not foundT2:
                            #print l2_node.obj.m
                            #print l1_node.obj.m
                            #print_intervals()
                            p=get_point(T2,l2_node)
                            side=l1_node.obj.point_in_line(p)
                            #below
                            if side==1:
                                #print "below"
                                if l2_node.right!=None:
                                    l2_min=l2_node.obj.m
                                    l2_node=l2_node.right
                                    foundT2=found_node(l2_node)
                                else:
                                    foundT2=True
                        
                                #on the line
                            if side==0:
                                #print "on the line"
                                foundT2=True
                        
                            #above the line 
                            if side==-1:
                                #print "above"
                                if l2_node.left!=None:
                                    l2_max=l2_node.obj.m
                                    l2_node=l2_node.left
                                    foundT2=found_node(l2_node)
                                else:
                                    foundT2=True
                        (n1,n2)=fix_int(l1_node,l2_node)
                        if n1!=None:
                            return (n1,n2)
                    #print "ERROR found T1"
                
                while foundT2 and (not foundT1):
                    #print "found T2 but not T1"
                                
                    l2_nodes=[l2_node]
                    suc2=T2.successor(l2_node)
                    pre2=T2.predecessor(l2_node)
                    if suc2!=None:
                        l2_nodes.append(suc2)
                    if pre2!=None:
                        l2_nodes.append(pre2)
                    
                    start_n1=l1_node
                    for l2_node in l2_nodes:
                        l1_node=start_n1
                        foundT1=False
                        while not foundT1:
                            q=get_point(T1,l1_node)
                            side=l2_node.obj.point_in_line(q)
                            #print_intervals()
                            #print l2_node.obj.m
                            #print l1_node.obj.m
                            #below
                            if side==1:
                                #print "below"
                                if l1_node.left!=None:
                                    l1_max=l1_node.obj.m
                                    l1_node=l1_node.left
                                    foundT1=found_node(l1_node)
                                else:
                                    foundT1=True
                            #on the line
                            if side==0:
                                #print "in the line"
                                foundT1=True
                            #above the line
                            if side==-1:
                                #print "above"
                                if l1_node.right!=None:
                                    l1_min=l1_node.obj.m
                                    l1_node=l1_node.right
                                    foundT1=found_node(l1_node)
                                else:
                                    foundT1=True
                        (n2,n1)=fix_int(l2_node,l1_node)
                        if n1!=None:
                            return (n1,n2)
                    #print "ERROR found T2"
                                    
                if (not foundT1) and (not foundT2):
                    #print "found none"
                    #print_intervals()
                    #print l1_node.obj.m
                    #print l2_node.obj.m
                    
                    #was l1_node and l2_node resp
                    maxT1=T1.max_tree(T1.root)
                    minT2=T2.min_tree(T2.root)
                    midslope=(minT2.obj.m+maxT1.obj.m)/2
                    p=get_point(T2,l2_node)
                    q=get_point(T1,l1_node)
                    b=p[1]-midslope*p[0]
                    mid_line=line.Line(p=p,q=[p[0]+1,midslope*p[0]+midslope+b])
                    vertical_line=line.Line(p=p,q=[p[0],p[1]+1])
                    side=get_case(mid_line,vertical_line,q)
                    
                    #print "p and q"
                    #print p
                    #print q
                    
                    if side=="A1":
                        if l2_node.right!=None:
                            #print side
                            #print "Delete the part of T2 below p"
                            l2_min=l2_node.obj.m
                            l2_node=l2_node.right
                            foundT2=found_node(l2_node)
                        else:
                            l2_min=l2_node.obj.m
                            foundT2=True
                            
                    if side=="C1":
                        #print side
                        #print "Delete the part of T1 above q"
                        if l1_node.left!=None:
                            l1_max=l1_node.obj.m
                            l1_node=l1_node.left
                            foundT1=found_node(l1_node)
                        else:
                            l1_max=l1_node.obj.m
                            foundT1=True
                            
                    if side=="A2":
                        #print side
                        #print "Delete the part of T2 above p"
                        if l2_node.left!=None:
                            l2_max=l2_node.obj.m
                            l2_node=l2_node.left
                            foundT2=found_node(l2_node)
                        else:
                            l2_max=l2_node.obj.m
                            foundT2=True
                            
                    if side=="C2":
                        #print side
                        #print "Delete the part of T1 below q"
                        if l1_node.right!=None:
                            l1_min=l1_node.obj.m
                            l1_node=l1_node.right
                            foundT1=found_node(l1_node)
                        else:
                            l1_min=l1_node.obj.m
                            foundT1=True
        
            return (l1_node,l2_node)
    
   
    def __init__(self,lower=False):
        Treap.__init__(self)
        self.lower=lower
    
    def print_local_envs(self,node):
        if node.__class__==self.Env_Node:
            print node.key
            node.local_env.show()
            self.print_local_envs(node.left)
            self.print_local_envs(node.right)
            
    def rotate_right(self,node):
        #Case 1
        if node.right==None:
            #I am assuming that since node.right is None, node.left
            #has an empty local_env. I am reusing it so to avoid
            #the extra cost of creating a new empty local_env.
            temp_env=node.left.local_env
            node.left.local_env=node.local_env
            node.local_env=temp_env
        #Case 2
        elif node.bridge_left.m<=node.left.bridge_left.m:
            Env=node.local_env
            Env_right=node.right.local_env
            Env_left=node.left.local_env
            Env_left.insert(node.bridge_left)
            Env_right.insert(node.bridge_right)
            (Env_left_left,n,Env_left_right)=Env_left.split(node.left.bridge_left.m)
            Env_left_left.insert_node(n)
            Env_left_right=node.left.right.local_env.join(Env_left_right)
            Env_left_left=Env_left_left.join(node.left.left.local_env)
            #updating node.right info
            (rleft,rright)=Envelope_Mantainer.point_of_intersection(Env_left_right,Env_right)
            (node.right.local_env,n,Env_right)=Env_right.split(rright.key)
            Env_right.insert_node(n)
            #updating node.left.right info
            (Env_left_right,n,node.left.right.local_env)=Env_left_right.split(rleft.key)
            Env_left_right.insert_node(n)
            Env_right=Env_left_right.join(Env_right)
            #updating node.left.left info remove bridge
            Env_left_left.delete(node.bridge_left.m)
            node.left.left.local_env=Env_left_left
            #updating node.left info
            node.left.local_env=Env
            node.left.bridge_right=node.bridge_right
            node.left.bridge_left=node.bridge_left
            #updating node info
            Env_right.delete(node.bridge_right.m)
            node.local_env=Env_right
            if self.lower:
                nrright=line.Line()
                nrright.m=rright.obj.m
                nrright.b=-rright.obj.b
                
                nrleft=line.Line()
                nrleft.m=rleft.obj.m
                nrleft.b=-rleft.obj.b
            else:
                nrright=rright.obj
                nrleft=rleft.obj    
            node.bridge_right=nrright
            node.bridge_left=nrleft
        #Case 3 Check HERE and below!
        else:
            temp_env=node.local_env
            node.local_env=node.left.right.local_env
            node.left.right.local_env=node.left.local_env
            node.left.local_env=temp_env

        #rotate right!
        Treap.rotate_right(self,node)
    
    def rotate_left(self,node):
        #Case 1
        if node.right.right==None:
            #I am assuming that since node.right.right is None, node.right
            #has an empty local_env. I am reusing it so to avoid
            #the extra cost of creating a new empty local_env.
            temp_env=node.right.local_env
            node.right.local_env=node.local_env
            node.local_env=temp_env
        #Case 2
        elif node.bridge_right.m>node.right.bridge_left.m:
            #######
            Env=node.local_env
            Env_left=node.left.local_env
            Env_right=node.right.local_env
            Env_right.insert(node.bridge_right)
            Env_left.insert(node.bridge_left)
            (Env_right_left,n,Env_right_right)=Env_right.split(node.right.bridge_left.m)
            Env_right_left.insert_node(n)
            Env_right_left=Env_right_left.join(node.right.left.local_env)
            Env_right_right=node.right.right.local_env.join(Env_right_right)
            #updating node.left info
            (rleft,rright)=Envelope_Mantainer.point_of_intersection(Env_left,Env_right_left)
            (Env_left,n,node.left.local_env)=Env_left.split(rleft.key)
            Env_left.insert_node(n)
            #updating node.right.left info
            (node.right.left.local_env,n,Env_right_left)=Env_right_left.split(rright.key)
            Env_right_left.insert_node(n)
            Env_left=Env_left.join(Env_right_left)
            #updating node.right.right info remove bridge
            Env_right_right.delete(node.bridge_right.m)
            node.right.right.local_env=Env_right_right
            #updating node.right info
            node.right.local_env=Env
            node.right.bridge_left=node.bridge_left
            node.right.bridge_right=node.bridge_right
            #updating node info
            Env_left.delete(node.bridge_left.m)
            node.local_env=Env_left
            if self.lower:
                nrright=line.Line()
                nrright.m=rright.obj.m
                nrright.b=-rright.obj.b
                
                nrleft=line.Line()
                nrleft.m=rleft.obj.m
                nrleft.b=-rleft.obj.b
            else:
                nrright=rright.obj
                nrleft=rleft.obj    
            node.bridge_right=nrright
            node.bridge_left=nrleft
        #Case 3
        else:
            temp_env=node.local_env
            node.local_env=node.right.left.local_env
            node.right.left.local_env=node.right.local_env
            node.right.local_env=temp_env

        #rotate left!
        Treap.rotate_left(self,node)
        
    def insert(self,l,debug=False):
        node=self.DOWN(l.m)
        enode=self.Env_Node(obj=l,lower=self.lower)
        lnode=self.Line_Node(obj=l,lower=self.lower)
        enode.left=lnode
        lnode.parent=enode
        if node==None:
            self.root=enode
            self.empty=False
        elif node.__class__==self.Env_Node:
            #must be a right child
            enode.parent=node
            node.right=enode            
        elif node.__class__==self.Line_Node:
            if self.compare(node.key,l.m)==0:
                node.insert(l,lower=self.lower)
                enode=node.parent
            else:
                if node.parent.left==node:
                    node.parent.left=enode
                else:
                    node.parent.right=enode
                enode.parent=node.parent
                node.parent=enode
                enode.right=node
        #Quitar  
        if debug:
            return enode
        self.UP(enode)
        #self.restore_heap(enode)
        #return enode
        
   
    def DOWN(self,key):
        if self.empty:
            return None
        
        node=self.root
        
        while node.__class__==self.Env_Node:
            parent=node
            if node.right==None: 
               node.left.local_env=node.local_env
            else:  
                (Tl,n,Tr)=node.local_env.split(node.bridge_left.m)
                Tl.insert_node(n)
                node.left.local_env=Tl.join(node.left.local_env)
                node.right.local_env=node.right.local_env.join(Tr)
                    
            if self.compare(node.key,key)<0:
                node=node.right
            elif self.compare(node.key,key)>=0:
                node=node.left
        
        if node==None:
            node=parent
            
        return node
    
    def UP(self,node):
        """Repairs what DOWN did."""
        while node!=None:
            #print "hola"
            if node.__class__==self.Line_Node:
                node=node.parent
            elif node.right==None:
                node.local_env=node.left.local_env
                node.bridge_left=None
                node.bridge_right=None
                node.left.local_env=None
                node=node.parent
            else:
                (lleft,lright)=Envelope_Mantainer.point_of_intersection(node.left.local_env,node.right.local_env)
                (Env_left,n,node.left.local_env)=node.left.local_env.split(lleft.key)
                Env_left.insert_node(n)
                (node.right.local_env,n,Env_right)=node.right.local_env.split(lright.key)
                Env_right.insert_node(n)
                node.local_env=Env_left.join(Env_right)
                if self.lower:
                    nlleft=line.Line()
                    nlleft.m=lleft.obj.m
                    nlleft.b=-lleft.obj.b
                    nlright=line.Line()
                    nlright.m=lright.obj.m
                    nlright.b=-lright.obj.b
                else:
                    nlleft=lleft.obj
                    nlright=lright.obj
                node.bridge_left=nlleft
                node.bridge_right=nlright
                node=node.parent
                
    def print_env(self):
        self.root.local_env.print_env()
    
    def delete_node(self,node):
        if node==None:
            return None
        while node.left.__class__!=self.Line_Node or node.right.__class__==self.Env_Node:
            if node.left.__class__==self.Line_Node or node.right.__class__==self.Env_Node:
                if node.left.__class__==None:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)   
            else:
                if self.compare_priorities(node.left,node.right) > 0:
                    self.rotate_left(node)
                else:
                    self.rotate_right(node)
        #We have moved the node to be deleted to the bottom!        
        if  node.parent!=None:        
            if node.parent.left==node:
                node.parent.left=None
            else:
               node.parent.right=None
        else:
            self.root=None
            self.empty=True
        
        
        return node
    
    class Env_Node(Treap.Node):
        
        def __init__(self,obj=line.Line(),lower=False):
                Treap.Node.__init__(self,key=obj.m)
                #$Q_alpha$ in the "Mantainance of Configurations"
                self.local_env=Envelope_Mantainer.Treap_Line(lower=lower)
                #self.local_env.insert(obj)
                self.bridge_left=obj
                self.bridge_right=None
                
    class Line_Node(Treap.Node):
        """It stores all lines with a same slope."""
        
        def __init__(self,obj=line.Line(),lower=False):
            Treap.Node.__init__(self,key=obj.m)
            self.local_env=Envelope_Mantainer.Treap_Line(lower=lower)
            self.local_env.insert(obj)
            self.lines=[obj]
            self.obj=obj
            self.empty=False
            
        def min_line(self):
            min=0
            for i in range(len(self.lines)):
                if self.lines[i].b<self.lines[min].b:
                    min=i
            return min
        
        def max_line(self):
            max=0
            for i in range(len(self.lines)):
                if self.lines[i].b>self.lines[max].b:
                    max=i
            return max
        
        def insert(self,line,lower=False):
            self.lines.append(line)
            if lower:
                min=self.min_line()
                self.obj=self.lines[min]
            else:
                max=self.max_line()
                self.obj=self.lines[max]
            self.local_env=Envelope_Mantainer.Treap_Line(lower=lower)
            self.local_env.insert(self.obj)
        
        def delete(self,lower):
            if lower:
                min=self.min_line()
                self.lines.pop(min)
                if len(self.lines)==0:
                    self.empty=True
                    self.obj=None
                    self.key=None
                else:
                    min=self.min_line()
                    self.obj=self.lines[min]
            else:
                max=self.max_line()
                self.lines.pop(max)
                if len(self.lines)==0:
                    self.empty=True
                    self.obj=None
                    self.key=None
                else:
                    max.self.max_line()
                    self.obj=self.lines[max]

    #I will assume for the time being that
    #there are no vertical lines and not two lines have the same slope
    class Treap_Line(Treap):
        """Treap representing the envelopes"""
        
        def __init__(self,lower=False):
            self.lower=lower
            Treap.__init__(self)        
        
        def insert(self,l):
            obj=l
            if self.lower:
                obj=line.Line()
                obj.m=l.m
                obj.b=-l.b
            Treap.insert(self,key=obj.m,obj=obj)
            
        def split_at_node(self,node):
            """Splits the treap a the given node."""
            self.move_node_to_root(node)
            left_treap=Envelope_Mantainer.Treap_Line(lower=self.lower)
            right_treap=Envelope_Mantainer.Treap_Line(lower=self.lower)
            root=self.root
            if root.left!=None:
                left_treap.empty=False
                left_treap.root=root.left
                left_treap.root.parent=None
            if root.right!=None:
                right_treap.empty=False
                right_treap.root=root.right
                right_treap.root.parent=None
            root.left=None
            root.right=None
            return (left_treap,root,right_treap)
    
        def paste(self,node,T2):
            """Returns a new treap conaining self, the node and the
               treap T2. The original treaps, self and T2 no longer
               satisfy the heap property."""
            treap=Envelope_Mantainer.Treap_Line(lower=self.lower)
            treap.empty=False
            treap.root=node
            treap.root.left=self.root
            treap.root.right=T2.root
            if treap.root.left!=None:
                 treap.root.left.parent=treap.root
            if treap.root.right!=None:
                 treap.root.right.parent=treap.root
            treap.root.parent=None
            treap.restore_heap_downwards(treap.root)
            return treap
        
        def get_env(self):
            (head,tail)=self.get_env_rec(self.root)
            return head
        
        def print_env(self):
            lnode=self.get_env()
            str="["
            while not lnode.empty:
                str=str+"["+lnode.car[0].__str__()+","+lnode.car[1].__str__()+"],"
                lnode=lnode.cdr
            str=str[:len(str)-1]+"]"
            print str
        
        def get_env_rec(self,node):
            if self.lower:
                b=-node.obj.b
            else:
                b=node.obj.b
            lst=List(car=(node.obj.m,b))
            if node.left!=None:
                (head,ltail)=self.get_env_rec(node.left)
                ltail.cdr=lst
            else:
                head=lst
            if node.right!=None:
                (rhead,tail)=self.get_env_rec(node.right)
                lst.cdr=rhead
            else:
                tail=lst
            return (head,tail)
            

class dynamic_ch(object):
    
    def __init__(self):
        self.root=None
        self.empty = True
        
    def insert(self, p):
        v = self.Node(key = p)
        v.J = p
        
        if self.empty:
            self.root = v
            self.empty = False       #XXX: Ql debería tener a p, no?
            return
        
        v.Ql.insert(key = p)
        u = self.DOWN(self.root, v)
        print "DOWN gave", u, u.Ql.root
        
        if u.key != v.key:
            aux = self.Node()
            parent = u.parent
            if parent is None:                       #u was the root
                u.Ql.insert(u.key)
                print "root"
                self.root = aux
                u.parent = aux
                v.parent = aux
                if v.key[1] >= u.key[1]:
                    aux.key = [0,u.key[1]]
                    aux.left = u
                    aux.right = v
#                    aux.J = u.key
                else:
                    aux.key = [0,v.key[1]]
                    aux.left = v
                    aux.right = u
#                    aux.J = v.key
                    
            elif parent.right is u:
                parent.right = aux
                aux.parent = parent
                u.parent = aux
                v.parent = aux
                if v.key[1] >= u.key[1]:
                    aux.key = [0,u.key[1]]
                    aux.left = u
                    aux.right = v
#                    aux.J = u.key
                else:
                    aux.key = [0,v.key[1]]
                    aux.left = v
                    aux.right = u
#                    aux.J = v.key
            else:
                parent.left = aux
                aux.parent = parent
                aux.key = [0,v.key[1]]
                aux.left = v
                aux.right = u
#                aux.J = v.key
                u.parent = aux
                v.parent = aux
            
        else:
            print "Point already in the tree"
            self.UP(u)
            return
        
        self.UP(v)
        
    def delete(self, p):
        aux = self.Node(key=p)
        u = self.DOWN(self.root, aux)
        print "DOWN gave", u

        if u.key != p:
            print "Point not found"
            self.UP(u)
            return

        sib = u.parent.right
        if sib is u:
            sib = u.parent.left
            
        grandpa = u.parent.parent
        
        if grandpa.left is u.parent:
            grandpa.left = sib
        else:
            grandpa.right = sib
            
        sib.parent = grandpa
        
        self.UP(sib)
        
        
        
    def isLeaf(self, node):
        return node.right is None and node.left is None
        
    def DOWN(self, v, p):
#        print "DOWN checks", v
        if not self.isLeaf(v):
#            print "        ... not a leaf"
#            print "splitting", v.Ql.root
#            print "at key", v.J
            Q1, r, Q2 = v.Ql.split(v.J)
            Q1.insert_node(r)
            if v.left != None:
                v.left.Ql = Q1.join(v.left.Ql)
            if v.right != None:
                v.right.Ql = v.right.Ql.join(Q2)
            if p.key[1] <= v.key[1]:
                v = v.left
            else:
                v = v.right
            return self.DOWN(v, p)
        else:
            return v
            
    def UP(self, v):
        if v != self.root:
            Q1, Q2, Q3, Q4, J = None,None,None,None,None,
            print "UP Brigding", v, "Ql:", v.Ql.root
            print "and        ",
            if v.parent.left is v:                
                print v.parent.right, "Ql", v.parent.right.Ql.root, "this is a right son"
                Q1, Q2, Q3, Q4, J = dynamic_ch.bridge(v.Ql, v.parent.right.Ql)
            else:
                print v.parent.left, "Ql", v.parent.left.Ql.root, "this is a left son"
                Q1, Q2, Q3, Q4, J = dynamic_ch.bridge(v.parent.left.Ql, v.Ql)
            v.parent.left.Ql = Q2
            v.parent.right.Ql = Q3
            v.parent.Ql = Q1.join(Q4)
            v.parent.J = J
            v.parent.key = [0,max(v.parent.key[1], v.parent.left.key[1])]
            self.UP(v.parent)
        return 
            
    @classmethod        
    def treapToList(cls, T):
        l = []
        def inOrder(node):
            if node.right == None and node.left == None:
                l.append(node.key)
                return
            if node.left != None:
                inOrder(node.left)
            l.append(node.key)
            if node.right != None:
                inOrder(node.right)
        if not T.empty:
            inOrder(T.root)
        return l
        
    @classmethod
    def bridge(cls, Lower, Upper):           #The points in Lower should have smaller y coordinates than the ones in Upper
        L1 = dynamic_ch.treapToList(Lower)
        L2 = dynamic_ch.treapToList(Upper)
        
        print "IN BRIDGE", L1
        print "         ", L2
        
        maxy = L1[-1][1]        #The biggest y coordinate of Lower
################### This code works when using the list representation of the treaps ###########
#        iqmin = 0
#        iqmax = len(L1)-1
#        iq = (iqmax + iqmin)/2                          #Indices of points q, qm, qM
#        iqm = iq if iq-1 < 0 else iq-1
#        iqM = iq if iq+1 >= len(L1) else iq+1
#        
#        q = L1[iq]                          #The points q, qm and qM
#        qm = L1[iqm]
#        qM = L1[iqM]
#        
#        ipmin = 0
#        ipmax = len(L2)-1
#        ip = (ipmax + ipmin)/2                      #Analogous to q
#        ipm = ip if ip-1 < 0 else ip-1
#        ipM = ip if ip+1 >= len(L2) else ip+1
#        
#        p = L2[ip]
#        pm = L2[ipm]
#        pM = L2[ipM]
#####################################################################################################

        p_aux = Upper.root
        p = p_aux.key
        pm = Upper.predecessor(p_aux)
        pm = p if pm is None else pm.key
        pM = Upper.successor(p_aux)
        pM = p if pM is None else pM.key
        
        q_aux = Lower.root
        q = q_aux.key
        qm = Lower.predecessor(q_aux)
        qm = q if qm is None else qm.key
        qM = Lower.successor(q_aux)
        qM = q if qM is None else qM.key
        
        print "Puntos"
        print pm, p, pM
        print qm, q, qM
        
        while turn(q, p, qm) < 0 or turn(q, p, qM) < 0 or turn(q, p, pm) < 0 or turn(q, p, pM) < 0:
#            x = raw_input()
            print "IN BRIDGE"
            #Caso 2
            if turn(q, p, qM) >=0 and turn(q, p, pm) >=0 and turn(q, p, pM) >=0 and turn(q, p, qm) < 0:
                print "C2"
#                ipmin = ip
#                iqmax = max(0, iq - 1)
                q_aux = q_aux if q_aux.left is None else q_aux.left
                
            #Caso 3
            elif turn(q, p, pm) >=0 and turn(q, p, qm) >=0 and turn(q, p, pM) >=0 and turn(q, p, qM) < 0:
                print "C3"
#                ipmin = ip
#                iqmin = min(iqm + 1, len(L1)-1)
                q_aux = q_aux if q_aux.right is None else q_aux.right
            #Caso 4
            elif turn(q, p, pm) >=0 and turn(q, p, qm) >=0 and turn(q, p, qM) >=0 and turn(q, p, pM) < 0:
                print "C4"
#                ipmin = min(ip + 1, len(L2)-1)
#                iqmax = iq
                p_aux = p_aux if p_aux.right is None else p_aux.right
            #Caso 5
            elif turn(q, p, pM) >=0 and turn(q, p, qm) >=0 and turn(q, p, qM) >=0 and turn(q, p, pm) < 0:
                print "C5"
#                ipmax = max(0, ip - 1)
#                iqmax = iq
                p_aux = p_aux if p_aux.left is None else p_aux.left
            #Caso 6
            elif turn(q, p, pm) >=0 and turn(q, p, qM) >=0 and turn(q, p, qm) < 0 and turn(q, p, pM) < 0:
                print "C6"
#                ipmin = min(ip + 1, len(L2)-1)
#                iqmax = max(0, iq - 1)
                p_aux = p_aux = p_aux if p_aux.right is None else p_aux.right
                q_aux = q_aux if q_aux.left is None else q_aux.left
            #caso 7
            elif turn(q, p, pM) >=0 and turn(q, p, qM) >=0 and turn(q, p, qm) < 0 and turn(q, p, pm) < 0:
                print "C7"
#                L1 = L1[:iqM+1]
#                iqmax = max(0, iq - 1)
                q_aux = q_aux if q_aux.left is None else q_aux.left
            #Caso 8
            elif turn(q, p, pm) >=0 and turn(q, p, qm) >=0 and turn(q, p, qM) < 0 and turn(q, p, pM) < 0:
                print "C8"
#                ipmin = min(ip + 1, len(L2)-1)
                p_aux = p_aux = p_aux if p_aux.right is None else p_aux.right
            #Caso 9
            elif turn(q, p, pM) >=0 and turn(q, p, qm) >=0 and turn(q, p, qM) < 0 and turn(q, p, pm) < 0:
                print "C9"
                #Calculamos la coordenada y donde se intersectan las tangentes ppm y qqM
                a1 = p[1]-pm[1]
                b1 = p[0]-pm[0]
                
                a2 = q[1]-qm[1]
                b2 = q[0]-qm[0]
                
                c1 = b1*p[1]-a1*p[0]
                c2 = b2*1[1]-a2*q[0]
                
                y = float(a2*c1 - a1*c2)/float(a2*b1 - a1*b2)
                
                #Subcaso 1:
                if y <= maxy:
#                    iqmin = qm
                    q_aux = q_aux if q_aux.left is None else q_aux.left
                #Subcaso 2
                else:
#                    ipmax = pM
                    p_aux = p_aux = p_aux if p_aux.right is None else p_aux.right
            
###################################################################################################33
#            iq = (iqmax + iqmin)/2
#            iqm = max(0, iq-1)
#            iqM = min(len(L1)-1, iq+1)
#            
#            q = L1[iq]
#            qm = L1[iqm]
#            qM = L1[iqM]
#            
#            ip = (ipmax + ipmin)/2
#            ipm = max(0, iq-1)
#            ipM = min(len(L2)-1, iq+1)
#            
#            p = L2[ip]
#            pm = L2[ipm]
#            pM = L2[ipM]
#######################################################################################################
            
            p = p_aux.key
            pm = Upper.predecessor(p_aux)
            pm = p if pm is None else pm.key
            pM = Upper.successor(p_aux)
            pM = p if pM is None else pM.key
            
            q = q_aux.key
            qm = Lower.predecessor(q_aux)
            qm = q if qm is None else qm.key
            qM = Lower.successor(q_aux)
            qm = q if qM is None else qM.key
        #ip and iq are the indices of the points that form the bridge
        J = q
#        print "p y q", q, p
        
        Q1, q, Q2 = Lower.split(q)
        Q3, p, Q4 = Upper.split(p)
        
        Q1.insert_node(q)
        Q4.insert_node(p)
        print "DONE!"
        print Q1.root
        print Q2.root
        print Q3.root
        print Q4.root
        print J
        return Q1, Q2, Q3, Q4, J
        
    class Node(object):
        
        def __init__(self,key = [0,0]):
        
            self.key = key          #A point is the node is a leaf, otherwise [0, maxy] where maxy is the biggest y coordinate in the left subtree
            self.Ql = Treap(lambda p, q: p[1]-q[1])       #This part does not contribute to the lc-hull of parent
            self.J = key           #The position of the support point in parent's lc-hull
            self.parent = None
            self.right = None
            self.left = None

        #for debugging purposes
        def __str__(self):
            
            if self.left==None:
                sleft="()"
            else:
                sleft=self.left.__str__()
                
            if self.right==None:
                sright="()"
            else:
                sright=self.right.__str__()
            snode="(key="+self.key.__str__()+")"
            s="("+snode+"("+sleft+","+sright+")"+")"
            return s