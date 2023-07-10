from main_algorithm import *
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
import random
from collections import OrderedDict
sys.setrecursionlimit(4000000)

#Read the facebook graph:
id_to_node={}#dictionary converting id to the node
nodes=[] #list of nodes
with open('facebook_properties.txt') as file:
    lines = [line.rstrip() for line in file]
edges_facebook=[]
regexp_1 = re.compile(r'N(\w*)\sage:(\w*)\sname:"(\w*)"\spos_x:(-?\w*)\spos_y:(-?\w*)\sheight:(\w*)')
regexp_2 = re.compile(r'N(\w*)->N(\w*) :(\w*)')
#Read nodes
for i in range(0,4309):
    re_match = regexp_1.match(lines[i])
    curr_nod=Node(int(re_match.group(1)))
    curr_nod.add_property("name",str(re_match.group(3)))
    curr_nod.add_property("age",int(re_match.group(2)))
    curr_nod.add_property("pos_x",int(re_match.group(4)))
    curr_nod.add_property("pos_y",int(re_match.group(5)))
    curr_nod.add_property("height",int(re_match.group(6)))
    curr_nod.add_property("id",int(re_match.group(1)))
    nodes.append(curr_nod)
    id_to_node[int(re_match.group(1))]=curr_nod

#Read edges
with open('val_facebook.txt') as file:
    lines4 = [line.rstrip() for line in file]
edge_counter=0
for i in range(4309,len(lines)):
    re_match = regexp_2.match(lines[i])
    from_id=int(re_match.group(1))
    to_id=int(re_match.group(2))
    edge_name=str(re_match.group(3))
    curr_edge=Edge(id_to_node[from_id],id_to_node[to_id],edge_name)
    curr_edge.add_property("val",abs(int(lines4[edge_counter])))
    edges_facebook.append(curr_edge)
    id_to_node[from_id].add_edge(curr_edge)
    edge_counter+=1

print(len(edges_facebook))
    #nodes[0] is start vertex of facebook graph



id_to_node2={}#dictionary converting id to the node
nodes_yt=[] #list of nodes
with open('youtube_nodes.txt') as file:
    lines2 = [line.rstrip() for line in file]
edges_yt=[]
regexp_3 = re.compile(r'N(\w*):\sage:(\w*)\sname:"(\w*)"\spos_x:(-?\w*)\spos_y:(-?\w*)\sheight:(\w*)')
for i in range(0,1134852):
    re_match = regexp_3.match(lines2[i])
    curr_nod=Node(int(re_match.group(1))+1)
    curr_nod.add_property("name",str(re_match.group(3)))
    curr_nod.add_property("age",int(re_match.group(2)))
    curr_nod.add_property("pos_x",int(re_match.group(4)))
    curr_nod.add_property("pos_y",int(re_match.group(5)))
    curr_nod.add_property("height",int(re_match.group(6)))
    curr_nod.add_property("id",int(re_match.group(1))+1)
    nodes_yt.append(curr_nod)
    id_to_node2[int(re_match.group(1))+1]=curr_nod


#Read edges
with open('out.com-youtube') as file:
    lines3 = [line.rstrip().split() for line in file]
for i in range(0,2987624):
    from_id=int(lines3[i][0])
    to_id=int(lines3[i][1])
    if from_id >1134851 or to_id >1134851:
        continue 
    curr_edge=Edge(id_to_node2[from_id],id_to_node2[to_id],edges_facebook[0].name)
    curr_edge.add_property("val",abs(int(lines4[random.randint(0,4000)])))
    edges_yt.append(curr_edge)
    id_to_node2[from_id].add_edge(curr_edge)


n_1=Node(1)
n_1.add_property("name","Geri")
n_1.add_property("age",26)
n_1.add_property("pos_x",-21)
n_1.add_property("pos_y",11)

n_2=Node(2)
n_2.add_property("name","A")
n_2.add_property("age",26)
n_2.add_property("pos_x",19)
n_2.add_property("pos_y",-19)

n_3=Node(3)
n_3.add_property("name","B")
n_3.add_property("age",26)
n_3.add_property("pos_x",21)
n_3.add_property("pos_y",11)

n_4=Node(4)
n_4.add_property("name","C")
n_4.add_property("age",26)
n_4.add_property("pos_x",-20)
n_4.add_property("pos_y",11)

n_5=Node(5)
n_5.add_property("name","F")
n_5.add_property("age",26)
n_5.add_property("pos_x",-22)
n_5.add_property("pos_y",11)

e_1=Edge(n_1,n_2,"A")
e_2=Edge(n_1,n_3,"A")
e_3=Edge(n_2,n_4,"A")
e_4=Edge(n_3,n_4,"A")
e_5=Edge(n_4,n_5,"A")

n_1.add_edge(e_1)
n_1.add_edge(e_2)
n_2.add_edge(e_3)
n_3.add_edge(e_4)
n_4.add_edge(e_5)

#n_1 is start of sample facebook graph



def test1(): #MH distance query.
    model=gp.Model()
    model.Params.OutputFlag = 0

    res=model.addVar(name="res")
    dif_x=model.addVar(name="dif_x")
    dif_y=model.addVar(name="dif_y")


    expr1=gp.LinExpr(res-9)
    expr2=gp.LinExpr(res-dif_x-dif_y)
    expr3=gp.LinExpr((-21)-dif_x)
    expr4=gp.LinExpr(dif_x+(-21))
    expr5=gp.LinExpr(11-dif_y)
    expr6=gp.LinExpr(dif_y+11)
    expr7=gp.LinExpr(11)
    expr8=gp.LinExpr(11)
    expr9=gp.LinExpr(-21)
    expr10=gp.LinExpr(-21)
    expr11=gp.LinExpr(39/2+7)

    index_expr=[0]*12
    index_expr[0]=(expr1,"<=","0",False,'w')
    index_expr[1]=(expr2,"==","0",False,'w')
    index_expr[2]=(expr3,"==","pos_x",False,'w')
    index_expr[3]=(expr4,"==","pos_x",False,'w')
    index_expr[4]=(expr5,"==","pos_y",False,'w')
    index_expr[5]=(expr6,"==","pos_y",False,'w')
    index_expr[6]=(expr7,">=","pos_y",False,'w')
    index_expr[7]=(expr8,"<=","pos_y",False,'w')
    index_expr[8]=(expr9,"<=","pos_x",False,'w')
    index_expr[9]=(expr10,">=","pos_x",False,'w')
    index_expr[10]=(expr11,"<=","age",False,'w')


    start_tuple_gp=('!','!','?','?','?','?','?','?','?','?','?')

    yt_mh_q1=State(1,False)
    yt_mh_q2=State(2,True)

    yt_mh_t1=Transition(yt_mh_q1,yt_mh_q1,"A",[],[])
    yt_mh_t2=Transition(yt_mh_q1,yt_mh_q2,"A",[0,1,2,4,6,9,10],[])
    yt_mh_t3=Transition(yt_mh_q1,yt_mh_q2,"A",[0,1,2,5,7,9,10],[])
    yt_mh_t4=Transition(yt_mh_q1,yt_mh_q2,"A",[0,1,3,4,6,8,10],[])
    yt_mh_t5=Transition(yt_mh_q1,yt_mh_q2,"A",[0,1,3,5,7,8,10],[])

    yt_mh_q1.add_transition(yt_mh_t1)
    yt_mh_q1.add_transition(yt_mh_t2)
    yt_mh_q1.add_transition(yt_mh_t3)
    yt_mh_q1.add_transition(yt_mh_t4)
    yt_mh_q1.add_transition(yt_mh_t5)

    print(time.time())
    start_time=time.time()
    start_test(model, nodes[0],yt_mh_q1,start_tuple_gp,[nodes[0]],index_expr)   #change here to n_1 (4 nodes), nodes[0] (5000 nodes), nodes_yt[0] (1million nodes).
    end_time=time.time()
    print(end_time-start_time)

#test1()

def test2():
    model=gp.Model()
    model.Params.OutputFlag = 0
    

    p_min=model.addVar(name="p_min")
    p_max=model.addVar(name="p_max")
    
    expr1=gp.LinExpr(p_min)
    expr2=gp.LinExpr(p_max)
    expr3=gp.LinExpr(p_min-p_max)
    expr4=gp.LinExpr(p_max-p_min-2)

    index_expr=[0]*4
    index_expr[0]=(expr1,"<=","val",False,'e')
    index_expr[1]=(expr2,">=","val",False,'e')
    index_expr[2]=(expr3,"<=","0",False,'e')
    index_expr[3]=(expr4,"<=","0",False,'e')

    start_tuple_gp=('?','?','!','!')

    aut2_q_1=State(1,True)

    aut2_t_1=Transition(aut2_q_1,aut2_q_1,"val",[0,1,2,3],[]) 
    aut2_q_1.add_transition(aut2_t_1)
    print(time.time())
    start_time=time.time()
    start_test(model, nodes[0],aut2_q_1,start_tuple_gp,[nodes[0]],index_expr) #Try here also instead of qla_s_1, nodes[0]

    end_time=time.time()
    print(end_time-start_time)

#test2()






model_test=gp.Model()
model_test.Params.OutputFlag = 0
#Negative triangle test query:
def test3():
    
    model2=gp.Model()
    model2.Params.OutputFlag = 0
    
    nt_q_1=State(1,False)#Repeat or decide to take
    nt_q_2=State(2,False)#First edge taken
    nt_q_3=State(3,False)#Second edge taken
    nt_q_4=State(4,True)#Third edge taken
 
    #Add the transitions now to the automaton.
 
    nt_x_1=model2.addVar(lb=-gp.GRB.INFINITY,name="nt_x_1")
    nt_x_2=model2.addVar(lb=-gp.GRB.INFINITY,name="nt_x_2")
    nt_x_3=model2.addVar(lb=-gp.GRB.INFINITY,name="nt_x_3")
    curr_id=model2.addVar(lb=-gp.GRB.INFINITY,name="curr_id")
    curr_id2=model2.addVar(lb=-gp.GRB.INFINITY,name="curr_id2")


    expr1=gp.LinExpr(nt_x_1)
    expr2=gp.LinExpr(curr_id)
    expr3=gp.LinExpr(nt_x_2)
    expr4=gp.LinExpr(nt_x_3)
    expr5=gp.LinExpr(curr_id2)
    expr6=gp.LinExpr(nt_x_1+nt_x_2+nt_x_3)
    expr7=gp.LinExpr(curr_id- curr_id2)

    index_expr=[0]*7
    index_expr[0]=(expr1,"==","val",False,'e')
    index_expr[1]=(expr2,"==","id",False,'a')
    index_expr[2]=(expr3,"==","val",False,'e')
    index_expr[3]=(expr4,"==","val",False,'e')
    index_expr[4]=(expr5,"==","id",False,'w')
    index_expr[5]=(expr6,"<=","0",False,'e')
    index_expr[6]=(expr7,"==","0",False,'e')

    start_tuple_gp=('?','?','?','?','?','!','!')


    nt_t_1=Transition(nt_q_1,nt_q_1,"A",[],[])
    nt_t_2=Transition(nt_q_1,nt_q_2,"A",[0,1],[])
    nt_t_3=Transition(nt_q_2,nt_q_3,"A",[2],[])
    nt_t_4=Transition(nt_q_3,nt_q_4,"A",[3,4,5,6],[])


    nt_q_1.add_transition(nt_t_1)
    nt_q_1.add_transition(nt_t_2)
    nt_q_2.add_transition(nt_t_3)
    nt_q_3.add_transition(nt_t_4)

    start_time=time.time()
    start_test(model2, nt_n_1,nt_q_1,start_tuple_gp,[nt_n_1],index_expr) #Try here also instead of qla_s_1, nodes[0]

    end_time=time.time()
    print(end_time-start_time)

#test3()
#Central path query
def test4():
    model=gp.Model()
    model.Params.OutputFlag = 0
    center_x=model.addVar(lb=-gp.GRB.INFINITY,name="center_x")
    center_y=model.addVar(lb=-gp.GRB.INFINITY,name="center_y")



    expr1=gp.LinExpr(center_x+center_y-10)#<=pos_x+pos_y
    expr2=gp.LinExpr(-center_x+center_y-10)#<=pos_y-pos_x
    expr3=gp.LinExpr(center_x-center_y-10)#<=pos_x-pos_y
    expr4=gp.LinExpr(-center_x-center_y-10)#<=-pos_x-pos_y
    index_expr=[0]*8
    #Now complex expressions.

    index_expr[0]=(expr1,"<=","pos_x+pos_y",True,[("pos_x",'a'),("pos_y",'a')])
    index_expr[1]=(expr2,"<=","pos_y-pos_x",True,[("pos_x",'a'),("pos_y",'a')])
    index_expr[2]=(expr3,"<=","pos_x-pos_y",True,[("pos_x",'a'),("pos_y",'a')])
    index_expr[3]=(expr4,"<=","-(pos_x+pos_y)",True,[("pos_x",'a'),("pos_y",'a')])

    index_expr[4]=(expr1,"<=","pos_x+pos_y",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[5]=(expr2,"<=","pos_y-pos_x",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[6]=(expr3,"<=","pos_x-pos_y",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[7]=(expr4,"<=","-(pos_x+pos_y)",True,[("pos_x",'w'),("pos_y",'w')])

    start_tuple_gp=('?','?','?','?','?','?','?','?')

    yt_mh_q1=State(1,True)
    yt_mh_t2=Transition(yt_mh_q1,yt_mh_q1,"A",[0,1,2,3,4,5,6,7],[])
 

    yt_mh_q1.add_transition(yt_mh_t2)


    start_time=time.time()
    start_test(model, nodes[0],yt_mh_q1,start_tuple_gp,[nodes[0]],index_expr)   #change here to n_1 (4 nodes), nodes[0] (5000 nodes), nodes_yt[0] (1million nodes).
    end_time=time.time()
    print(end_time-start_time)


#test4()

#Very important tradeoff between pruning, and s-t path queries, the less we can prune the easier the s-t path query becomes, natural duality.

def test5():
    #-21 ,11 coordinates of s.
    model=gp.Model()
    model.Params.OutputFlag = 0

    expr1=gp.LinExpr((-21)+(11)-9)#<=pos_x+pos_y
    #((centerx-pos_x) + (center_y -posy) <=9)
    expr2=gp.LinExpr(-(-21)+(11)-9)#<=pos_y-pos_x
    #(pos_x-center_x)+(centery-pos_y)<=9
    expr3=gp.LinExpr((-21)-(11)-9)#<=pos_x-pos_y

    expr4=gp.LinExpr(-(-21)-(11)-9)#<=-pos_x-pos_y
    index_expr=[0]*4
    #Now complex expressions.

    index_expr[0]=(expr1,"<=","pos_x+pos_y",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[1]=(expr2,"<=","pos_y-pos_x",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[2]=(expr3,"<=","pos_x-pos_y",True,[("pos_x",'w'),("pos_y",'w')])
    index_expr[3]=(expr4,"<=","-(pos_x+pos_y)",True,[("pos_x",'w'),("pos_y",'w')])

    start_tuple_gp=('?','?','?','?')

    yt_mh_q1=State(1,False)
    yt_mh_q2=State(2,True)
    yt_mh_t1=Transition(yt_mh_q1,yt_mh_q1,"A",[],[])
    yt_mh_t2=Transition(yt_mh_q1,yt_mh_q2,"A",[0,1,2,3],[])
 
    yt_mh_q1.add_transition(yt_mh_t1)
    yt_mh_q1.add_transition(yt_mh_t2)



    start_time=time.time()
    start_test(model, nodes[0],yt_mh_q1,start_tuple_gp,[nodes[0]],index_expr)   #change here to n_1 (4 nodes), nodes[0] (5000 nodes), nodes_yt[0] (1million nodes).
    end_time=time.time()
    print(end_time-start_time)

#test5()

#Subset sum toy, example for Algorithm 1
# ss_1=Node(1)
# ss_2=Node(2)
# ss_3=Node(3)
# ss_4=Node(4)
# ss_5=Node(5)
# ss_6=Node(6)
# ss_7=Node(7)

# ss_1.add_property("val",3)
# ss_2.add_property("val",8)
# ss_3.add_property("val",2)
# ss_4.add_property("val",10)
# ss_5.add_property("val",4)
# ss_e_1=Edge(ss_1,ss_2,"next")
# ss_e_2=Edge(ss_2,ss_3,"next")
# ss_e_3=Edge(ss_3,ss_4,"next")
# ss_e_4=Edge(ss_4,ss_5,"next")
# ss_e_5=Edge(ss_5,ss_6,"next")
# ss_e_6=Edge(ss_6,ss_7,"next")

# ss_1.add_edge(ss_e_1)
# ss_2.add_edge(ss_e_2)
# ss_3.add_edge(ss_e_3)
# ss_4.add_edge(ss_e_4)
# ss_5.add_edge(ss_e_5)
# ss_6.add_edge(ss_e_6)

# ss_q_1=State(1,False)
# ss_q_2=State(2,False)
# ss_q_3=State(3,False)
# ss_q_4=State(4,False)
# ss_q_5=State(5,False)
# ss_q_6=State(6,False)
# ss_q_7=State(7,True)


# x_1=Int('x_1')
# x_2=Int('x_2')
# x_3=Int('x_3')
# x_4=Int('x_4')
# x_5=Int('x_5')
# val=Int('val')

# ss_t_1=Transition(ss_q_1,ss_q_2,"next",x_1==0,[])
# ss_t_12=Transition(ss_q_1,ss_q_2,"next",x_1==val,[(val,"from","int")])

# ss_q_1.add_transition(ss_t_1)
# ss_q_1.add_transition(ss_t_12)

# ss_t_2=Transition(ss_q_2,ss_q_3,"next",x_2==0,[])
# ss_t_22=Transition(ss_q_2,ss_q_3,"next",x_2==val,[(val,"from","int")])
# ss_q_2.add_transition(ss_t_2)
# ss_q_2.add_transition(ss_t_22)

# ss_t_3=Transition(ss_q_3,ss_q_4,"next",x_3==0,[])
# ss_t_32=Transition(ss_q_3,ss_q_4,"next",x_3==val,[(val,"from","int")])
# ss_q_3.add_transition(ss_t_3)
# ss_q_3.add_transition(ss_t_32)

# ss_t_4=Transition(ss_q_4,ss_q_5,"next",x_4==0,[])
# ss_t_42=Transition(ss_q_4,ss_q_5,"next",x_4==val,[(val,"from","int")])
# ss_q_4.add_transition(ss_t_4)
# ss_q_4.add_transition(ss_t_42)

# ss_t_5=Transition(ss_q_5,ss_q_6,"next",x_5==0,[])
# ss_t_52=Transition(ss_q_5,ss_q_6,"next",x_5==val,[(val,"from","int")])
# ss_q_5.add_transition(ss_t_5)
# ss_q_5.add_transition(ss_t_52)

# ss_t_6=Transition(ss_q_6,ss_q_7,"next",(x_1 +x_2 +x_3 +x_4 + x_5)==9,[])

# ss_q_6.add_transition(ss_t_6)
def test7():
    random_endpoint= random.choice(nodes)
    model=gp.Model()
    model.Params.OutputFlag = 0
    

    p_min=model.addVar(name="p_min")
    p_max=model.addVar(name="p_max")
    
    expr1=gp.LinExpr(p_min)
    expr2=gp.LinExpr(p_max)
    expr3=gp.LinExpr(p_min-p_max)
    expr4=gp.LinExpr(p_max-p_min-0)

    index_expr=[0]*4
    index_expr[0]=(expr1,"<=","val",False,'e')
    index_expr[1]=(expr2,">=","val",False,'e')
    index_expr[2]=(expr3,"<=","0",False,'e')
    index_expr[3]=(expr4,"<=","0",False,'e')

    start_tuple_gp=('?','?','!','!')

    aut2_q_1=State(1,True)

    aut2_t_1=Transition(aut2_q_1,aut2_q_1,"val",[0,1,2,3],[]) 
    aut2_q_1.add_transition(aut2_t_1)
    print(time.time())
    start_time=time.time()
    start_test_endpoints(model, nodes[0],aut2_q_1,start_tuple_gp,[nodes[0]],index_expr,random_endpoint) #Try here also instead of qla_s_1, nodes[0]

    end_time=time.time()
    print(end_time-start_time)

#test7()