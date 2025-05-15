import tkinter as tk
from tkinter import messagebox
from graph import *
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import os

class GraphInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Project Interface')
        self.root.minsize(500, 500)  # Set minimum window size
        
        self.graph = None
        self.setup_ui()
        
    def setup_ui(self):
        # Frames
        self.frame_buttons = tk.LabelFrame(self.root, text='Buttons')
        self.frame_buttons.pack(fill='x', padx=10, pady=10)
        
        self.frame_images = tk.LabelFrame(self.root, text='Graph')
        self.frame_images.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        self.button_new = tk.Button(self.frame_buttons, text='New Graph', command=self.new_graph)
        self.button_new.pack(side='left', padx=5, pady=5)
        
        self.button_load = tk.Button(self.frame_buttons, text='Load file', command=self.load_file)
        self.button_load.pack(side='left', padx=5, pady=5)
        
        self.button_save = tk.Button(self.frame_buttons, text='Save Graph', command=self.save_graph)
        self.button_save.pack(side='left', padx=5, pady=5)
        
        self.button_show = tk.Button(self.frame_buttons, text='Show', command=self.show_graph)
        self.button_show.pack(side='left', padx=5, pady=5)
        
        self.button_add = tk.Button(self.frame_buttons, text='Add Element', command=self.add_element)
        self.button_add.pack(side='left', padx=5, pady=5)
        
        self.button_remove = tk.Button(self.frame_buttons, text='Remove Element', command=self.remove_element)
        self.button_remove.pack(side='left', padx=5, pady=5)
        
        # Label for graph selection
        self.label_selected = tk.Label(self.frame_buttons, text='Graph selected: None yet')
        self.label_selected.pack(side='left', padx=5, pady=5)
        
        # Image display
        self.image_label = tk.Label(self.frame_images)
        self.image_label.pack(fill='both', expand=True)
        
    def new_graph(self):
        # Ask for confirmation if there's an existing graph
        if self.graph and self.graph.list_of_nodes:
            if not messagebox.askyesno("Confirm", "Creating a new graph will discard the current one. Continue?"):
                return
        
        # Create new empty graph
        self.graph = Graph()
        self.label_selected.config(text='Graph selected: New Graph')
        messagebox.showinfo("Success", "New empty graph created")
        
    def load_file(self):
        window = tk.Toplevel(self.root)
        window.title("Load File")
        window.geometry('300x200')
        window.transient(self.root)  # Make window modal
        
        def load_example():
            from test_graph import G
            self.graph = G
            self.label_selected.config(text='Graph selected: Example')
            window.destroy()
            
        def load_invented():
            from test_graph import G2
            self.graph = G2
            self.label_selected.config(text='Graph selected: Invented')
            window.destroy()
            
        def load_data():
            try:
                gd = Graph()
                ImportData(gd)
                if gd.list_of_nodes:  # Check if data was actually loaded
                    self.graph = gd
                    self.label_selected.config(text='Graph selected: Imported data')
                else:
                    messagebox.showwarning("Warning", "No data was loaded from the file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            window.destroy()
        
        tk.Button(window, text='Load example graph', command=load_example).pack(pady=10)
        tk.Button(window, text='Load invented graph', command=load_invented).pack(pady=10)
        tk.Button(window, text='Import Data', command=load_data).pack(pady=10)
        
    def add_element(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        window = tk.Toplevel(self.root)
        window.title("Add Element")
        window.geometry('300x400')
        window.transient(self.root)
        
        # Node addition
        node_frame = tk.LabelFrame(window, text="Add Node")
        node_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(node_frame, text="Name:").pack()
        name_entry = tk.Entry(node_frame)
        name_entry.pack()
        
        tk.Label(node_frame, text="X coordinate:").pack()
        x_entry = tk.Entry(node_frame)
        x_entry.pack()
        
        tk.Label(node_frame, text="Y coordinate:").pack()
        y_entry = tk.Entry(node_frame)
        y_entry.pack()
        
        def add_node():
            try:
                name = name_entry.get().strip()
                x = float(x_entry.get())
                y = float(y_entry.get())
                
                if not name or len(name) != 1:
                    raise ValueError("Node name must be a single character")
                    
                node = Node(name, x, y)
                if AddNode(self.graph, node):
                    messagebox.showinfo("Success", f"Node {name} added successfully")
                    self.show_graph()  # Refresh the display
                else:
                    messagebox.showwarning("Warning", f"Node {name} already exists")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(node_frame, text="Add Node", command=add_node).pack(pady=5)
        
        # Segment addition
        segment_frame = tk.LabelFrame(window, text="Add Segment")
        segment_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(segment_frame, text="Segment name (2 chars):").pack()
        seg_name_entry = tk.Entry(segment_frame)
        seg_name_entry.pack()
        
        tk.Label(segment_frame, text="Origin node:").pack()
        origin_entry = tk.Entry(segment_frame)
        origin_entry.pack()
        
        tk.Label(segment_frame, text="Destination node:").pack()
        dest_entry = tk.Entry(segment_frame)
        dest_entry.pack()
        
        def add_segment():
            try:
                seg_name = seg_name_entry.get().strip()
                origin = origin_entry.get().strip()
                dest = dest_entry.get().strip()
                
                if len(seg_name) != 2:
                    raise ValueError("Segment name must be 2 characters")
                    
                if not GetNodeByName(self.graph, origin):
                    raise ValueError(f"Origin node {origin} does not exist")
                if not GetNodeByName(self.graph, dest):
                    raise ValueError(f"Destination node {dest} does not exist")
                    
                AddSegment(self.graph, seg_name, origin, dest)
                messagebox.showinfo("Success", f"Segment {seg_name} added successfully")
                self.show_graph()  # Refresh the display
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(segment_frame, text="Add Segment", command=add_segment).pack(pady=5)
        
    def remove_element(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        window = tk.Toplevel(self.root)
        window.title("Remove Element")
        window.geometry('300x400')
        window.transient(self.root)
        
        # Node removal
        node_frame = tk.LabelFrame(window, text="Remove Node")
        node_frame.pack(fill='x', padx=5, pady=5)
        
        # Create a dropdown with existing nodes
        node_var = tk.StringVar(window)
        node_names = [node.name for node in self.graph.list_of_nodes]
        if not node_names:
            node_names = ["No nodes available"]
            node_var.set(node_names[0])
        else:
            node_var.set(node_names[0])
            
        node_dropdown = tk.OptionMenu(node_frame, node_var, *node_names)
        node_dropdown.pack(pady=5)
        
        def remove_node():
            try:
                node_name = node_var.get()
                if node_name == "No nodes available":
                    messagebox.showwarning("Warning", "No nodes available to remove")
                    return
                    
                node = GetNodeByName(self.graph, node_name)
                if not node:
                    raise ValueError(f"Node {node_name} not found")
                
                # Remove all segments connected to this node
                segments_to_remove = []
                for segment in self.graph.list_of_segments:
                    if segment.origin_node == node or segment.destination_node == node:
                        segments_to_remove.append(segment)
                
                for segment in segments_to_remove:
                    self.graph.list_of_segments.remove(segment)
                
                # Remove node from other nodes' neighbor lists
                for other_node in self.graph.list_of_nodes:
                    if node in other_node.list_of_neighbors:
                        other_node.list_of_neighbors.remove(node)
                
                # Remove the node
                self.graph.list_of_nodes.remove(node)
                
                messagebox.showinfo("Success", f"Node {node_name} and its connected segments removed successfully")
                self.show_graph()  # Refresh the display
                window.destroy()  # Close the window after successful removal
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(node_frame, text="Remove Node", command=remove_node).pack(pady=5)
        
        # Segment removal
        segment_frame = tk.LabelFrame(window, text="Remove Segment")
        segment_frame.pack(fill='x', padx=5, pady=5)
        
        # Create a dropdown with existing segments
        segment_var = tk.StringVar(window)
        segment_names = [f"{seg.name} ({seg.origin_node.name}-{seg.destination_node.name})" 
                        for seg in self.graph.list_of_segments]
        if not segment_names:
            segment_names = ["No segments available"]
            segment_var.set(segment_names[0])
        else:
            segment_var.set(segment_names[0])
            
        segment_dropdown = tk.OptionMenu(segment_frame, segment_var, *segment_names)
        segment_dropdown.pack(pady=5)
        
        def remove_segment():
            try:
                segment_info = segment_var.get()
                if segment_info == "No segments available":
                    messagebox.showwarning("Warning", "No segments available to remove")
                    return
                    
                # Extract segment name from the dropdown text (format: "name (origin-destination)")
                segment_name = segment_info.split(" ")[0]
                
                # Find and remove the segment
                segment_to_remove = None
                for segment in self.graph.list_of_segments:
                    if segment.name == segment_name:
                        segment_to_remove = segment
                        break
                
                if not segment_to_remove:
                    raise ValueError(f"Segment {segment_name} not found")
                
                # Remove the segment from the graph
                self.graph.list_of_segments.remove(segment_to_remove)
                
                # Remove the destination node from origin node's neighbors
                if segment_to_remove.destination_node in segment_to_remove.origin_node.list_of_neighbors:
                    segment_to_remove.origin_node.list_of_neighbors.remove(segment_to_remove.destination_node)
                
                messagebox.showinfo("Success", f"Segment {segment_name} removed successfully")
                self.show_graph()  # Refresh the display
                window.destroy()  # Close the window after successful removal
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(segment_frame, text="Remove Segment", command=remove_segment).pack(pady=5)
        
    def show_graph(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        try:
            Plot(self.graph)  # Save the plot
            
            if os.path.exists('Figure.png'):
                # Calculate aspect ratio preserving size
                img = Image.open('Figure.png')
                width, height = img.size
                max_size = 400  # Maximum dimension
                
                # Calculate new dimensions maintaining aspect ratio
                if width > height:
                    new_width = min(width, max_size)
                    new_height = int(height * (new_width / width))
                else:
                    new_height = min(height, max_size)
                    new_width = int(width * (new_height / height))
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference
            else:
                messagebox.showerror("Error", "Failed to generate graph image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display graph: {str(e)}")
            
    def save_graph(self):
        if not self.graph or not self.graph.list_of_nodes:
            messagebox.showwarning("Warning", "No graph to save")
            return
            
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Graph"
            )
            
            if not file_path:  # User cancelled the save dialog
                return
                
            with open(file_path, 'w') as f:
                # First write all nodes
                for node in self.graph.list_of_nodes:
                    f.write(f"{node.name} {int(node.coordinate_x)} {int(node.coordinate_y)}\n")
                
                # Then write all segments
                for segment in self.graph.list_of_segments:
                    f.write(f"{segment.name} {segment.origin_node.name} {segment.destination_node.name}\n")
                    
            messagebox.showinfo("Success", f"Graph saved successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {str(e)}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GraphInterface()
    app.run()
