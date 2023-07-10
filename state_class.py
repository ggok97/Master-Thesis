class State:
    def __init__(self,idd,final):
        self.idd=idd
        self.delta=[]#outgoing transitions
        self.final=final#boolean value : true -> final state , false ->not final state
    def add_transition(self, t):
        self.delta.append(t)    
    def __str__(self):
        return f"{self.idd}{self.final}"
    def __hash__(self):
        return self.idd
    def __eq__(self,other):
        return self.idd==other.idd