from z3 import *
import gurobipy as gp
from gurobipy import GRB
import re
import time
import pstats
import sys
from node_class import *
from edge_class import *
from state_class import *
from transition_class import*
from collections import OrderedDict
sys.setrecursionlimit(4000000)

s=Solver()
s.add(z3.BoolVal(True))
p=frozenset([z3.BoolVal(True)])
visited={}
solset=[]

#Incremental SMT solving version of Algorithm 1.
def dfs(node,state, path):
    global s
    global visited
    global solset
    res=(s.check()==z3.sat)
    if not res:
        return
    
    if state.final and res: #final state and satisfiable.
        print(node.properties["name"])

    for e in node.edges:
        for t in state.delta:
            temp_form=t.formula
            rep=z3.BoolVal(True)
            for p in t.parameters: #p=(var,loc,typ)
                if p[1]=="from" :# alpha
                    rep=z3.RealVal(e.node1.properties[str(p[0])])
                elif p[1]=="to": #omega
                    rep=z3.RealVal(e.node2.properties[str(p[0])])
                elif p[1]=="edge": #e
                    rep=z3.RealVal(e.properties[str(p[0])])
                temp_form=z3.substitute(temp_form,(p[0],rep))
            #print(temp_form)
            temp=frozenset([temp_form])
            j=path.union(temp)
            if not temp_form in path:
                l=True
            else:
                l=False 
            if not (e.node2,t.state2,j) in visited:
                if l:
                    s.push() #Incremental SMT solving
                    s.add(temp_form)
                visited[e.node2,t.state2,j]=True
                dfs(e.node2,t.state2,j) #Move on.
                if l:
                    s.pop() #Incremental SMT solving



###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################
###############################################################################################################




#Add a boolean for complex or noncomplex. complex meaning right handside is not just a number but a more complex expression.
#A complex expression needs to be replaced and then evaluated, 
#Tuple consists of (left handside, operator, right handside variable, complex, place)

visited_qla=set()
def start_test(model,start_node,start_state,start_tup,start_path,index_expr):

    dfs_QLA_with_stack(start_node,start_state,start_tup,start_path,model,index_expr)

#relax gives the tightest bounds. P, E  to P' E' in the thesis.
def relax(tup,edge,trans,index_expr):
    tup2=list(tup).copy()
    #check now the tuples that can be changed by the transition:
    for i in trans.formula:
     #assumes a non complex expression.
        if tup2[i]=='!':
            tup2[i]=0
        else:
            info=index_expr[i]
            operator=info[1]
            curr_prop=info[2]
            place=info[4]
            complex_expr=info[3]
            new_val=0
            if not complex_expr:
                if place=='w' and curr_prop in edge.node2.properties: 
                    new_val=int(edge.node2.properties[curr_prop])
                elif place=='a' and curr_prop in edge.node1.properties:
                    new_val=int(edge.node1.properties[curr_prop])
                elif place=='e' and curr_prop in edge.properties:
                    new_val=int(edge.properties[curr_prop])
                    

                if tup2[i]=='?':
                    tup2[i]=new_val
                elif operator=="<" or operator =="<=":
                    tup2[i]=min(new_val,tup2[i])
                elif operator==">" or operator ==">=":
                    tup2[i]=max(new_val,tup2[i]) 
                elif operator == "==" and not new_val==tup2[i]:
                    return False
            else:
                for e in place:
                    if e[1]=='w':
                        curr_prop=curr_prop.replace(e[0],str(edge.node2.properties[e[0]]))
                    elif e[1]=='a':
                        curr_prop=curr_prop.replace(e[0],str(edge.node1.properties[e[0]]))
                    elif e[1]=='e':
                        curr_prop=curr_prop.replace(e[0],str(edge.properties[e[0]]))
                new_val=eval(curr_prop)
                if tup2[i]=='?':
                    tup2[i]=new_val
                elif operator=="<" or operator =="<=":
                    tup2[i]=min(new_val,tup2[i])
                elif operator==">" or operator ==">=":
                    tup2[i]=max(new_val,tup2[i])
                elif operator == "==" and not new_val==tup2[i]:
                    return False


    return tuple(tup2)



#To find paths here, keep a stack with current popped nodes in it.
#Algorithm 2 in the thesis,
#Iterative dfs 
def dfs_QLA_with_stack(node,state,tup,path_t,model,index_expr):
    global s
    global visited_qla
    stackk=[(node,state,tup)]
    vis={}
    vis[(node,state)]={tup}
    visited_qla.add((node,state,tup))
    while not len(stackk)==0:
        curr=stackk.pop()
        #print(curr)
        for i in range(0,len(curr[2])):
            val=curr[2][i]
            if val=='?' or val=='!':
                continue
            else:
                val=int(curr[2][i])
                info=index_expr[i] 
                operator=info[1]
                lhs=info[0]
                if operator=="<":
                    model.addConstr(lhs< val)
                elif operator==">":
                    model.addConstr(lhs> val)
                elif operator=="<=":
                    model.addConstr(lhs<= val)
                elif operator== ">=":
                    model.addConstr(lhs>= val)
                elif operator == "==":
                    model.addConstr(lhs == val)
        model.optimize()
        #print(model.display())
        res= model.status==GRB.INFEASIBLE
        if curr[1].final and not res:
            print(curr[0].properties["name"],curr[0].properties["pos_x"],curr[0].properties["pos_y"])
            #print("PATH:")
            # for l in stackk:
            #     v=l[0]
            #     print(v.properties["name"],v.properties["pos_x"],v.properties["pos_y"])
            # print("ENDPATH")
        elif res:
            for constr in model.getConstrs():
                model.remove(constr)
            continue

        for constr in model.getConstrs():
            model.remove(constr)
            
        for e in curr[0].edges:
            for t in curr[1].delta:
                new_tup=relax(curr[2],e,t,index_expr)
                better=to_exp(e.node2,t.state2,new_tup,vis,index_expr)
                if not (e.node2,t.state2,new_tup) in visited_qla and not new_tup==False and better:
                    visited_qla.add((e.node2,t.state2,new_tup))
                    stackk.append((e.node2,t.state2,new_tup))


#keep track of incomparable search states
def to_exp(v,q,new_tuple,vis,index_expr):
    if not new_tuple:
        return False
    if (v,q) not in vis:
        vis[(v,q)]={new_tuple}
        return True
    else:
        tuples=vis[(v,q)].copy()
        new_tuples=tuples.copy()
        for old_tuple in tuples:
            res=compare_with_tup(new_tuple,old_tuple,index_expr)
            if res=="worse":
                return False
            if res=="better":
                new_tuples.remove(old_tuple)
                new_tuples.add(new_tuple)
                vis[(v,q)]=new_tuples
                return True


        vis[(v,q)].add(new_tuple)
        return True
        

def compare_with_tup(new_tuple,old_tuple,index_expr):

    if better(old_tuple,new_tuple,index_expr):
        return "worse"
    elif better(new_tuple,old_tuple,index_expr):
        return "better" 
    else:
        return "inc"  #incomparable
    

#Tuple pruning strategy.
def better(tuple1,tuple2,index_expr):
    #Is tuple1 better than tuple2 ? That means it has atleast the questionmarks and exclamation marks of tuple 2 and the lower, upperobunds are better
    for i in range(0,len(tuple1)):
        info=index_expr[i] 
        operator=info[1]
        if tuple1[i]==tuple2[i]:
            continue
        if tuple1[i]=='?' or tuple1[i]=='!':
            continue
        elif tuple2[i]=='?' or tuple2[i]=='!':
            return False
        elif operator=="<" or operator =="<=":
            if tuple1[i]==max(tuple1[i],tuple2[i]):
                continue
            else:
                return False
        elif operator==">" or operator ==">=":
            if tuple1[i]==min(tuple1[i],tuple2[i]):
                continue
            else:
                return False
        elif operator == "==" :
            if tuple1[i]==tuple2[i]:
                continue
    return True


def start_test_endpoints(model,start_node,start_state,start_tup,start_path,index_expr,endpoint):
    dfs_QLA_with_stack_endpoint(start_node,start_state,start_tup,start_path,model,index_expr,endpoint)



def dfs_QLA_with_stack_endpoint(node,state,tup,path_t,model,index_expr,endpoint):
    global s
    global visited_qla
    stackk=[(node,state,tup)]
    vis={}
    vis[(node,state)]={tup}
    visited_qla.add((node,state,tup))
    while not len(stackk)==0:
        curr=stackk.pop()
        #print(curr)
        for i in range(0,len(curr[2])):
            val=curr[2][i]
            if val=='?' or val=='!':
                continue
            else:
                val=int(curr[2][i])
                info=index_expr[i] 
                operator=info[1]
                lhs=info[0]
                if operator=="<":
                    model.addConstr(lhs< val)
                elif operator==">":
                    model.addConstr(lhs> val)
                elif operator=="<=":
                    model.addConstr(lhs<= val)
                elif operator== ">=":
                    model.addConstr(lhs>= val)
                elif operator == "==":
                    model.addConstr(lhs == val)
        model.optimize()
        #print(model.display())
        res= model.status==GRB.INFEASIBLE
        if curr[1].final and not res and curr[0]==endpoint:
            print(curr[0].properties["name"],curr[0].properties["pos_x"],curr[0].properties["pos_y"])
            return True
            #print("PATH:")
            # for l in stackk:
            #     v=l[0]
            #     print(v.properties["name"],v.properties["pos_x"],v.properties["pos_y"])
            # print("ENDPATH")
        elif res:
            for constr in model.getConstrs():
                model.remove(constr)
            continue

        for constr in model.getConstrs():
            model.remove(constr)
            
        for e in curr[0].edges:
            for t in curr[1].delta:
                new_tup=relax(curr[2],e,t,index_expr)
                better=to_exp(e.node2,t.state2,new_tup,vis,index_expr)
                if not (e.node2,t.state2,new_tup) in visited_qla and not new_tup==False and better:
                    visited_qla.add((e.node2,t.state2,new_tup))
                    stackk.append((e.node2,t.state2,new_tup))
