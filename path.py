from node import *
from graph import *
import matplotlib.pyplot as plt 
import numpy as np

class Path:
    def __init__ (self, origin):
        self.nodes = [origin]
        self.cost = 0.0

def AddNodeToPath(path, node): #MIRAR
    add = True
    for a in path.nodes:
        if a == node:
            add = False
            break
    if add == True:
        last = path.nodes[-1]
        path.cost += round(Distance(last, node), 2)
        path.nodes.append(node)
    return add

def ContainsNode (p, node):
    for a in p.nodes:
        if a == node:
            return True
    return False

def CostToNode (p, node):
    total = 0.0
    i = 0
    if node not in p.nodes:
        return -1
    while i < len(p.nodes)-1 :
        a = p.nodes[i]
        b = p.nodes[i + 1]
        if a == node:
            break
        else:
            total += round(Distance(a, b), 2)
        i += 1
    return total

def PlotPath (g, p):
    for n in g.node:
        plt.plot(n.x, n.y, 'o', color='gray', markersize=3)
        plt.text(n.x, n.y, f'{n.name}', fontsize=8, color='black')

    for n in p.nodes:
        plt.plot(n.x, n.y, 'o', color='blue', markersize=5)
    
    for i in range(len(p.nodes) - 1):
        origin = p.nodes[i]
        destination = p.nodes[i+1]
        for s in g.segment:
            if s.origin == origin and s.destination == destination or s.origin == destination and s.destination == origin:
                plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y,
                           head_width=0.2, head_length=0.3, fc='blue', ec='blue', linewidth = 2, length_includes_head=True)
                midx = (s.origin.x + s.destination.x) / 2
                midy = (s.origin.y + s.destination.y) / 2
                plt.text(midx, midy, f'{s.cost} km', fontsize=8, color ='black')
            else:
                plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y, 
                          head_width=0.2, head_length=0.3, fc='gray', ec='gray', linewidth = 0.5, length_includes_head=True)
                midx = (s.origin.x + s.destination.x) / 2
                midy = (s.origin.y + s.destination.y) / 2
                plt.text(midx, midy, f'{s.cost} km', fontsize=8, color ='gray')
    
    plt.grid(color='grey', linestyle='dashed', linewidth=0.5)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()