


import networkx as nx
import numpy as np


class CascadeWattsModel:

    def __init__(self, no_agents, net, threshold):
        self.no_agents = no_agents
        self.network = net
        self.threshold = threshold
        self.__agents = list(range(self.no_agents))
        self.state = np.zeros(self.no_agents, dtype = np.bool)
        self.in_equilibrium = False
        self.time= 0

        assert self.no_agents == self.network.number_of_nodes()


    def initalise_agents(self, p0):
        seed = np.random.randint(0, self.no_agents , int(p0*self.no_agents) )
        self.state[seed] = True

    def iterate(self):
        np.random.shuffle( self.__agents )

        self.no_changes = 0
        for _ag in self.__agents:
            if self.state[_ag] == True:
                continue
            if self.network.degree(_ag) == 0: continue
            no_active_neighs = np.sum( [self.state[_neigh] for _neigh in self.network.neighbors(_ag) ])
            if no_active_neighs/self.network.degree(_ag) > self.threshold[_ag]:
                self.state[_ag] = True
                self.no_changes += 1

        if self.no_changes == 0:
            self.in_equilibrium = True

        self.time += 1

    def get_cascade_size(self):
        return np.sum(self.state)



