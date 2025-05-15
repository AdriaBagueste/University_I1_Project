import tkinter as tk
from tkinter import messagebox, ttk
from graph import *
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import os

class GraphInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Graph Project Interface')
        
        # Set larger initial window size
        self.root.minsize(1200, 800)  # Increased minimum window size
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size (80% of screen size, but not larger than 1600x1000)
        window_width = min(int(screen_width * 0.8), 1600)
        window_height = min(int(screen_height * 0.8), 1000)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure ttk styles
        self.setup_styles()
        
        self.graph = None
        self.setup_ui()
        
    def setup_styles(self):
        """Configure ttk styles for consistent look"""
        style = ttk.Style()
        
        # Configure button style
        style.configure('Custom.TButton', 
                       padding=(10, 5),  # (horizontal, vertical) padding
                       width=15)
        
        # Configure dialog button style
        style.configure('Dialog.TButton',
                       padding=(20, 5),  # Wider padding for dialog buttons
                       width=20)
        
        # Configure label frame style
        style.configure('Custom.TLabelframe', padding=5)
        style.configure('Custom.TLabelframe.Label', padding=5)
        
        # Configure label style
        style.configure('Custom.TLabel', padding=5)
        
        # Configure frame style with padding
        style.configure('Padded.TFrame', padding=10)
        
    def create_modal_window(self, title, width, height):
        """Creates a modal window centered relative to the main window"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f'{width}x{height}')
        
        # Make window modal
        window.transient(self.root)
        window.grab_set()
        
        # Center the window relative to the main window
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        window.geometry(f'+{x}+{y}')
        
        # Prevent window resizing
        window.resizable(False, False)
        
        return window
        
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Frames with better styling
        self.frame_buttons = ttk.LabelFrame(main_container, text='Operations', style='Custom.TLabelframe')
        self.frame_buttons.pack(fill='x', pady=(0, 10))
        
        self.frame_images = ttk.LabelFrame(main_container, text='Graph Visualization', style='Custom.TLabelframe')
        self.frame_images.pack(fill='both', expand=True)
        
        # Create button container with grid layout
        button_container = ttk.Frame(self.frame_buttons)
        button_container.pack(fill='x', padx=5, pady=5)
        
        # Row 1 buttons
        self.button_new = ttk.Button(button_container, text='New Graph', command=self.new_graph, style='Custom.TButton')
        self.button_new.grid(row=0, column=0, padx=2, pady=2)
        
        self.button_load = ttk.Button(button_container, text='Load File', command=self.load_file, style='Custom.TButton')
        self.button_load.grid(row=0, column=1, padx=2, pady=2)
        
        self.button_save = ttk.Button(button_container, text='Save Graph', command=self.save_graph, style='Custom.TButton')
        self.button_save.grid(row=0, column=2, padx=2, pady=2)
        
        self.button_show = ttk.Button(button_container, text='Show Graph', command=self.show_graph, style='Custom.TButton')
        self.button_show.grid(row=0, column=3, padx=2, pady=2)
        
        # Row 2 buttons
        self.button_add = ttk.Button(button_container, text='Add Element', command=self.add_element, style='Custom.TButton')
        self.button_add.grid(row=1, column=0, padx=2, pady=2)
        
        self.button_remove = ttk.Button(button_container, text='Remove Element', command=self.remove_element, style='Custom.TButton')
        self.button_remove.grid(row=1, column=1, padx=2, pady=2)
        
        self.button_reachability = ttk.Button(button_container, text='Show Reachability', command=self.show_reachability, style='Custom.TButton')
        self.button_reachability.grid(row=1, column=2, padx=2, pady=2)
        
        self.button_shortest_path = ttk.Button(button_container, text='Find Shortest Path', command=self.find_shortest_path, style='Custom.TButton')
        self.button_shortest_path.grid(row=1, column=3, padx=2, pady=2)
        
        # Status label with better styling
        self.label_selected = ttk.Label(self.frame_buttons, text='Graph selected: None yet', style='Custom.TLabel')
        self.label_selected.pack(side='bottom', fill='x', padx=5, pady=5)
        
        # Image display with border
        self.image_frame = ttk.Frame(self.frame_images, borderwidth=2, relief="solid")
        self.image_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill='both', expand=True, padx=5, pady=5)
        
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
        window = self.create_modal_window("Load File", 300, 200)
        
        # Create a frame for buttons with padding
        button_frame = ttk.Frame(window, style='Padded.TFrame')
        button_frame.pack(fill='both', expand=True)
        
        # Create buttons with proper styling
        ttk.Button(button_frame, 
                  text='Load example graph', 
                  command=lambda: self.load_graph_type('example', window),
                  style='Dialog.TButton').pack(fill='x', pady=2)
                  
        ttk.Button(button_frame, 
                  text='Load invented graph', 
                  command=lambda: self.load_graph_type('invented', window),
                  style='Dialog.TButton').pack(fill='x', pady=2)
                  
        ttk.Button(button_frame, 
                  text='Import Data', 
                  command=lambda: self.load_graph_type('import', window),
                  style='Dialog.TButton').pack(fill='x', pady=2)
        
    def load_graph_type(self, graph_type, window):
        try:
            if graph_type == 'example':
                from test_graph import G
                self.graph = G
                self.label_selected.config(text='Graph selected: Example')
            elif graph_type == 'invented':
                from test_graph import G2
                self.graph = G2
                self.label_selected.config(text='Graph selected: Invented')
            else:  # import
                gd = Graph()
                ImportData(gd)
                if gd.list_of_nodes:
                    self.graph = gd
                    self.label_selected.config(text='Graph selected: Imported data')
                else:
                    messagebox.showwarning("Warning", "No data was loaded from the file")
                    return
                    
            self.show_graph()  # Refresh the display
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load graph: {str(e)}")
        
    def add_element(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        window = self.create_modal_window("Add Element", 400, 500)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Node tab
        node_frame = ttk.Frame(notebook, padding="10")
        notebook.add(node_frame, text="Add Node")
        
        # Create form with labels and entries
        ttk.Label(node_frame, text="Name (single character):").pack(fill='x', pady=(0, 5))
        name_entry = ttk.Entry(node_frame)
        name_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(node_frame, text="X coordinate:").pack(fill='x', pady=(0, 5))
        x_entry = ttk.Entry(node_frame)
        x_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(node_frame, text="Y coordinate:").pack(fill='x', pady=(0, 5))
        y_entry = ttk.Entry(node_frame)
        y_entry.pack(fill='x', pady=(0, 10))
        
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
                    self.show_graph()
                    window.destroy()
                else:
                    messagebox.showwarning("Warning", f"Node {name} already exists")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(node_frame, text="Add Node", command=add_node).pack(pady=10)
        
        # Segment tab
        segment_frame = ttk.Frame(notebook, padding="10")
        notebook.add(segment_frame, text="Add Segment")
        
        ttk.Label(segment_frame, text="Segment name (2 characters):").pack(fill='x', pady=(0, 5))
        seg_name_entry = ttk.Entry(segment_frame)
        seg_name_entry.pack(fill='x', pady=(0, 10))
        
        # Create dropdowns for node selection
        ttk.Label(segment_frame, text="Origin node:").pack(fill='x', pady=(0, 5))
        origin_var = tk.StringVar(segment_frame)
        node_names = [node.name for node in self.graph.list_of_nodes]
        origin_dropdown = ttk.Combobox(segment_frame, textvariable=origin_var, values=node_names, state="readonly")
        origin_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            origin_dropdown.set(node_names[0])
            
        ttk.Label(segment_frame, text="Destination node:").pack(fill='x', pady=(0, 5))
        dest_var = tk.StringVar(segment_frame)
        dest_dropdown = ttk.Combobox(segment_frame, textvariable=dest_var, values=node_names, state="readonly")
        dest_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            dest_dropdown.set(node_names[-1])
        
        def add_segment():
            try:
                seg_name = seg_name_entry.get().strip()
                origin = origin_var.get()
                dest = dest_var.get()
                
                if len(seg_name) != 2:
                    raise ValueError("Segment name must be 2 characters")
                    
                if not GetNodeByName(self.graph, origin):
                    raise ValueError(f"Origin node {origin} does not exist")
                if not GetNodeByName(self.graph, dest):
                    raise ValueError(f"Destination node {dest} does not exist")
                    
                AddSegment(self.graph, seg_name, origin, dest)
                messagebox.showinfo("Success", f"Segment {seg_name} added successfully")
                self.show_graph()
                window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(segment_frame, text="Add Segment", command=add_segment).pack(pady=10)
        
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
            Plot(self.graph)
            self.update_graph_display('Figure.png')
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
            
    def show_reachability(self):
        if not self.graph or not self.graph.list_of_nodes:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        window = self.create_modal_window("Show Reachability", 300, 200)
        
        # Create frame with padding
        frame = ttk.Frame(window, style='Padded.TFrame')
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Select start node:", style='Custom.TLabel').pack(fill='x')
        
        # Create dropdown with existing nodes
        node_var = tk.StringVar(window)
        node_names = [node.name for node in self.graph.list_of_nodes]
        node_dropdown = ttk.Combobox(frame, textvariable=node_var, values=node_names, state="readonly")
        node_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            node_dropdown.set(node_names[0])
        
        def show_reachable():
            try:
                node_name = node_var.get()
                node = GetNodeByName(self.graph, node_name)
                if not node:
                    raise ValueError(f"Node {node_name} not found")
                    
                PlotReachability(self.graph, node)
                
                # Display the reachable nodes
                reachable = GetReachableNodes(self.graph, node)
                reachable_names = [n.name for n in reachable]
                messagebox.showinfo("Reachable Nodes", 
                                  f"From node {node_name}, you can reach: {', '.join(reachable_names)}")
                
                # Update the display
                self.update_graph_display('Figure_3.png')
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame, text="Show Reachability", command=show_reachable, style='Dialog.TButton').pack(fill='x', pady=(10, 0))
        
    def find_shortest_path(self):
        if not self.graph or not self.graph.list_of_nodes:
            messagebox.showwarning("Warning", "Please load a graph first")
            return
            
        window = self.create_modal_window("Find Shortest Path", 300, 250)
        
        # Create frame with padding
        frame = ttk.Frame(window, style='Padded.TFrame')
        frame.pack(fill='both', expand=True)
        
        # Create dropdowns for origin and destination nodes
        ttk.Label(frame, text="Select origin node:", style='Custom.TLabel').pack(fill='x')
        origin_var = tk.StringVar(window)
        node_names = [node.name for node in self.graph.list_of_nodes]
        origin_dropdown = ttk.Combobox(frame, textvariable=origin_var, values=node_names, state="readonly")
        origin_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            origin_dropdown.set(node_names[0])
        
        ttk.Label(frame, text="Select destination node:", style='Custom.TLabel').pack(fill='x')
        dest_var = tk.StringVar(window)
        dest_dropdown = ttk.Combobox(frame, textvariable=dest_var, values=node_names, state="readonly")
        dest_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            dest_dropdown.set(node_names[-1])
        
        def find_path():
            try:
                origin_name = origin_var.get()
                dest_name = dest_var.get()
                
                origin = GetNodeByName(self.graph, origin_name)
                destination = GetNodeByName(self.graph, dest_name)
                
                if not origin or not destination:
                    raise ValueError("Selected nodes not found")
                    
                path = FindShortestPath(self.graph, origin, destination)
                
                if path:
                    # Plot the path
                    PlotPath(self.graph, path)
                    
                    # Show path information
                    path_nodes = [n.name for n in path.nodes]
                    messagebox.showinfo("Shortest Path Found", 
                                      f"Path: {' -> '.join(path_nodes)}\nTotal cost: {path.cost:.2f}")
                    
                    # Update the display
                    self.update_graph_display('Figure_2.png')
                else:
                    messagebox.showinfo("No Path Found", 
                                      f"There is no path from {origin_name} to {dest_name}")
                    
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame, text="Find Path", command=find_path, style='Dialog.TButton').pack(fill='x', pady=(10, 0))
        
    def update_graph_display(self, image_file):
        """Helper method to update the graph display with an image file"""
        if os.path.exists(image_file):
            img = Image.open(image_file)
            width, height = img.size
            
            # Get the current size of the image frame
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
            
            # Calculate maximum dimensions (90% of frame size)
            max_width = int(frame_width * 0.9)
            max_height = int(frame_height * 0.9)
            
            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = min(width, max_width)
                new_height = int(height * (new_width / width))
            else:
                new_height = min(height, max_height)
                new_width = int(width * (new_height / height))
            
            # Ensure minimum size
            new_width = max(new_width, 400)
            new_height = max(new_height, 300)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.config(image=photo)
            self.image_label.image = photo
            
            # Update the frame to fit the image
            self.image_frame.update_idletasks()
        else:
            messagebox.showerror("Error", f"Failed to load image: {image_file}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GraphInterface()
    app.run()
