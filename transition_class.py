#Transition can have many formulas.
class Transition: #Transitions of the automaton
    def __init__(self,state1,state2,label,formula, parameters):
        self.state1=state1#from
        self.state2=state2#to
        self.label=label
        self.formula=formula # z3 expression using parameters and free variables.
        self.parameters=parameters #list of tuples of the form [(x,"to", "int") (y,"edge","string") ...] 
