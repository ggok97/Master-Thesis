#An edge can have many properties.
class Edge: #Edge in a graph 
    def __init__(self,node1,node2,name):
        self.node1=node1    #from
        self.node2=node2    #to
        self.name=name
        self.properties={}
    def add_property(self,k,val):
        self.properties[k]=val