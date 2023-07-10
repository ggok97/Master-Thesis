class Node: #Node in a graph:
    def __init__(self,idd):
        self.edges=[]
        self.idd=idd
        self.properties={}
    def add_property(self,k,val):#dictionary
        self.properties[k]=val

    def add_edge(self,e):
        self.edges.append(e)
    def __hash__(self):
        return self.idd
    def __eq__(self,other):
        return self.idd==other.idd