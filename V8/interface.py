import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from graph import *
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import os
from airSpace import AirSpace
import io
from navPoint import GetNavPointByNumber
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import traceback

# --- A320 Performance Data (Estimates) ---
A320_CRUISING_SPEED_KMPH = 840 # Typical cruising speed in km/h
A320_FUEL_CONSUMPTION_KGPH = 2086.5 # Typical fuel consumption in kg per hour (approx 4600 lbs/hr)

class AirspaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Explorer")
        # Start maximized
        self.root.state('zoomed')  # For Windows
        self.airspace = None
        self.airspace_image = None
        self.visualization_running = False  # Flag to track visualization state
        self.fig = None # Store matplotlib figure
        self.ax = None # Store matplotlib axes
        self.canvas = None # Store FigureCanvasTkAgg
        self.canvas_widget = None # Store Tkinter canvas widget
        self.toolbar = None # Store NavigationToolbar2Tk
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Add debouncing for resize events
        self._resize_timer = None
        self._last_resize_time = 0
        self._resize_delay = 250  # milliseconds
        
        self.current_graph_type = None # 'airspace' or 'simple'
        self.current_graph_data = None # Holds either AirSpace object or simple graph data (dict)
        
        # Store references to graph editing buttons and entries
        self.node_name_entry = None
        self.node_x_entry = None
        self.node_y_entry = None
        self.add_node_button = None
        self.remove_node_button = None
        self.segment_from_entry = None
        self.segment_to_entry = None
        self.add_segment_button = None
        self.remove_segment_button = None
        self.edit_status_text = None
        
        # Wait for window to be ready
        self.root.update_idletasks()
        
        self.setup_ui()
        
        # Bind resize event with debouncing
        self.root.bind('<Configure>', self.on_window_resize)
        
    def setup_styles(self):
        """Configure ttk styles for consistent look"""
        style = ttk.Style()
        
        # Configure styles
        style.configure('Custom.TButton', padding=(10, 5), width=15)
        style.configure('Dialog.TButton', padding=(20, 5), width=20)
        style.configure('Custom.TLabelframe', padding=5)
        style.configure('Custom.TLabelframe.Label', padding=5)
        style.configure('Custom.TLabel', padding=5)
        style.configure('Padded.TFrame', padding=10)

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        
        # Define colors
        bg_color = '#2b2b2b' if self.dark_mode else 'SystemButtonFace'
        fg_color = 'white' if self.dark_mode else 'black'
        entry_bg = '#404040' if self.dark_mode else 'white'
        
        # Update root window
        self.root.configure(bg=bg_color)
        
        # Update all widgets recursively
        def update_widget_colors(widget):
            try:
                # Handle ttk widgets using styles
                if isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                    widget.configure(style='Dark.TFrame' if self.dark_mode else 'Custom.TFrame')
                elif isinstance(widget, ttk.Label):
                    widget.configure(style='Dark.TLabel' if self.dark_mode else 'Custom.TLabel')
                elif isinstance(widget, ttk.Button):
                    widget.configure(style='Dark.TButton' if self.dark_mode else 'Custom.TButton')
                elif isinstance(widget, ttk.Entry):
                    widget.configure(style='Dark.TEntry' if self.dark_mode else 'Custom.TEntry')
                elif isinstance(widget, ttk.Combobox):
                    widget.configure(style='Dark.TCombobox' if self.dark_mode else 'Custom.TCombobox')
                elif isinstance(widget, ttk.Notebook):
                    widget.configure(style='Dark.TNotebook' if self.dark_mode else 'Custom.TNotebook')
                # Handle tk widgets using direct color configuration
                elif isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Label, tk.Button, tk.Entry, tk.Text, tk.Canvas)):
                    widget.configure(bg=bg_color, fg=fg_color)
                    if isinstance(widget, tk.Text):
                        widget.configure(insertbackground=fg_color)
                
                # Update children
                for child in widget.winfo_children():
                    update_widget_colors(child)
            except Exception as e:
                print(f"Error updating widget colors: {e}")
        
        # Start updating from root
        update_widget_colors(self.root)
        
        # Update matplotlib figure
        if self.fig:
            self.fig.set_facecolor(bg_color)
            if self.ax:
                self.ax.set_facecolor(bg_color)
                self.ax.tick_params(colors=fg_color)
                self.ax.xaxis.label.set_color(fg_color)
                self.ax.yaxis.label.set_color(fg_color)
                self.ax.title.set_color(fg_color)
                self.canvas.draw()

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
        print("\n=== Starting UI Setup ===")
        # Configure grid weights for the root window
        self.root.grid_rowconfigure(1, weight=1)  # Make the canvas row expandable
        self.root.grid_columnconfigure(0, weight=1)
        print("Root window grid configured")

        # Main frame for all controls
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        frame.grid_columnconfigure(6, weight=1)  # Make the last column expandable
        print("Main frame created and gridded")
        
        # First row of controls
        # Add airspace selection dropdown
        ttk.Label(frame, text="Select Airspace:").grid(row=0, column=0, padx=5)
        self.airspace_var = tk.StringVar(value="Catalunya")
        self.airspace_dropdown = ttk.Combobox(frame, textvariable=self.airspace_var, 
                                            values=["Catalunya", "España", "Europe"],
                                            state="readonly", width=15)
        self.airspace_dropdown.grid(row=0, column=1, padx=5)
        
        # Main control buttons
        self.load_button = ttk.Button(frame, text="Load Selected Airspace", command=self.load_selected_airspace)
        self.load_button.grid(row=0, column=2, padx=5)
        self.visualize_button = ttk.Button(frame, text="Visualize Airspace", command=self.visualize_airspace, state='disabled')
        self.visualize_button.grid(row=0, column=3, padx=5)
        self.stop_visualize_button = ttk.Button(frame, text="Stop Visualization", command=self.stop_visualization, state='disabled')
        self.stop_visualize_button.grid(row=0, column=4, padx=5)
        self.status_label = ttk.Label(frame, text="Status: Waiting for data load...")
        self.status_label.grid(row=0, column=5, padx=10)

        # Second row of controls
        self.show_image_button = ttk.Button(frame, text="Show Predefined Graph Image", command=self._show_predefined_image)
        self.show_image_button.grid(row=1, column=0, padx=5, pady=5)
        self.load_simple_graph_button = ttk.Button(frame, text="Load Simple Graph", command=self._load_simple_graph)
        self.load_simple_graph_button.grid(row=1, column=1, padx=5, pady=5)
        self.create_simple_graph_button = ttk.Button(frame, text="Create New Simple Graph", command=self._create_new_simple_graph)
        self.create_simple_graph_button.grid(row=1, column=2, padx=5, pady=5)
        self.show_path_features_button = ttk.Button(frame, text="Show Path Finding Features", command=self.show_v2_features)
        self.show_path_features_button.grid(row=1, column=3, padx=5, pady=5)
        self.show_edit_panel_button = ttk.Button(frame, text="Show Edit Panel", command=self.show_edit_panel)
        self.show_edit_panel_button.grid(row=1, column=4, padx=5, pady=5)
        self.show_photo_group_button = ttk.Button(frame, text="Show Photo Group", command=self.show_photo_group)
        self.show_photo_group_button.grid(row=1, column=5, padx=5, pady=5)
        
        # Third row of controls
        self.export_kml_button = ttk.Button(frame, text="Export to KML", command=self.export_to_kml, state='disabled')
        self.export_kml_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.show_extra_features_button = ttk.Button(frame, text="Extra Features", command=self.show_extra_features)
        self.show_extra_features_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky='ew')
        print("All control buttons created and gridded")

        # Create canvas frame for visualization
        print("Creating canvas frame...")
        self.airspace_canvas_frame = ttk.Frame(self.root)
        print(f"Canvas frame created: {self.airspace_canvas_frame}")
        self.airspace_canvas_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        self.airspace_canvas_frame.grid_rowconfigure(1, weight=1)
        self.airspace_canvas_frame.grid_columnconfigure(0, weight=1)
        print("Canvas frame gridded and configured")
        print("=== UI Setup Complete ===\n")

    def export_to_kml(self):
        """Export the current airspace data to a KML file."""
        if not self.airspace:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        try:
            # Open file dialog to choose save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".kml",
                filetypes=[("KML files", "*.kml"), ("All files", "*.*")],
                title="Export to KML"
            )
            
            if not file_path:  # User cancelled
                return

            # Create KML content
            kml_content = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<kml xmlns="http://www.opengis.net/kml/2.2">',
                '<Document>',
                f'<name>{self.airspace.name} Airspace</name>',
                '<description>Exported from Airspace Explorer</description>'
            ]

            # Add navigation points
            for point in self.airspace.nav_points:
                # Create a placemark for each point
                kml_content.extend([
                    '<Placemark>',
                    f'<name>{point.number} - {point.name}</name>',
                    '<Point>',
                    f'<coordinates>{point.longitude},{point.latitude},0</coordinates>',
                    '</Point>',
                    '</Placemark>'
                ])

            # Add segments as LineStrings
            for segment in self.airspace.nav_segments:
                origin = self.airspace.get_nav_point(segment.origin_number)
                dest = self.airspace.get_nav_point(segment.destination_number)
                if origin and dest:
                    kml_content.extend([
                        '<Placemark>',
                        f'<name>Segment {origin.number}-{dest.number}</name>',
                        '<LineString>',
                        '<coordinates>',
                        f'{origin.longitude},{origin.latitude},0 {dest.longitude},{dest.latitude},0',
                        '</coordinates>',
                        '</LineString>',
                        '</Placemark>'
                    ])

            # Add airports with special styling
            if hasattr(self.airspace, 'nav_airports'):
                for airport in self.airspace.nav_airports:
                    kml_content.extend([
                        '<Placemark>',
                        f'<name>{airport.icao} - {airport.name}</name>',
                        '<styleUrl>#airport</styleUrl>',
                        '<Point>',
                        f'<coordinates>{airport.longitude},{airport.latitude},0</coordinates>',
                        '</Point>',
                        '</Placemark>'
                    ])

            # Close KML document
            kml_content.extend([
                '</Document>',
                '</kml>'
            ])

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(kml_content))

            self.status_label.config(text=f"Status: Airspace exported to KML successfully.")
            messagebox.showinfo("Success", f"Airspace exported to:\n{file_path}")

        except Exception as e:
            error_msg = str(e)
            print(f"KML export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export to KML: {error_msg}")
            self.status_label.config(text="Status: KML export failed.")

    def on_window_resize(self, event):
        """Handle window resize with debouncing"""
        if event.widget != self.root or not self.airspace_image:
            return

        # Cancel any pending resize
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)

        # Schedule new resize
        self._resize_timer = self.root.after(self._resize_delay, self._delayed_resize)

    def _delayed_resize(self):
        """Actually perform the resize after the delay"""
        self._resize_timer = None
        # Re-visualize the current graph if one is loaded
        if self.current_graph_type:
            self._visualize_current_graph()

    def update_v2_dropdowns(self):
        """Helper to update dropdowns for navpoints"""
        # Check if dropdowns exist before trying to update them
        if not hasattr(self, 'reach_point_dropdown') or not hasattr(self, 'path_origin_dropdown') or not hasattr(self, 'path_dest_dropdown'):
            return

        if not self.airspace or not self.airspace.nav_points:
            values = []
        else:
            values = [f"{p.number} ({p.name})" for p in self.airspace.nav_points]
            
        self.reach_point_dropdown['values'] = values
        self.path_origin_dropdown['values'] = values
        self.path_dest_dropdown['values'] = values
        
        if values:
            self.reach_point_var.set(values[0])
            self.path_origin_var.set(values[0])
            self.path_dest_var.set(values[-1])

    def load_selected_airspace(self):
        print("\n=== Starting Airspace Load ===")
        try:
            selected_airspace = self.airspace_var.get()
            print(f"Selected airspace: {selected_airspace}")
            
            # Map display names to directory names
            dir_names = {
                "Catalunya": "airspace_catalonia",
                "España": "Airspace Spain",
                "Europe": "ECAC airspace"
            }
            base_dir = os.path.join(os.path.dirname(__file__), dir_names[selected_airspace])
            print(f"Base directory: {base_dir}")
            
            # Define file patterns for each airspace
            file_patterns = {
                "Catalunya": ("Cat_nav.txt", "Cat_seg.txt", "Cat_aer.txt"),
                "España": ("Spain_nav.txt", "Spain_seg.txt", "Spain_aer.txt"),
                "Europe": ("ECAC_nav.txt", "ECAC_seg.txt", "ECAC_aer.txt")
            }
            
            # Disable buttons during loading
            print("Disabling buttons...")
            self.load_button.configure(state='disabled')
            self.visualize_button.configure(state='disabled')
            self.stop_visualize_button.configure(state='disabled')
            self.export_kml_button.configure(state='disabled')
            self.root.update_idletasks()
            
            # Handle Spain airspace data which is in a zip file
            temp_dir = None
            if selected_airspace == "España":
                print("Processing Spain airspace data...")
                self.status_label.config(text="Extracting Spain airspace data...")
                self.root.update_idletasks()
                
                zip_path = os.path.join(base_dir, "Spain_graph.zip")
                print(f"Looking for zip file at: {zip_path}")
                if not os.path.exists(zip_path):
                    raise FileNotFoundError("Spain airspace data zip file not found.")
                    
                # Create a temporary directory for extracted files
                import tempfile
                import zipfile
                temp_dir = tempfile.mkdtemp()
                print(f"Created temporary directory: {temp_dir}")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        print("Extracting zip file...")
                        zip_ref.extractall(temp_dir)
                    base_dir = temp_dir  # Use the temporary directory for file paths
                    print("Zip file extracted successfully")
                except Exception as e:
                    raise Exception(f"Failed to extract Spain airspace data: {str(e)}")
            
            # Verify all required files exist
            nav_file = os.path.join(base_dir, file_patterns[selected_airspace][0])
            seg_file = os.path.join(base_dir, file_patterns[selected_airspace][1])
            aer_file = os.path.join(base_dir, file_patterns[selected_airspace][2])
            
            print(f"Checking required files:")
            print(f"  Nav file: {nav_file}")
            print(f"  Seg file: {seg_file}")
            print(f"  Aer file: {aer_file}")
            
            for file_path in [nav_file, seg_file, aer_file]:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Required file not found: {os.path.basename(file_path)}")
            
            self.status_label.config(text=f"Loading {selected_airspace} airspace data...")
            self.root.update_idletasks()
            
            # Create new airspace instance
            print("Creating new AirSpace instance...")
            self.airspace = AirSpace(name=selected_airspace)
            
            # Load data with timeout
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def load_data_thread():
                try:
                    print("Starting data load in thread...")
                    success = self.airspace.load_data(nav_file, seg_file, aer_file)
                    print(f"Data load completed with success: {success}")
                    result_queue.put(("success", success))
                except Exception as e:
                    print(f"Error in load thread: {str(e)}")
                    result_queue.put(("error", str(e)))
            
            # Start loading in a separate thread
            print("Starting load thread...")
            thread = threading.Thread(target=load_data_thread)
            thread.daemon = True
            thread.start()
            
            # Wait for result with timeout
            try:
                print("Waiting for load result...")
                result_type, result = result_queue.get(timeout=30)  # 30 second timeout
                if result_type == "error":
                    raise Exception(result)
                if not result:
                    raise Exception(f"Failed to load {selected_airspace} airspace data.")
            except queue.Empty:
                raise Exception("Loading timed out after 30 seconds")
            
            self.status_label.config(text=f"Status: {selected_airspace} airspace loaded.")
            self.visualize_button.config(state='normal')
            self.export_kml_button.config(state='normal')
            self.show_airspace_info()
            self.update_v2_dropdowns()
            print("Airspace load completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error loading airspace: {error_msg}")
            messagebox.showerror("Error", f"Failed to load {selected_airspace} airspace data: {error_msg}")
            self.status_label.config(text="Status: Failed to load data.")
            self.visualize_button.configure(state='disabled')
            self.export_kml_button.configure(state='disabled')
            
        finally:
            # Clean up temporary directory for Spain airspace
            if temp_dir and os.path.exists(temp_dir):
                try:
                    print(f"Cleaning up temporary directory: {temp_dir}")
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Error cleaning up temp directory: {str(e)}")
            
            # Set the current graph data
            self.current_graph_type = 'airspace'
            self.current_graph_data = self.airspace

            # Clear any previously loaded simple graph data
            # Note: We don't explicitly clear the airspace object here as it's replaced
            # but we should clear the simple graph data structure if that was loaded previously.
            # This might involve adding a dedicated cleanup method or checking type.
            # For now, assume switching from simple to airspace replaces the need to clear simple data.

            # Re-enable buttons
            self.load_button.configure(state='normal')
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def show_airspace_info(self):
        """Show airspace statistics in a message box."""
        if not self.airspace:
            return
            
        stats = self.airspace.get_statistics()
        info = [
            f"Airspace: {stats['name']}",
            f"Navigation Points: {stats['num_nav_points']}",
            f"Segments: {stats['num_segments']}",
            f"Airports: {stats['num_airports']}",
            f"Total SIDs: {stats['total_sids']}",
            f"Total STARs: {stats['total_stars']}",
            "",
            "Airports List:"
        ]
        for airport in self.airspace.nav_airports:
            info.append(f"- {airport.icao} ({airport.name})")
            if airport.sids:
                info.append(f"    SIDs: {', '.join(airport.get_sids())}")
            if airport.stars:
                info.append(f"    STARs: {', '.join(airport.get_stars())}")
        
        # Show info in a message box
        messagebox.showinfo("Airspace Information", "\n".join(info))

    def show_neighbors(self):
        """Show neighbors of selected node in the current airspace"""
        if not self.airspace or not self.airspace.nav_points:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        window = self.create_modal_window("Show Neighbors", 400, 300)
        
        # Create frame with padding
        frame = ttk.Frame(window, style='Padded.TFrame')
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Node selection
        ttk.Label(frame, text="Select node:", style='Custom.TLabel').grid(row=0, column=0, sticky='ew')
        node_var = tk.StringVar(window)
        node_names = [f"{point.number} ({point.name})" for point in self.airspace.nav_points]
        node_dropdown = ttk.Combobox(frame, textvariable=node_var, values=node_names, state="readonly")
        node_dropdown.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        if node_names:
            node_dropdown.set(node_names[0])
        
        # Results text area
        result_text = tk.Text(frame, height=10, wrap='word', state='disabled')
        result_text.grid(row=2, column=0, sticky='nsew', pady=5)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=result_text.yview)
        scrollbar.grid(row=2, column=1, sticky='ns')
        result_text.configure(yscrollcommand=scrollbar.set)
        
        def show_node_neighbors():
            try:
                point_info = node_var.get()
                point_number = int(point_info.split()[0])
                selected_point = self.airspace.get_nav_point(point_number)
                
                if not selected_point:
                    raise ValueError(f"Point {point_number} not found")
                
                # Get neighbors through segments
                neighbors = set()
                for segment in self.airspace.get_segments_from(point_number):
                    neighbor = self.airspace.get_nav_point(segment.destination_number)
                    if neighbor:
                        neighbors.add(neighbor)
                
                # Display results
                result_text.config(state='normal')
                result_text.delete(1.0, 'end')
                
                if neighbors:
                    result_text.insert('end', f"Neighbors of point {point_number} ({selected_point.name}):\n\n")
                    for neighbor in sorted(neighbors, key=lambda x: x.number):
                        result_text.insert('end', f"- Point {neighbor.number} ({neighbor.name})\n")
                else:
                    result_text.insert('end', f"Point {point_number} ({selected_point.name}) has no neighbors.")
                
                result_text.config(state='disabled')
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(frame, text="Show Neighbors", command=show_node_neighbors, 
                  style='Dialog.TButton').grid(row=3, column=0, sticky='ew', pady=(10, 0))

    def visualize_airspace(self):
        """Visualize the airspace with proper error handling and state management"""
        print("\n=== Starting Airspace Visualization ===")
        if not self.airspace:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        try:
            # Set visualization state
            self.visualization_running = True
            
            # Disable/enable appropriate buttons
            self.visualize_button.configure(state='disabled')
            self.stop_visualize_button.configure(state='normal')
            self.root.update_idletasks()

            # Update status
            self.status_label.config(text="Status: Preparing visualization...")
            self.root.update_idletasks()

            # Set a reasonable figure size for matplotlib (in inches)
            fig_width, fig_height = 12, 9
            dpi = 100

            # Create figure with a white background
            fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi, facecolor='white')
            ax = fig.add_subplot(111)

            self.fig = fig # Store figure
            self.ax = ax # Store axes

            # Add map background for Catalonia, Spain, or Europe
            if self.airspace.name in ["Catalunya", "España", "Europe"]:
                print(f"\n=== Loading Map for {self.airspace.name} ===")
                try:
                    # Load the map image
                    map_names = {
                        "Catalunya": "Catalonia map.jpg",
                        "España": "Spain map.jpg",
                        "Europe": "Europe map.jpg"
                    }
                    map_name = map_names[self.airspace.name]
                    
                    # Try multiple possible paths for the map
                    possible_paths = [
                        os.path.join('V6', 'maps', map_name),
                        os.path.join('maps', map_name),
                        os.path.join(os.path.dirname(__file__), 'maps', map_name),
                        os.path.join(os.path.dirname(__file__), 'V6', 'maps', map_name)
                    ]
                    
                    map_path = None
                    for path in possible_paths:
                        print(f"Checking path: {os.path.abspath(path)}")
                        if os.path.exists(path):
                            map_path = path
                            print(f"Found map at: {os.path.abspath(path)}")
                            break
                    
                    if not map_path:
                        print("Map file not found in any of the expected locations:")
                        for path in possible_paths:
                            print(f"  - {os.path.abspath(path)}")
                        raise FileNotFoundError(f"Could not find map file for {self.airspace.name}")
                    
                    print(f"Loading map from: {os.path.abspath(map_path)}")
                    img = Image.open(map_path)
                    print(f"Map image size: {img.size}")
                    
                    # Get current axis limits
                    if hasattr(self.airspace, 'nav_points') and self.airspace.nav_points:
                        lats = [point.latitude for point in self.airspace.nav_points]
                        lons = [point.longitude for point in self.airspace.nav_points]
                        if lats and lons:
                            min_lat, max_lat = min(lats), max(lats)
                            min_lon, max_lon = min(lons), max(lons)
                            print(f"Using coordinates from nav points: lon={min_lon} to {max_lon}, lat={min_lat} to {max_lat}")
                        else:
                            # Default coordinates based on region
                            if self.airspace.name == "Catalunya":
                                min_lon, max_lon = 0.0, 3.5
                                min_lat, max_lat = 40.0, 43.0
                            elif self.airspace.name == "España":
                                min_lon, max_lon = -10.0, 5.0
                                min_lat, max_lat = 35.0, 44.0
                            else:  # Europe
                                min_lon, max_lon = -15.0, 30.0
                                min_lat, max_lat = 35.0, 60.0
                            print(f"Using default coordinates for {self.airspace.name}: lon={min_lon} to {max_lon}, lat={min_lat} to {max_lat}")
                    else:
                        # Default coordinates based on region
                        if self.airspace.name == "Catalunya":
                            min_lon, max_lon = 0.0, 3.5
                            min_lat, max_lat = 40.0, 43.0
                        elif self.airspace.name == "España":
                            min_lon, max_lon = -10.0, 5.0
                            min_lat, max_lat = 35.0, 44.0
                        else:  # Europe
                            min_lon, max_lon = -15.0, 30.0
                            min_lat, max_lat = 35.0, 60.0
                        print(f"Using default coordinates for {self.airspace.name}: lon={min_lon} to {max_lon}, lat={min_lat} to {max_lat}")

                    # Add padding
                    lon_padding = (max_lon - min_lon) * 0.1
                    lat_padding = (max_lat - min_lat) * 0.1
                    initial_xlim = (min_lon - lon_padding, max_lon + lon_padding)
                    initial_ylim = (min_lat - lat_padding, max_lat + lat_padding)
                    
                    print(f"Setting map extent with padding: lon={initial_xlim}, lat={initial_ylim}")
                    
                    # Display the image as background
                    ax.imshow(img, extent=[initial_xlim[0], initial_xlim[1], initial_ylim[0], initial_ylim[1]], 
                             aspect='auto', alpha=0.5, zorder=0)
                    print("Map background added successfully")
                    print("=== Map Loading Complete ===\n")
                except Exception as e:
                    print(f"Error loading map background: {str(e)}")
                    print(f"Error type: {type(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    print("=== Map Loading Failed ===\n")

            # Update status
            self.status_label.config(text="Status: Drawing segments...")
            self.root.update_idletasks()

            # Draw segments with reduced alpha for better performance
            if hasattr(self.airspace, 'nav_segments') and self.airspace.nav_segments:
                # Group segments by type for better performance
                airport_segments = []
                nav_segments = []
                for segment in self.airspace.nav_segments:
                    try:
                        # Check if either origin or destination is an airport
                        origin = self.airspace.get_nav_point(segment.origin_number)
                        dest = self.airspace.get_nav_point(segment.destination_number)
                        if origin and dest and hasattr(self.airspace, 'nav_airports'):
                            if origin in self.airspace.nav_airports or dest in self.airspace.nav_airports:
                                airport_segments.append(segment)
                            else:
                                nav_segments.append(segment)
                    except Exception as e:
                        print(f"Error processing segment: {str(e)}")
                        continue

                # Draw non-airport segments first (more transparent)
                if nav_segments:
                    try:
                        x_coords = []
                        y_coords = []
                        for segment in nav_segments:
                            origin = self.airspace.get_nav_point(segment.origin_number)
                            dest = self.airspace.get_nav_point(segment.destination_number)
                            if origin and dest:
                                x_coords.extend([origin.longitude, dest.longitude, None])
                                y_coords.extend([origin.latitude, dest.latitude, None])
                        if x_coords and y_coords:  # Only plot if we have valid coordinates
                            ax.plot(x_coords, y_coords, 'gray', alpha=0.2, linewidth=0.5, label='Nav Segments')
                    except Exception as e:
                        print(f"Error drawing nav segments: {str(e)}")

                # Draw airport segments (more visible)
                if airport_segments:
                    try:
                        x_coords = []
                        y_coords = []
                        for segment in airport_segments:
                            origin = self.airspace.get_nav_point(segment.origin_number)
                            dest = self.airspace.get_nav_point(segment.destination_number)
                            if origin and dest:
                                x_coords.extend([origin.longitude, dest.longitude, None])
                                y_coords.extend([origin.latitude, dest.latitude, None])
                        if x_coords and y_coords:  # Only plot if we have valid coordinates
                            ax.plot(x_coords, y_coords, 'red', alpha=0.4, linewidth=0.8, label='Airport Segments')
                    except Exception as e:
                        print(f"Error drawing airport segments: {str(e)}")

            # Check if visualization was stopped
            if not self.visualization_running:
                plt.close(fig)
                return

            # Update status
            self.status_label.config(text="Status: Drawing points...")
            self.root.update_idletasks()

            # Draw points with reduced size for better performance
            if hasattr(self.airspace, 'nav_points') and self.airspace.nav_points:
                try:
                    # Group points by type
                    airports = []
                    nav_points = []
                    for point in self.airspace.nav_points:
                        if hasattr(self.airspace, 'nav_airports') and point in self.airspace.nav_airports:
                            airports.append(point)
                        else:
                            nav_points.append(point)

                    # Draw navigation points
                    if nav_points:
                        x_coords = [p.longitude for p in nav_points]
                        y_coords = [p.latitude for p in nav_points]
                        if x_coords and y_coords:  # Only plot if we have valid coordinates
                            ax.scatter(x_coords, y_coords, c='blue', s=20, alpha=0.6, label='Nav Points')

                    # Draw airports
                    if airports:
                        x_coords = [p.longitude for p in airports]
                        y_coords = [p.latitude for p in airports]
                        if x_coords and y_coords:  # Only plot if we have valid coordinates
                            ax.scatter(x_coords, y_coords, c='red', s=50, alpha=0.8, label='Airports')
                except Exception as e:
                    print(f"Error drawing points: {str(e)}")

            # Check if visualization was stopped
            if not self.visualization_running:
                plt.close(fig)
                return

            # Update status
            self.status_label.config(text="Status: Finalizing visualization...")
            self.root.update_idletasks()

            # Set plot properties
            ax.set_title(f"{self.airspace.name} Airspace")
            ax.grid(True, alpha=0.3)
            
            # Set axis labels
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')

            # Only add legend if we have points to show
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(handles, labels, loc='upper right', fontsize='small')

            # Save the plot with optimized settings
            buf = io.BytesIO()
            fig.savefig(buf, 
                       format='png', 
                       dpi=dpi, 
                       bbox_inches='tight',
                       pad_inches=0.2,
                       facecolor='white',
                       edgecolor='none')
            plt.close(fig) # Close the figure after saving to free memory
            buf.seek(0)

            # Check if visualization was stopped
            if not self.visualization_running:
                return

            # Update status
            self.status_label.config(text="Status: Loading image...")
            self.root.update_idletasks()

            # Load and display the image
            img = Image.open(buf)

            # --- Embedding Matplotlib Figure in Tkinter Canvas ---
            print("Creating matplotlib canvas...")
            # Clear previous canvas content
            if self.canvas_widget:
                print("Destroying previous canvas widget...")
                self.canvas_widget.destroy()
            if self.canvas:
                print("Destroying previous canvas...")
                self.canvas.get_tk_widget().destroy()
            if self.toolbar:
                print("Destroying previous toolbar...")
                self.toolbar.destroy()

            # Create a FigureCanvasTkAgg widget
            print("Creating new FigureCanvasTkAgg...")
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.airspace_canvas_frame)
            self.canvas_widget = self.canvas.get_tk_widget()

            # Create the navigation toolbar
            print("Creating navigation toolbar...")
            toolbar_frame = ttk.Frame(self.airspace_canvas_frame)
            toolbar_frame.grid(row=0, column=0, sticky='ew')
            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            self.toolbar.update()
            print("Toolbar created and configured")

            # Embed the matplotlib canvas widget into the Tkinter canvas
            print("Gridding canvas widget...")
            self.canvas_widget.grid(row=1, column=0, sticky='nsew') # Use grid to place in the canvas frame

            # Redraw the canvas
            print("Drawing canvas...")
            self.canvas.draw()

            # Update status
            self.status_label.config(text=f"Status: {self.airspace.name} airspace visualization complete.")
            print("=== Airspace Visualization Complete ===\n")

        except Exception as e:
            error_msg = str(e)
            print(f"Visualization error: {e}") # Debug print the error
            messagebox.showerror("Visualization Error", f"Failed to visualize airspace: {error_msg}")
            self.status_label.config(text="Status: Visualization failed.")

        finally:
            # Reset visualization state and button states
            self.visualization_running = False
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def show_v2_features(self):
        """Show a modal window with reachability and shortest path features."""
        print("\n=== Starting Path Finding Features Window Setup ===")
        if not self.airspace:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        window = tk.Toplevel(self.root)
        window.title("Path Finding Features")
        window.geometry('800x600')
        window.transient(self.root)
        print("Path finding features window created")
        
        # Center the window
        x = self.root.winfo_x() + (self.root.winfo_width() - 800) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 600) // 2
        window.geometry(f'+{x}+{y}')
        print("Window positioned")
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(window)
        notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        print("Notebook created and gridded")
        
        # Reachability tab
        reachability_frame = ttk.Frame(notebook, padding="10")
        notebook.add(reachability_frame, text="Reachability Analysis")
        reachability_frame.grid_rowconfigure(1, weight=1)
        reachability_frame.grid_columnconfigure(0, weight=1)
        print("Reachability frame created and configured")
        
        # Reachability controls
        control_frame = ttk.Frame(reachability_frame)
        control_frame.grid(row=0, column=0, sticky='ew', pady=5)
        control_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(control_frame, text="Start Point:").grid(row=0, column=0, padx=5)
        self.reach_point_var = tk.StringVar()
        self.reach_point_dropdown = ttk.Combobox(control_frame, textvariable=self.reach_point_var, 
                                               values=[f"{point.number} ({point.name})" for point in self.airspace.nav_points],
                                               state="readonly", width=30)
        self.reach_point_dropdown.grid(row=0, column=1, padx=5, sticky='ew')
        if self.airspace.nav_points:
            self.reach_point_dropdown.set(f"{self.airspace.nav_points[0].number} ({self.airspace.nav_points[0].name})")
        
        ttk.Button(control_frame, text="Show Reachability", 
                  command=self._show_reachability).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Status text area for reachability
        status_frame = ttk.Frame(reachability_frame)
        status_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        
        print("Creating reachability status text widget...")
        self.reach_status_text = tk.Text(status_frame, wrap='word', state='disabled')
        self.reach_status_text.grid(row=0, column=0, sticky='nsew')
        reach_scroll = ttk.Scrollbar(status_frame, orient='vertical', command=self.reach_status_text.yview)
        reach_scroll.grid(row=0, column=1, sticky='ns')
        self.reach_status_text.configure(yscrollcommand=reach_scroll.set)
        print("Reachability status text widget created and configured")
        
        # Shortest Path tab
        path_frame = ttk.Frame(notebook, padding="10")
        notebook.add(path_frame, text="Shortest Path (A*)")
        path_frame.grid_rowconfigure(1, weight=1)
        path_frame.grid_columnconfigure(0, weight=1)
        print("Path frame created and configured")
        
        # Path finding controls
        path_control_frame = ttk.Frame(path_frame)
        path_control_frame.grid(row=0, column=0, sticky='ew', pady=5)
        path_control_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(path_control_frame, text="Origin:").grid(row=0, column=0, padx=5)
        self.path_origin_var = tk.StringVar()
        self.path_origin_dropdown = ttk.Combobox(path_control_frame, textvariable=self.path_origin_var,
                                               values=[f"{point.number} ({point.name})" for point in self.airspace.nav_points],
                                               state="readonly", width=30)
        self.path_origin_dropdown.grid(row=0, column=1, padx=5, sticky='ew')
        if self.airspace.nav_points:
            self.path_origin_dropdown.set(f"{self.airspace.nav_points[0].number} ({self.airspace.nav_points[0].name})")

        ttk.Label(path_control_frame, text="Destination:").grid(row=1, column=0, padx=5)
        self.path_dest_var = tk.StringVar()
        self.path_dest_dropdown = ttk.Combobox(path_control_frame, textvariable=self.path_dest_var,
                                             values=[f"{point.number} ({point.name})" for point in self.airspace.nav_points],
                                             state="readonly", width=30)
        self.path_dest_dropdown.grid(row=1, column=1, padx=5, sticky='ew')
        if self.airspace.nav_points:
            self.path_dest_dropdown.set(f"{self.airspace.nav_points[-1].number} ({self.airspace.nav_points[-1].name})")
        
        ttk.Button(path_control_frame, text="Find Shortest Path", 
                  command=self._find_path).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Status text area for path finding
        path_status_frame = ttk.Frame(path_frame)
        path_status_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        path_status_frame.grid_rowconfigure(0, weight=1)
        path_status_frame.grid_columnconfigure(0, weight=1)
        
        print("Creating path finding status text widget...")
        self.path_status_text = tk.Text(path_status_frame, wrap='word', state='disabled')
        self.path_status_text.grid(row=0, column=0, sticky='nsew')
        path_scroll = ttk.Scrollbar(path_status_frame, orient='vertical', command=self.path_status_text.yview)
        path_scroll.grid(row=0, column=1, sticky='ns')
        self.path_status_text.configure(yscrollcommand=path_scroll.set)
        print("Path finding status text widget created and configured")
        print("=== Path Finding Features Window Setup Complete ===\n")

    def _on_plot_window_resize(self, event, fig, canvas):
        """Handle resize event for plot windows to redraw canvas."""
        # Check if the event is from the toplevel window itself or if event is None (for scheduled calls)
        if event is None or event.widget == event.widget.winfo_toplevel():
            try:
                print(f"[_on_plot_window_resize] Resize event detected: {event.type if event else 'Scheduled'}, widget: {event.widget if event else 'None'}") # Debug print
                # Get the new size of the canvas widget
                canvas_width = canvas.get_tk_widget().winfo_width()
                canvas_height = canvas.get_tk_widget().winfo_height()

                print(f"[_on_plot_window_resize] Canvas widget size (px): {canvas_width}x{canvas_height}") # Debug print

                if canvas_width <= 1 or canvas_height <= 1: # Check against 1x1 as well
                    # Avoid errors with zero or 1x1 dimensions during minimization or initial states
                        print("[_on_plot_window_resize] Canvas size is too small, skipping redraw.") # Debug print
                        # If size is still too small, schedule another check (optional, but can help)
                        if event is not None: # Only reschedule if it was a real resize event
                             event.widget.after(50, lambda: self._on_plot_window_resize(None, fig, canvas))
                        return

                # Ensure the canvas updates with the new window size
                canvas.draw_idle()

                # The manual figure resizing code is removed as it was causing issues
                # dpi = fig.get_dpi()
                # fig.set_size_inches(canvas_width / dpi, canvas_height / dpi, forward=True)
                # print(f"[_on_plot_window_resize] Figure size set to (inches): {fig.get_size_inches()}") # Debug print

                # Ensure the aspect ratio is still 'equal' after resize
                # This might be redundant with 'adjustable='box'' but good to be explicit
                # for ax in fig.get_axes():
                #     ax.set_aspect('equal', adjustable='box')

                # Redraw the canvas
                # canvas.draw() # draw_idle is preferred for interactive backends
            except Exception as e:
                print(f"Error during plot window resize: {e}")

    def _show_reachability(self):
        """Show the reachability graph in a new window."""
        print("\n=== Starting Reachability Analysis ===")
        if not self.airspace or not self.airspace.nav_points:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        try:
            # Get selected start point from the instance variable dropdown
            point_info = self.reach_point_var.get()
            if not point_info:
                 messagebox.showwarning("Selection Error", "Please select a start point.")
                 return
            point_number = int(point_info.split()[0])
            start_point = self.airspace.get_nav_point(point_number)

            if not start_point:
                messagebox.showerror("Error", f"Point {point_number} not found")
                return

            print(f"Starting reachability analysis from point {point_number} ({start_point.name})")

            # Create a new top-level window
            reachability_window = tk.Toplevel(self.root)
            reachability_window.title(f"Reachability Graph from {start_point.name}")
            reachability_window.geometry('1200x800') # Set a default size

            # Create a frame for the matplotlib canvas and toolbar
            plot_frame = ttk.Frame(reachability_window)
            plot_frame.pack(fill='both', expand=True)
            plot_frame.grid_rowconfigure(1, weight=1)
            plot_frame.grid_columnconfigure(0, weight=1)

            # Create a frame for the toolbar
            toolbar_frame = ttk.Frame(plot_frame)
            toolbar_frame.grid(row=0, column=0, sticky='ew')

            # Create figure and axes for the plot
            fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')

            # Plot the base airspace (static background)
            self.airspace.plot(
                fig=fig,
                ax=ax,
                show_points=True,
                show_segments=True,
                show_airports=True,
                point_color='blue',
                segment_color='gray',
                airport_color='red',
                point_size=20,
                segment_width=0.5,
                airport_size=50,
                point_alpha=0.6,
                segment_alpha=0.2,
                airport_alpha=0.7
            )

            # Perform reachability calculation
            reachable = set()
            queue = [start_point]
            visited = {start_point.number}
            while queue:
                current = queue.pop(0)
                reachable.add(current)
                for segment in self.airspace.get_segments_from(current.number):
                    dest_number = segment.destination_number
                    if dest_number not in visited:
                        visited.add(dest_number)
                        dest_point = self.airspace.get_nav_point(dest_number)
                        if dest_point:
                            queue.append(dest_point)


            # Highlight reachable points and the start point
            for point in reachable:
                ax.plot(point.longitude, point.latitude, 'go', 
                       markersize=8, alpha=0.8, label='Reachable' if point == start_point else "", zorder=3)
            ax.plot(start_point.longitude, start_point.latitude, 'ro',
                   markersize=10, alpha=1.0, label='Start Point', zorder=4)

            # Set plot properties
            ax.set_title(f"Reachable Points from {start_point.name}")
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.grid(True, alpha=0.3)

            # Add legend
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                # Ensure unique labels for the legend
                unique_labels = []
                unique_handles = []
                for h, l in zip(handles, labels):
                    if l not in unique_labels:
                        unique_labels.append(l)
                        unique_handles.append(h)
                ax.legend(unique_handles, unique_labels, loc='upper right', fontsize='small')

            # Embed the matplotlib canvas in the new window's frame
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=1, column=0, sticky='nsew')

            # Add toolbar to the new window's frame
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()

            # Bind the resize event for the new window
            reachability_window.bind('<Configure>', lambda event: self._on_plot_window_resize(event, fig, canvas))

            # Update status text in the main window
            reachable_names = [f"{p.number} ({p.name})" for p in reachable]
            status_text = f"From point {point_number}, you can reach {len(reachable)} points:\n" + \
                        ", ".join(reachable_names)
            
            # Update the status text in the features window
            if hasattr(self, 'reach_status_text') and self.reach_status_text:
                self.reach_status_text.config(state='normal')
                self.reach_status_text.delete(1.0, 'end')
                self.reach_status_text.insert('end', status_text)
                self.reach_status_text.config(state='disabled')

        except Exception as e:
            error_msg = str(e)
            print(f"Reachability visualization error: {e}") # Debug print the error
            messagebox.showerror("Reachability Visualization Error", f"Failed to visualize reachability: {error_msg}")
            if hasattr(self, 'reach_status_text') and self.reach_status_text:
                self.reach_status_text.config(state='normal')
                self.reach_status_text.delete(1.0, 'end')
                self.reach_status_text.insert('end', f"Error: {error_msg}")
                self.reach_status_text.config(state='disabled')

    def _find_path(self):
        """Show the shortest path graph (animated) in a new window."""
        if not self.airspace or not self.airspace.nav_points:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        try:
            # Get selected origin and destination points from the instance variable dropdowns
            origin_info = self.path_origin_var.get()
            dest_info = self.path_dest_var.get()
            if not origin_info or not dest_info:
                 messagebox.showwarning("Selection Error", "Please select both origin and destination points.")
                 return

            origin_number = int(origin_info.split()[0])
            dest_number = int(dest_info.split()[0])
            origin = self.airspace.get_nav_point(origin_number)
            destination = self.airspace.get_nav_point(dest_number)

            if not origin or not destination:
                messagebox.showerror("Error", "Selected points not found")
                return

            # --- Path Finding (A*) ---
            def heuristic(a, b):
                return ((a.longitude - b.longitude) ** 2 + 
                       (a.latitude - b.latitude) ** 2) ** 0.5

            def get_neighbors(point):
                return [self.airspace.get_nav_point(seg.destination_number)
                       for seg in self.airspace.get_segments_from(point.number)]

            def get_cost(a, b):
                for seg in self.airspace.get_segments_from(a.number):
                    if seg.destination_number == b.number:
                        return seg.distance
                return float('inf')

            open_set = {origin.number}
            closed_set = set()
            came_from = {}
            g_score = {origin.number: 0}
            f_score = {origin.number: heuristic(origin, destination)}

            path = []
            while open_set:
                current_number = min(open_set, key=lambda x: f_score.get(x, float('inf')))
                current = self.airspace.get_nav_point(current_number)

                if current_number == destination.number:
                    # Path found, reconstruct it
                    while current_number in came_from:
                        path.append(self.airspace.get_nav_point(current_number))
                        current_number = came_from[current_number]
                    path.append(origin)
                    path.reverse()
                    break # Exit the while loop

                open_set.remove(current_number)
                closed_set.add(current_number)

                for neighbor in get_neighbors(current):
                    if neighbor.number in closed_set:
                        continue

                    tentative_g = g_score[current_number] + get_cost(current, neighbor)

                    if neighbor.number not in open_set:
                        open_set.add(neighbor.number)
                    elif tentative_g >= g_score.get(neighbor.number, float('inf')):
                        continue

                    came_from[neighbor.number] = current_number
                    g_score[neighbor.number] = tentative_g
                    f_score[neighbor.number] = tentative_g + heuristic(neighbor, destination)

            if not path:
                if hasattr(self, 'path_status_text') and self.path_status_text:
                    self.path_status_text.config(state='normal')
                    self.path_status_text.delete(1.0, 'end')
                    self.path_status_text.insert('end', f"No path found from {origin_number} to {dest_number}")
                    self.path_status_text.config(state='disabled')
                return

            # --- Static Path Plot Setup ---
            # Create a new top-level window for the path plot
            path_window = tk.Toplevel(self.root)
            path_window.title(f"Shortest Path: {origin.name} to {destination.name}")
            path_window.geometry('1200x800') # Set a default size

            # Create a frame for the matplotlib canvas and toolbar
            plot_frame = ttk.Frame(path_window)
            plot_frame.pack(fill='both', expand=True)
            plot_frame.grid_rowconfigure(1, weight=1)
            plot_frame.grid_columnconfigure(0, weight=1)

            # Create a frame for the toolbar
            toolbar_frame = ttk.Frame(plot_frame)
            toolbar_frame.grid(row=0, column=0, sticky='ew')

            # Create figure and axes for the plot
            fig_path = plt.Figure(figsize=(12, 8), dpi=100, facecolor='white')
            ax_path = fig_path.add_subplot(111)

            # Plot the base map, points, and segments (static background)
            self.airspace.plot(
                fig=fig_path,
                ax=ax_path,
                show_points=True,
                show_segments=True,
                show_airports=True,
                point_color='blue',
                segment_color='gray',
                airport_color='red',
                point_size=20,
                segment_width=0.5,
                airport_size=50,
                point_alpha=0.6,
                segment_alpha=0.2,
                airport_alpha=0.7
            )

            # Plot the path
            path_x = [p.longitude for p in path]
            path_y = [p.latitude for p in path]
            ax_path.plot(path_x, path_y, 'r-', linewidth=2, alpha=0.8, label='Path', zorder=4)

            # Plot the start and end points more prominently
            ax_path.plot(origin.longitude, origin.latitude, 'go',
                       markersize=10, alpha=0.8, label='Start', zorder=5)
            ax_path.plot(destination.longitude, destination.latitude, 'mo',
                       markersize=10, alpha=0.8, label='End', zorder=5)

            # Set plot properties
            ax_path.set_title(f"Shortest Path: {origin.name} to {destination.name}")
            ax_path.set_xlabel('Longitude')
            ax_path.set_ylabel('Latitude')
            ax_path.grid(True, alpha=0.3)
            ax_path.set_aspect('equal', adjustable='box')

            # Add legend
            handles, labels = ax_path.get_legend_handles_labels()
            if handles:
                ax_path.legend(handles, labels, loc='upper right', fontsize='small')

            # Embed the plot in the new window's frame
            canvas_path = FigureCanvasTkAgg(fig_path, master=plot_frame)
            canvas_path_widget = canvas_path.get_tk_widget()
            canvas_path_widget.grid(row=1, column=0, sticky='nsew')

            # Add toolbar to the new window's frame
            toolbar_path = NavigationToolbar2Tk(canvas_path, toolbar_frame)
            toolbar_path.update()

            # Schedule a redraw shortly after the window is created
            path_window.after(10, lambda: self._on_plot_window_resize(None, fig_path, canvas_path))

            # Calculate path statistics
            total_distance = sum(get_cost(path[i], path[i+1]) for i in range(len(path)-1))
            path_points = [f"{p.number} ({p.name})" for p in path]

            # Calculate estimated flight data
            estimated_time_hours_float = total_distance / A320_CRUISING_SPEED_KMPH
            estimated_hours = int(estimated_time_hours_float)
            estimated_minutes = int((estimated_time_hours_float * 60) % 60)
            estimated_fuel_kg = estimated_time_hours_float * A320_FUEL_CONSUMPTION_KGPH

            # Update status text
            status_text = f"Path: {' -> '.join(path_points)}\n" + \
                        f"Total distance: {total_distance:.2f} km\n\n" + \
                        f"Estimated A320 Flight Data:\n" + \
                        f"  Flight Time: {estimated_hours}h {estimated_minutes}m\n" + \
                        f"  Fuel Burn: {estimated_fuel_kg:.2f} kg"

            if hasattr(self, 'path_status_text') and self.path_status_text:
                self.path_status_text.config(state='normal')
                self.path_status_text.delete(1.0, 'end')
                self.path_status_text.insert('end', status_text)
                self.path_status_text.config(state='disabled')

        except Exception as e:
            error_msg = str(e)
            print(f"Path finding error: {e}") # Debug print the error
            messagebox.showerror("Path Finding Error", f"Failed to find path: {error_msg}")
            if hasattr(self, 'path_status_text') and self.path_status_text:
                self.path_status_text.config(state='normal')
                self.path_status_text.delete(1.0, 'end')
                self.path_status_text.insert('end', f"Error: {error_msg}")
                self.path_status_text.config(state='disabled')

    def stop_visualization(self):
        """Stop the current visualization process and any running animations"""
        if self.visualization_running or self.fig or self.canvas or self.canvas_widget or self.toolbar:
            self.visualization_running = False
            self.status_label.config(text="Status: Visualization stopped.")
            self.fig = None
            self.ax = None
            if self.canvas: # Check if canvas exists before destroying
                 self.canvas.get_tk_widget().destroy() # Destroy the Tkinter widget associated with the canvas
                 self.canvas = None
            if self.airspace_canvas_frame: # Destroy the canvas frame
                self.airspace_canvas_frame.destroy()
                self.airspace_canvas_frame = None
            if self.toolbar:
                 self.toolbar.destroy()
                 self.toolbar = None
            # Stop path animation if it's running
            # if self.path_animation: # Removed animation stop
            #      self.path_animation.event_source.stop()
            #      self.path_animation = None
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def on_window_ready(self, event):
        """Handle window ready event"""
        # This method is primarily for initial visualization, not animations
        # Keep it as is or remove if not needed for initial view
        pass # Or add initial visualization call if desired

    def _show_predefined_image(self):
        """Show a predefined graph image in a new window."""
        image_path = os.path.join('V8', 'Figure_2.png')
        
        if not os.path.exists(image_path):
            messagebox.showerror("Error", f"Image file not found at: {image_path}")
            return

        try:
            # Create a new top-level window
            image_window = tk.Toplevel(self.root)
            image_window.title("Predefined Graph Image")

            # Load the image using PIL
            img = Image.open(image_path)
            # Convert to Tkinter PhotoImage
            tk_img = ImageTk.PhotoImage(img)

            # Create a label to display the image
            image_label = ttk.Label(image_window, image=tk_img)
            image_label.image = tk_img # Keep a reference!
            image_label.pack(padx=10, pady=10)

            # Adjust window size to fit the image
            image_window.geometry(f"{img.width}x{img.height}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")

    def _load_simple_graph(self):
        """Open a file dialog, load a simple graph from a text file, and display it."""
        
        file_path = filedialog.askopenfilename(
            initialdir=".",  # Start in the current directory
            title="Select Simple Graph File",
            filetypes=(("Text Files", "*.txt"), ("All files", "*.*"))
        )
        
        if not file_path:
            return # User cancelled
            
        print(f"Selected file for simple graph: {file_path}") # Debug print

        points = {}
        segments = []

        file_content = ""

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                file_content = "".join(lines)

            # Parse points and segments
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                
                if len(parts) == 3: # Could be Point (Name X Y) or Segment (Name P1 P2)
                    name = parts[0]
                    part1 = parts[1]
                    part2 = parts[2]

                    try:
                        # Attempt to parse as a point (Name X Y)
                        x = float(part1)
                        y = float(part2)
                        points[name] = (x, y)
                        print(f"Parsed point: {name} ({x}, {y})") # Debug print
                    except ValueError:
                        # If float conversion fails, assume it's a segment (Name P1 P2)
                        segment_name = name
                        point1_name = part1
                        point2_name = part2
                        segments.append((point1_name, point2_name)) # Store just point names for simplicity in this example
                        print(f"Parsed segment: {segment_name} from {point1_name} to {point2_name}") # Debug print

                elif len(parts) == 2: # Assume Segment (P1 P2) - backwards compatibility with original Data.txt segment format
                     point1_name = parts[0]
                     point2_name = parts[1]
                     segments.append((point1_name, point2_name))
                     print(f"Parsed segment (2 parts): from {point1_name} to {point2_name}") # Debug print

                else:
                    print(f"Skipping unknown line format: {line}")

            if not points:
                messagebox.showwarning("Load Error", "No points found in the file.")
                # If no points, maybe clear segments too? Or handle appropriately.
                self.current_graph_data = {'points': {}, 'segments': []}
                self.current_graph_type = 'simple'
                self._update_edit_panel_state() # Update panel state
                self._log_edit_status(f"Loaded file {os.path.basename(file_path)} but no points found.")
                self._visualize_current_graph()
                return

            # Display loaded data in a modal window
            data_window = self.create_modal_window(f"Loaded Data: {os.path.basename(file_path)}", 400, 400)

            text_area = tk.Text(data_window, wrap='word', state='normal')
            text_area.pack(fill='both', expand=True, padx=10, pady=10)
            text_area.insert('end', file_content)
            text_area.config(state='disabled')

            # Set the current graph data
            self.current_graph_type = 'simple'
            self.current_graph_data = {'points': points, 'segments': segments}

            # Clear any previously loaded airspace data (assuming it was stored in self.airspace)
            self.airspace = None

            self._log_edit_status(f"Successfully loaded data from {os.path.basename(file_path)}. Graph ready for editing/visualization.")

            # Visualize the loaded simple graph in the main canvas
            self._visualize_current_graph()

        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_path}")
            self._log_edit_status(f"Error: File not found at {file_path}.")
            self.current_graph_type = None
            self.current_graph_data = None
            self._update_edit_panel_state()
        except Exception as e:
            error_msg = str(e)
            print(f"Error loading or displaying simple graph: {e}") # Debug print
            messagebox.showerror("Error", f"Failed to load or display simple graph: {error_msg}")
            self._log_edit_status(f"Error loading simple graph: {error_msg}")
            self.current_graph_type = None
            self.current_graph_data = None
            self._update_edit_panel_state()

    def _update_edit_panel_state(self):
        """Enables or disables the edit panel controls based on the current graph type."""
        is_simple_graph = (self.current_graph_type == 'simple')
        state = 'normal' if is_simple_graph else 'disabled'

        # Check if UI elements exist before configuring
        if self.node_name_entry:
            self.node_name_entry.config(state=state)
        if self.node_x_entry:
            self.node_x_entry.config(state=state)
        if self.node_y_entry:
            self.node_y_entry.config(state=state)
        if self.add_node_button:
            self.add_node_button.config(state=state)
        if self.remove_node_button:
            self.remove_node_button.config(state=state)

        if self.segment_from_entry:
            self.segment_from_entry.config(state=state)
        if self.segment_to_entry:
            self.segment_to_entry.config(state=state)
        if self.add_segment_button:
            self.add_segment_button.config(state=state)
        if self.remove_segment_button:
            self.remove_segment_button.config(state=state)

        # Also clear the inputs when disabling the panel
        if not is_simple_graph:
            if self.node_name_entry: self.node_name_entry.delete(0, 'end')
            if self.node_x_entry: self.node_x_entry.delete(0, 'end')
            if self.node_y_entry: self.node_y_entry.delete(0, 'end')
            if self.segment_from_entry: self.segment_from_entry.delete(0, 'end')
            if self.segment_to_entry: self.segment_to_entry.delete(0, 'end')
            # Only clear status text if the widget exists
            if self.edit_status_text:
                self.edit_status_text.config(state='normal')
                self.edit_status_text.delete(1.0, 'end')
                self.edit_status_text.config(state='disabled')

    def _create_new_simple_graph(self):
        """Initializes an empty simple graph for editing."""
        # Stop any current visualization first
        self.stop_visualization()

        # Initialize an empty simple graph data structure
        self.current_graph_type = 'simple'
        self.current_graph_data = {'points': {}, 'segments': []}

        # Clear any previously loaded airspace data
        self.airspace = None

        self._log_edit_status("Initialized a new empty simple graph.")
        self._update_edit_panel_state() # Ensure panel is enabled
        
        # Visualize the empty graph (will just show axes)
        self._visualize_current_graph()

    def _visualize_current_graph(self):
        """Visualizes the currently loaded graph (airspace or simple)."""
        if self.current_graph_type == 'airspace':
            self.visualize_airspace() # Use the existing airspace visualization
        elif self.current_graph_type == 'simple':
            self._visualize_simple_graph()
        else:
            print("No graph loaded to visualize.") # Debug print

    def _visualize_simple_graph(self):
        """Visualizes the loaded simple graph in the main canvas."""
        if not self.current_graph_data or self.current_graph_type != 'simple':
            messagebox.showwarning("Visualization Error", "No simple graph data available to visualize.")
            return

        points = self.current_graph_data.get('points', {})
        segments = self.current_graph_data.get('segments', [])

        if not points:
            messagebox.showwarning("Visualization Error", "Simple graph has no points to visualize.")
            return

        try:
            # Clear previous canvas content and matplotlib figure/toolbar
            if self.canvas_widget:
                self.canvas_widget.destroy()
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            if self.toolbar:
                self.toolbar.destroy()
            if self.fig:
                plt.close(self.fig)
                self.fig = None
                self.ax = None

            # Create figure and axes for the plot
            # Set a reasonable figure size for matplotlib (in inches)
            fig_width, fig_height = 12, 9
            dpi = 100
            self.fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi, facecolor='white')
            self.ax = self.fig.add_subplot(111)

            # Plot points
            point_names = list(points.keys())
            x_coords = [points[name][0] for name in point_names]
            y_coords = [points[name][1] for name in point_names]
            
            if x_coords and y_coords:
                self.ax.scatter(x_coords, y_coords, c='blue', s=50, zorder=5)

                # Add labels to points
                for name, (x, y) in points.items():
                    self.ax.annotate(name, (x, y), textcoords="offset points", xytext=(0,10), ha='center')

            # Plot segments
            for p1_name, p2_name in segments:
                if p1_name in points and p2_name in points:
                    x1, y1 = points[p1_name]
                    x2, y2 = points[p2_name]
                    self.ax.plot([x1, x2], [y1, y2], 'r-', linewidth=1.5, zorder=1)
                else:
                    print(f"Skipping segment with unknown point(s): {p1_name}-{p2_name}") # Debug print

            # Set plot properties
            self.ax.set_title("Simple Loaded Graph") # Generic title for now
            self.ax.set_xlabel('X Coordinate')
            self.ax.set_ylabel('Y Coordinate')
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal', adjustable='box') # Ensure equal aspect ratio
            self.fig.tight_layout()

            # Embed the matplotlib canvas widget into the Tkinter canvas
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.airspace_canvas_frame)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.grid(row=1, column=0, sticky='nsew')

            # Create the navigation toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.airspace_canvas_frame)
            self.toolbar.update()

            # Redraw the canvas
            self.canvas.draw()

            print("Simple graph visualization complete.") # Debug print

        except Exception as e:
            error_msg = str(e)
            print(f"Simple graph visualization error: {e}") # Debug print the error
            messagebox.showerror("Visualization Error", f"Failed to visualize simple graph: {error_msg}")

    def _log_edit_status(self, message):
        """Helper to log messages to the editing status text area."""
        print(f"Attempting to log edit status: {message}")
        print(f"edit_status_text exists: {hasattr(self, 'edit_status_text')}")
        print(f"edit_status_text value: {self.edit_status_text if hasattr(self, 'edit_status_text') else 'None'}")
        
        if hasattr(self, 'edit_status_text') and self.edit_status_text:
            print("Updating edit status text widget")
            self.edit_status_text.config(state='normal')
            self.edit_status_text.insert('end', message + '\n')
            self.edit_status_text.see('end') # Auto-scroll to the end
            self.edit_status_text.config(state='disabled')
            print("Edit status text updated successfully")
        else:
            print("Warning: edit_status_text widget not available")

    def _add_node(self):
        """Add a node to the current simple graph."""
        if self.current_graph_type != 'simple' or not self.current_graph_data:
            self._log_edit_status("Error: No simple graph loaded.")
            messagebox.showwarning("Edit Error", "Please load a simple graph first.")
            return

        name = self.node_name_entry.get().strip()
        x_str = self.node_x_entry.get().strip()
        y_str = self.node_y_entry.get().strip()

        if not name or not x_str or not y_str:
            self._log_edit_status("Error: Node name, X, and Y are required.")
            messagebox.showwarning("Input Error", "Please enter node Name, X, and Y.")
            return

        try:
            x = float(x_str)
            y = float(y_str)
        except ValueError:
            self._log_edit_status(f"Error: Invalid coordinates for node {name}.")
            messagebox.showwarning("Input Error", "X and Y must be numbers.")
            return

        points = self.current_graph_data['points']

        if name in points:
            self._log_edit_status(f"Error: Node '{name}' already exists.")
            messagebox.showwarning("Edit Error", f"Node '{name}' already exists.")
            return

        points[name] = (x, y)
        self._log_edit_status(f"Added node '{name}' at ({x}, {y}).")
        self._visualize_current_graph() # Update visualization
        self.node_name_entry.delete(0, 'end')
        self.node_x_entry.delete(0, 'end')
        self.node_y_entry.delete(0, 'end')

    def _remove_node(self):
        """Remove a node and its associated segments from the current simple graph."""
        if self.current_graph_type != 'simple' or not self.current_graph_data:
            self._log_edit_status("Error: No simple graph loaded.")
            messagebox.showwarning("Edit Error", "Please load a simple graph first.")
            return

        name = self.node_name_entry.get().strip()

        if not name:
            self._log_edit_status("Error: Node name is required for removal.")
            messagebox.showwarning("Input Error", "Please enter the Name of the node to remove.")
            return

        points = self.current_graph_data['points']
        segments = self.current_graph_data['segments']

        if name not in points:
            self._log_edit_status(f"Error: Node '{name}' not found.")
            messagebox.showwarning("Edit Error", f"Node '{name}' not found.")
            return

        # Remove the node
        del points[name]
        self._log_edit_status(f"Removed node '{name}'.")

        # Remove segments connected to the node
        initial_segment_count = len(segments)
        segments[:] = [(p1, p2) for p1, p2 in segments if p1 != name and p2 != name]
        removed_segment_count = initial_segment_count - len(segments)
        if removed_segment_count > 0:
             self._log_edit_status(f"Removed {removed_segment_count} segment(s) connected to '{name}'.")

        self._visualize_current_graph() # Update visualization
        self.node_name_entry.delete(0, 'end')

    def _add_segment(self):
        """Add a segment to the current simple graph."""
        if self.current_graph_type != 'simple' or not self.current_graph_data:
            self._log_edit_status("Error: No simple graph loaded.")
            messagebox.showwarning("Edit Error", "Please load a simple graph first.")
            return

        from_name = self.segment_from_entry.get().strip()
        to_name = self.segment_to_entry.get().strip()

        if not from_name or not to_name:
            self._log_edit_status("Error: Start and end node names are required for adding a segment.")
            messagebox.showwarning("Input Error", "Please enter From and To node names.")
            return

        points = self.current_graph_data['points']
        segments = self.current_graph_data['segments']

        if from_name not in points or to_name not in points:
            self._log_edit_status(f"Error: One or both nodes ('{from_name}', '{to_name}') not found.")
            messagebox.showwarning("Edit Error", f"One or both nodes ('{from_name}', '{to_name}') not found.")
            return

        segment = (from_name, to_name)
        if segment in segments or (to_name, from_name) in segments: # Check for both directions
            self._log_edit_status(f"Error: Segment '{from_name}' to '{to_name}' already exists.")
            messagebox.showwarning("Edit Error", f"Segment '{from_name}' to '{to_name}' already exists.")
            return

        segments.append(segment)
        self._log_edit_status(f"Added segment '{from_name}' to '{to_name}'.")
        self._visualize_current_graph() # Update visualization
        self.segment_from_entry.delete(0, 'end')
        self.segment_to_entry.delete(0, 'end')

    def _remove_segment(self):
        """Remove a segment from the current simple graph."""
        if self.current_graph_type != 'simple' or not self.current_graph_data:
            self._log_edit_status("Error: No simple graph loaded.")
            messagebox.showwarning("Edit Error", "Please load a simple graph first.")
            return

        from_name = self.segment_from_entry.get().strip()
        to_name = self.segment_to_entry.get().strip()

        if not from_name or not to_name:
            self._log_edit_status("Error: Start and end node names are required for removing a segment.")
            messagebox.showwarning("Input Error", "Please enter From and To node names.")
            return

        segments = self.current_graph_data['segments']

        segment = (from_name, to_name)
        reverse_segment = (to_name, from_name)

        if segment in segments:
            segments.remove(segment)
            self._log_edit_status(f"Removed segment '{from_name}' to '{to_name}'.")
            self._visualize_current_graph() # Update visualization
        elif reverse_segment in segments:
             segments.remove(reverse_segment)
             self._log_edit_status(f"Removed segment '{to_name}' to '{from_name}'.")
             self._visualize_current_graph() # Update visualization
        else:
            self._log_edit_status(f"Error: Segment '{from_name}' to '{to_name}' not found.")
            messagebox.showwarning("Edit Error", f"Segment '{from_name}' to '{to_name}' not found.")
            
        self.segment_from_entry.delete(0, 'end')
        self.segment_to_entry.delete(0, 'end')

    def show_edit_panel(self):
        """Show the graph editing panel in a modal window."""
        print("\n=== Opening Edit Panel ===")
        # Create modal window
        edit_window = self.create_modal_window("Graph Editor", 400, 600)
        print("Edit window created")

        # Create main frame with padding
        main_frame = ttk.Frame(edit_window, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        edit_window.grid_rowconfigure(0, weight=1)
        edit_window.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        print("Main frame created and configured")

        # Node editing section
        node_frame = ttk.LabelFrame(main_frame, text="Node Editing", padding="5")
        node_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        node_frame.grid_columnconfigure(1, weight=1)
        print("Node frame created")

        # Node name
        ttk.Label(node_frame, text="Name:").grid(row=0, column=0, padx=5, pady=2)
        self.node_name_entry = ttk.Entry(node_frame, width=20)
        self.node_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        # Node X coordinate
        ttk.Label(node_frame, text="X:").grid(row=1, column=0, padx=5, pady=2)
        self.node_x_entry = ttk.Entry(node_frame, width=20)
        self.node_x_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        # Node Y coordinate
        ttk.Label(node_frame, text="Y:").grid(row=2, column=0, padx=5, pady=2)
        self.node_y_entry = ttk.Entry(node_frame, width=20)
        self.node_y_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew')

        # Node buttons
        node_button_frame = ttk.Frame(node_frame)
        node_button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        node_button_frame.grid_columnconfigure(0, weight=1)
        node_button_frame.grid_columnconfigure(1, weight=1)

        self.add_node_button = ttk.Button(node_button_frame, text="Add Node", command=self._add_node)
        self.add_node_button.grid(row=0, column=0, padx=5)
        self.remove_node_button = ttk.Button(node_button_frame, text="Remove Node", command=self._remove_node)
        self.remove_node_button.grid(row=0, column=1, padx=5)
        print("Node controls created")

        # Segment editing section
        segment_frame = ttk.LabelFrame(main_frame, text="Segment Editing", padding="5")
        segment_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        segment_frame.grid_columnconfigure(1, weight=1)
        print("Segment frame created")

        # Segment from
        ttk.Label(segment_frame, text="From:").grid(row=0, column=0, padx=5, pady=2)
        self.segment_from_entry = ttk.Entry(segment_frame, width=20)
        self.segment_from_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        # Segment to
        ttk.Label(segment_frame, text="To:").grid(row=1, column=0, padx=5, pady=2)
        self.segment_to_entry = ttk.Entry(segment_frame, width=20)
        self.segment_to_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        # Segment buttons
        segment_button_frame = ttk.Frame(segment_frame)
        segment_button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        segment_button_frame.grid_columnconfigure(0, weight=1)
        segment_button_frame.grid_columnconfigure(1, weight=1)

        self.add_segment_button = ttk.Button(segment_button_frame, text="Add Segment", command=self._add_segment)
        self.add_segment_button.grid(row=0, column=0, padx=5)
        self.remove_segment_button = ttk.Button(segment_button_frame, text="Remove Segment", command=self._remove_segment)
        self.remove_segment_button.grid(row=0, column=1, padx=5)
        print("Segment controls created")

        # Status text area
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        print("Status frame created")

        self.edit_status_text = tk.Text(status_frame, wrap='word', state='disabled', height=10)
        self.edit_status_text.grid(row=0, column=0, sticky='nsew')
        status_scroll = ttk.Scrollbar(status_frame, orient='vertical', command=self.edit_status_text.yview)
        status_scroll.grid(row=0, column=1, sticky='ns')
        self.edit_status_text.configure(yscrollcommand=status_scroll.set)
        print("Status text area created")

        # Add save button
        save_button = ttk.Button(main_frame, text="Save Graph", command=self._save_graph)
        save_button.grid(row=3, column=0, pady=10)
        print("Save button created")

        # Update panel state based on current graph type
        self._update_edit_panel_state()
        print("Edit panel state updated")

        # Log initial status
        if self.current_graph_type == 'simple':
            self._log_edit_status("Simple graph editor ready.")
        else:
            self._log_edit_status("Airspace graph editor ready.")
        print("=== Edit Panel Setup Complete ===\n")

    def _save_graph(self):
        """Save the current graph to a file in the same format as imported files."""
        if not self.current_graph_data or self.current_graph_type != 'simple':
            self._log_edit_status("Error: No simple graph data to save.")
            return

        try:
            # Open file dialog to choose save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Graph As"
            )
            
            if not file_path:  # User cancelled
                return

            # Get the graph data
            points = self.current_graph_data['points']
            segments = self.current_graph_data['segments']

            # Write the data in the same format as imported files
            with open(file_path, 'w') as f:
                # Write points
                for name, (x, y) in points.items():
                    f.write(f"{name} {x} {y}\n")
                
                # Write segments
                for p1, p2 in segments:
                    f.write(f"{p1} {p2}\n")

            self._log_edit_status(f"Graph saved successfully to: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"Graph saved to:\n{file_path}")

        except Exception as e:
            error_msg = str(e)
            self._log_edit_status(f"Error saving graph: {error_msg}")
            messagebox.showerror("Save Error", f"Failed to save graph: {error_msg}")

    def show_photo_group(self):
        """Show the photo group images in a new window."""
        print("\n=== Opening Photo Group Window ===")
        
        # Create a new window
        photo_window = tk.Toplevel(self.root)
        photo_window.title("Photo Group")
        
        # Get screen dimensions
        screen_width = photo_window.winfo_screenwidth()
        screen_height = photo_window.winfo_screenheight()
        
        # Set window size to 80% of screen
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        photo_window.geometry(f"{window_width}x{window_height}")
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        photo_window.geometry(f"+{x}+{y}")
        
        # Create a frame to hold the images
        frame = ttk.Frame(photo_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        try:
            # Get the path to the Photo_group directory
            photo_dir = os.path.join(os.path.dirname(__file__), 'Photo_group')
            print(f"Looking for images in: {photo_dir}")
            
            # Get all image files
            image_files = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            print(f"Found {len(image_files)} images")
            
            if not image_files:
                messagebox.showwarning("No Images", "No images found in the Photo_group directory.")
                return
            
            # Calculate target size for all images
            target_width = window_width // 3 - 40  # Divide by 3 for three images, subtract padding
            target_height = window_height - 60  # Subtract padding
            
            # Load and display each image
            for i, image_file in enumerate(image_files):
                try:
                    # Load the image
                    image_path = os.path.join(photo_dir, image_file)
                    print(f"Loading image: {image_path}")
                    
                    # Open and resize the image
                    img = Image.open(image_path)
                    
                    # Calculate aspect ratio
                    aspect_ratio = img.width / img.height
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    if aspect_ratio > 1:  # Wider than tall
                        new_width = target_width
                        new_height = int(target_width / aspect_ratio)
                        if new_height > target_height:
                            new_height = target_height
                            new_width = int(target_height * aspect_ratio)
                    else:  # Taller than wide
                        new_height = target_height
                        new_width = int(target_height * aspect_ratio)
                        if new_width > target_width:
                            new_width = target_width
                            new_height = int(target_width / aspect_ratio)
                    
                    # Resize image
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create a new image with the target size and white background
                    final_img = Image.new('RGB', (target_width, target_height), 'white')
                    
                    # Calculate position to center the resized image
                    x_offset = (target_width - new_width) // 2
                    y_offset = (target_height - new_height) // 2
                    
                    # Paste the resized image onto the white background
                    final_img.paste(img, (x_offset, y_offset))
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(final_img)
                    
                    # Create label for the image
                    label = ttk.Label(frame, image=photo)
                    label.image = photo  # Keep a reference!
                    label.grid(row=0, column=i, padx=5, pady=5)
                    
                    print(f"Displayed image {i+1}: {image_file}")
                    
                except Exception as e:
                    print(f"Error loading image {image_file}: {str(e)}")
                    continue
            
            print("=== Photo Group Window Setup Complete ===\n")
            
        except Exception as e:
            print(f"Error setting up photo group window: {str(e)}")
            messagebox.showerror("Error", f"Failed to display images: {str(e)}")
            photo_window.destroy()

    def show_extra_features(self):
        """Show a window with extra features information."""
        # Create a new window
        features_window = tk.Toplevel(self.root)
        features_window.title("Extra Features")
        
        # Set window size and position
        window_width = 600
        window_height = 400
        screen_width = features_window.winfo_screenwidth()
        screen_height = features_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        features_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window modal
        features_window.transient(self.root)
        features_window.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(features_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', padx=10, pady=10)
        text_widget.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Insert the text
        features_text = """Extra features:

- You can see the map behind the points of the airspace area.
- You can zoom in and out in the graph.
- Ones zoomed in, you can drag and explore the map zoomed in.

- In the Show Path Finding features, ones you search for the path, you can see the distance, time and fuel comsumption. Assuming that we are flying with an A320."""
        
        text_widget.insert('1.0', features_text)
        text_widget.configure(state='disabled')  # Make text read-only
        
        # Add close button
        close_button = ttk.Button(main_frame, text="Close", command=features_window.destroy)
        close_button.pack(pady=10)


def main():
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    