import tkinter as tk
from tkinter import messagebox
import matplotlib as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from node import *
from segment import *
from graph import *
  


def ExampleGraph ():
    G= Graph()
    AddNode(G, Node("A",1,20))
    AddNode(G, Node("B",8,17))
    AddNode(G, Node("C",15,20))
    AddNode(G, Node("D",18,15))
    AddNode(G, Node("E",2,4))
    AddNode(G, Node("F",6,5))
    AddNode(G, Node("G",12,12))
    AddNode(G, Node("H",10,3))
    AddNode(G, Node("I",19,1))
    AddNode(G, Node("J",13,5))
    AddNode(G, Node("K",3,15))
    AddNode(G, Node("L",4,10))
    AddSegment(G, "AB","A","B")
    AddSegment(G, "AE","A","E")
    AddSegment(G, "AK","A","K")
    AddSegment(G, "BA","B","A")
    AddSegment(G, "BC","B","C")
    AddSegment(G, "BF","B","F")
    AddSegment(G, "BK","B","K")
    AddSegment(G, "BG","B","G")
    AddSegment(G, "CD","C","D")
    AddSegment(G, "CG","C","G")
    AddSegment(G, "DG","D","G")
    AddSegment(G, "DH","D","H")
    AddSegment(G, "DI","D","I")
    AddSegment(G, "EF","E","F")
    AddSegment(G, "FL","F","L")
    AddSegment(G, "GB","G","B")
    AddSegment(G, "GF","G","F")
    AddSegment(G, "GH","G","H")
    AddSegment(G, "ID","I","D")
    AddSegment(G, "IJ","I","J")
    AddSegment(G, "JI","J","I")
    AddSegment(G, "KA","K","A")
    AddSegment(G, "KL","K","L")
    AddSegment(G, "LK","L","K")
    AddSegment(G, "LF","L","F")
    return G
G = ExampleGraph()
g = Graph()

def InterfaceGraph():
    ####### base ######
    root = tk.Tk()
    root.geometry('700x300')
    root.title('Interface')
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=3)
    root.rowconfigure(2, weight=3)
    # Select
    select_frame = tk.LabelFrame(root, text = 'Select:')
    select_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    select_frame.rowconfigure(0, weight=1)
    select_frame.rowconfigure(1, weight=1)
    select_frame.columnconfigure(0, weight=1)
    select_frame.columnconfigure(1, weight=1)
    select_frame.columnconfigure(2, weight=1)

    tk.Label(select_frame, text="File Path:").grid(row=0, column=0, sticky=tk.W, padx=5)
    tk.Label(select_frame, text="Node:").grid(row=0, column=1, sticky=tk.W, padx=5)
    tk.Label(select_frame, text="Segment:").grid(row=0, column=2, sticky=tk.W, padx=5)

    entryFile = tk.Entry(select_frame)
    entryFile.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    entryNode = tk.Entry(select_frame)
    entryNode.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    entrySegment = tk.Entry(select_frame)
    entrySegment.grid(row=1, column=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    # paths
    paths_frame = tk.LabelFrame(root, text = 'Paths')
    paths_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    paths_frame.rowconfigure(0, weight=1)
    paths_frame.columnconfigure(0, weight=1)
    paths_frame.columnconfigure(1, weight=1)

    reachability = tk.Button(paths_frame, text = 'Reachability', command=lambda: PlotReachability(g, Reachability(g, f'{entryNode.get()}')))
    reachability.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    shortest_path = tk.Button(paths_frame, text = 'Shortest Path', command=lambda: PlotPath(g, FindShortestPath(g, DetectEntry(entryNode.get())[0], DetectEntry(entryNode.get())[1])))
    shortest_path.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    # example graph
    example_graph_frame = tk.LabelFrame(root, text = 'Example Graph')
    example_graph_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    example_graph_frame.rowconfigure(0, weight=1)
    example_graph_frame.columnconfigure(0, weight=1)
    example_graph_frame.columnconfigure(1, weight=1)

    button1 = tk.Button(example_graph_frame, text = 'Show Example Graph', command=lambda: Plot(G))
    button1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    button2 = tk.Button(example_graph_frame, text = 'Show Example Node Neighbors', command=lambda: PlotNode(G, 'C'))
    button2.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    # Load Graph
    load_graph_frame = tk.LabelFrame(root, text = 'Load Graph')
    load_graph_frame.grid(row=1, rowspan=2, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    
    load_graph_frame.rowconfigure(0, weight=1)
    load_graph_frame.rowconfigure(1, weight=1)
    load_graph_frame.columnconfigure(0, weight=1)
    load_graph_frame.columnconfigure(1, weight=1)
    load_graph_frame.columnconfigure(2, weight=1)

    def loadfile():
       l = LoadFile(entryFile.get())
       globals()['g'] = l

    Load_File = tk.Button(load_graph_frame, text = 'Load File', command=lambda: loadfile())
    Load_File.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    GraphNode = tk.Button(load_graph_frame, text = 'Show Node Neighbors', command=lambda: PlotNode(g, entryNode.get()))
    GraphNode.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    newgraph = tk.Button(load_graph_frame, text = 'New Graph', command=lambda: NewGraph(g))
    newgraph.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    savegraph = tk.Button(load_graph_frame, text = 'Save Graph', command=lambda: SaveGraph(g))
    savegraph.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    ShowGraph = tk.Button(load_graph_frame, text = 'Show Graph', command=lambda: Plot(g))
    ShowGraph.grid(row=1, column=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    #Graph Editing
    editing_frame = tk.LabelFrame(root, text = 'Edit Graph')
    editing_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    
    editing_frame.rowconfigure(0, weight=1)
    editing_frame.columnconfigure(0, weight=1)
    editing_frame.columnconfigure(1, weight=1)
    editing_frame.columnconfigure(2, weight=1)
    editing_frame.columnconfigure(3, weight=1)

    addnode = tk.Button(editing_frame, text = 'Add Node', command=lambda: AddNode(g, DetectEntry(entryNode.get())))
    addnode.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    deleteNode = tk.Button(editing_frame, text = 'Delete Node', command=lambda: DeleteNode(g, entryNode.get()))
    deleteNode.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    addsegment = tk.Button(editing_frame, text = 'Add Segment', command=lambda: AddSegment(g, DetectEntry(entrySegment.get())[0], DetectEntry(entrySegment.get())[1], DetectEntry(entrySegment.get())[2]))
    addsegment.grid(row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
    
    deletesegment = tk.Button(editing_frame, text = 'Delete Segment', command=lambda: DeleteSegment(g, entrySegment.get()))
    deletesegment.grid(row=0, column=3, padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

    root.mainloop()

InterfaceGraph()