import tkinter as tk
from tkinter import messagebox, ttk
from graph import *
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import os
from airSpace import AirSpace
import io
from navPoint import GetNavPointByNumber

class AirspaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Explorer")
        # Start maximized
        self.root.state('zoomed')  # For Windows
        self.airspace = None
        self.airspace_image = None
        self.visualization_running = False  # Flag to track visualization state
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Add debouncing for resize events
        self._resize_timer = None
        self._last_resize_time = 0
        self._resize_delay = 250  # milliseconds
        
        # Wait for window to be ready
        self.root.update_idletasks()
        
        self.setup_ui()
        
        # Bind resize event with debouncing
        self.root.bind('<Configure>', self.on_window_resize)
        
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
        # Configure grid weights for the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.grid(row=0, column=0, sticky='nsew')
        
        self.tab_main = ttk.Frame(self.tab_control)
        self.tab_info = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_main, text='Main')
        self.tab_control.add(self.tab_info, text='Airspace Info')

        # Configure grid weights for tabs
        self.tab_main.grid_rowconfigure(1, weight=1)
        self.tab_main.grid_columnconfigure(0, weight=1)
        self.tab_info.grid_rowconfigure(1, weight=1)
        self.tab_info.grid_columnconfigure(0, weight=1)

        # Main tab: Load and visualize
        frame = ttk.Frame(self.tab_main)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        # Add airspace selection dropdown
        ttk.Label(frame, text="Select Airspace:").pack(side='left', padx=5)
        self.airspace_var = tk.StringVar(value="Catalunya")
        self.airspace_dropdown = ttk.Combobox(frame, textvariable=self.airspace_var, 
                                            values=["Catalunya", "España", "Europe"],
                                            state="readonly", width=15)
        self.airspace_dropdown.pack(side='left', padx=5)
        
        self.load_button = ttk.Button(frame, text="Load Selected Airspace", command=self.load_selected_airspace)
        self.load_button.pack(side='left', padx=5)
        self.visualize_button = ttk.Button(frame, text="Visualize Airspace", command=self.visualize_airspace, state='disabled')
        self.visualize_button.pack(side='left', padx=5)
        self.stop_visualize_button = ttk.Button(frame, text="Stop Visualization", command=self.stop_visualization, state='disabled')
        self.stop_visualize_button.pack(side='left', padx=5)
        self.status_label = ttk.Label(frame, text="Status: Waiting for data load...")
        self.status_label.pack(side='left', padx=10)

        # --- Redesigned Airspace Info tab layout ---
        # Main container for info tab
        info_main = ttk.Frame(self.tab_info)
        info_main.pack(fill='both', expand=True, padx=10, pady=10)
        info_main.grid_rowconfigure(0, weight=1)
        info_main.grid_columnconfigure(1, weight=1)

        # Left vertical info panel with neighbors button
        info_panel = ttk.LabelFrame(info_main, text="Airspace Information", padding="10")
        info_panel.grid(row=0, column=0, sticky='ns', padx=5, pady=5)
        info_panel.grid_propagate(False)
        info_panel.grid_rowconfigure(1, weight=1)
        info_panel.grid_columnconfigure(0, weight=1)

        # Add Show Neighbors button at the top of the info panel
        neighbors_frame = ttk.Frame(info_panel)
        neighbors_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        neighbors_frame.grid_columnconfigure(0, weight=1)
        
        self.show_neighbors_button = ttk.Button(neighbors_frame, 
                                              text="Show Neighbors", 
                                              command=self.show_neighbors, 
                                              style='Custom.TButton',
                                              width=20)
        self.show_neighbors_button.grid(row=0, column=0, sticky='ew')
        print("Show Neighbors button created and placed")  # Debug print

        # Info text area
        text_frame = ttk.Frame(info_panel)
        text_frame.grid(row=1, column=0, sticky='nsew')
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(text_frame, wrap='word', state='disabled', width=36)
        self.info_text.grid(row=0, column=0, sticky='nsew')
        info_scroll = ttk.Scrollbar(text_frame, orient='vertical', command=self.info_text.yview)
        info_scroll.grid(row=0, column=1, sticky='ns')
        self.info_text.configure(yscrollcommand=info_scroll.set)

        # Main area (functions bar at top, canvas below)
        main_area = ttk.Frame(info_main)
        main_area.grid(row=0, column=1, sticky='nsew')
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        # --- Path Finding Features Bar (top of main area) ---
        v2_frame = ttk.LabelFrame(main_area, text="Path Finding Features", padding="10")
        v2_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10,0))
        v2_frame.grid_columnconfigure(0, weight=1)
        v2_frame.grid_columnconfigure(1, weight=1)

        # Reachability controls
        reach_frame = ttk.Frame(v2_frame)
        reach_frame.grid(row=0, column=0, sticky='ew', padx=5)
        ttk.Label(reach_frame, text="Reachability: Start point").pack(side='left', padx=5)
        self.reach_point_var = tk.StringVar(reach_frame)
        self.reach_point_dropdown = ttk.Combobox(reach_frame, textvariable=self.reach_point_var, state="readonly", width=20)
        self.reach_point_dropdown.pack(side='left', padx=5)
        ttk.Button(reach_frame, text="Show", command=self._show_reachability).pack(side='left', padx=5)

        # Add Show Neighbors button to reachability frame
        self.show_neighbors_button = ttk.Button(reach_frame, 
                                              text="Show Neighbors", 
                                              command=self.show_neighbors, 
                                              style='Custom.TButton')
        self.show_neighbors_button.pack(side='left', padx=5)

        # Reachability result/status (scrollable, fixed height)
        reach_status_frame = ttk.Frame(v2_frame)
        reach_status_frame.grid(row=1, column=0, sticky='ew', padx=5)
        self.reach_status_text = tk.Text(reach_status_frame, height=4, wrap='word', state='disabled', width=60)
        self.reach_status_text.pack(side='left', fill='x', expand=True)
        reach_status_scroll = ttk.Scrollbar(reach_status_frame, orient='vertical', command=self.reach_status_text.yview)
        reach_status_scroll.pack(side='left', fill='y')
        self.reach_status_text.configure(yscrollcommand=reach_status_scroll.set)

        # Shortest path controls
        path_frame = ttk.Frame(v2_frame)
        path_frame.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(path_frame, text="Shortest Path: Origin").pack(side='left', padx=5)
        self.path_origin_var = tk.StringVar(path_frame)
        self.path_origin_dropdown = ttk.Combobox(path_frame, textvariable=self.path_origin_var, state="readonly", width=20)
        self.path_origin_dropdown.pack(side='left', padx=5)
        ttk.Label(path_frame, text="Destination").pack(side='left', padx=5)
        self.path_dest_var = tk.StringVar(path_frame)
        self.path_dest_dropdown = ttk.Combobox(path_frame, textvariable=self.path_dest_var, state="readonly", width=20)
        self.path_dest_dropdown.pack(side='left', padx=5)
        ttk.Button(path_frame, text="Find", command=self._find_path).pack(side='left', padx=5)

        # Shortest path result/status (scrollable, fixed height)
        path_status_frame = ttk.Frame(v2_frame)
        path_status_frame.grid(row=1, column=1, sticky='ew', padx=5)
        self.path_status_text = tk.Text(path_status_frame, height=4, wrap='word', state='disabled', width=60)
        self.path_status_text.pack(side='left', fill='x', expand=True)
        path_status_scroll = ttk.Scrollbar(path_status_frame, orient='vertical', command=self.path_status_text.yview)
        path_status_scroll.pack(side='left', fill='y')
        self.path_status_text.configure(yscrollcommand=path_status_scroll.set)

        # --- Graph/Canvas visualization (fills rest of main area) ---
        canvas_frame = ttk.Frame(main_area)
        canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        self.airspace_canvas = tk.Canvas(canvas_frame, bg='white')
        self.airspace_canvas.grid(row=0, column=0, sticky='nsew')
        y_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.airspace_canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.airspace_canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        self.airspace_canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

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
        self.visualize_airspace()

    def update_v2_dropdowns(self):
        # Helper to update dropdowns for navpoints
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
        try:
            selected_airspace = self.airspace_var.get()
            # Map display names to directory names
            dir_names = {
                "Catalunya": "airspace_catalonia",
                "España": "Airspace Spain",
                "Europe": "ECAC airspace"
            }
            base_dir = os.path.join(os.path.dirname(__file__), dir_names[selected_airspace])
            
            # Define file patterns for each airspace
            file_patterns = {
                "Catalunya": ("Cat_nav.txt", "Cat_seg.txt", "Cat_aer.txt"),
                "España": ("Spain_nav.txt", "Spain_seg.txt", "Spain_aer.txt"),
                "Europe": ("ECAC_nav.txt", "ECAC_seg.txt", "ECAC_aer.txt")
            }
            
            # Disable buttons during loading
            self.load_button.configure(state='disabled')
            self.visualize_button.configure(state='disabled')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()
            
            # Handle Spain airspace data which is in a zip file
            temp_dir = None
            if selected_airspace == "España":
                self.status_label.config(text="Extracting Spain airspace data...")
                self.root.update_idletasks()
                
                zip_path = os.path.join(base_dir, "Spain_graph.zip")
                if not os.path.exists(zip_path):
                    raise FileNotFoundError("Spain airspace data zip file not found.")
                    
                # Create a temporary directory for extracted files
                import tempfile
                import zipfile
                temp_dir = tempfile.mkdtemp()
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    base_dir = temp_dir  # Use the temporary directory for file paths
                except Exception as e:
                    raise Exception(f"Failed to extract Spain airspace data: {str(e)}")
            
            # Verify all required files exist
            nav_file = os.path.join(base_dir, file_patterns[selected_airspace][0])
            seg_file = os.path.join(base_dir, file_patterns[selected_airspace][1])
            aer_file = os.path.join(base_dir, file_patterns[selected_airspace][2])
            
            for file_path in [nav_file, seg_file, aer_file]:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Required file not found: {os.path.basename(file_path)}")
            
            self.status_label.config(text=f"Loading {selected_airspace} airspace data...")
            self.root.update_idletasks()
            
            # Create new airspace instance
            self.airspace = AirSpace(name=selected_airspace)
            
            # Load data with timeout
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def load_data_thread():
                try:
                    success = self.airspace.load_data(nav_file, seg_file, aer_file)
                    result_queue.put(("success", success))
                except Exception as e:
                    result_queue.put(("error", str(e)))
            
            # Start loading in a separate thread
            thread = threading.Thread(target=load_data_thread)
            thread.daemon = True
            thread.start()
            
            # Wait for result with timeout
            try:
                result_type, result = result_queue.get(timeout=30)  # 30 second timeout
                if result_type == "error":
                    raise Exception(result)
                if not result:
                    raise Exception(f"Failed to load {selected_airspace} airspace data.")
            except queue.Empty:
                raise Exception("Loading timed out after 30 seconds")
            
            self.status_label.config(text=f"Status: {selected_airspace} airspace loaded.")
            self.visualize_button.config(state='normal')
            self.show_airspace_info()
            self.update_v2_dropdowns()
            
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Failed to load {selected_airspace} airspace data: {error_msg}")
            self.status_label.config(text="Status: Failed to load data.")
            self.visualize_button.config(state='disabled')
            
        finally:
            # Clean up temporary directory for Spain airspace
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except:
                    pass  # Ignore cleanup errors
            
            # Re-enable buttons
            self.load_button.configure(state='normal')
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def show_airspace_info(self):
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
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, 'end')
        self.info_text.insert('end', '\n'.join(info))
        self.info_text.config(state='disabled')

    def show_neighbors(self):
        """Show neighbors of selected node in the current airspace"""
        if not self.airspace or not self.airspace.nav_points:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        window = self.create_modal_window("Show Neighbors", 400, 300)
        
        # Create frame with padding
        frame = ttk.Frame(window, style='Padded.TFrame')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Node selection
        ttk.Label(frame, text="Select node:", style='Custom.TLabel').pack(fill='x')
        node_var = tk.StringVar(window)
        node_names = [f"{point.number} ({point.name})" for point in self.airspace.nav_points]
        node_dropdown = ttk.Combobox(frame, textvariable=node_var, values=node_names, state="readonly")
        node_dropdown.pack(fill='x', pady=(0, 10))
        if node_names:
            node_dropdown.set(node_names[0])
        
        # Results text area
        result_text = tk.Text(frame, height=10, wrap='word', state='disabled')
        result_text.pack(fill='both', expand=True, pady=5)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=result_text.yview)
        scrollbar.pack(side='right', fill='y')
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
                  style='Dialog.TButton').pack(fill='x', pady=(10, 0))

    def visualize_airspace(self):
        """Visualize the airspace with proper error handling and state management"""
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
            plt.close(fig)
            buf.seek(0)

            # Check if visualization was stopped
            if not self.visualization_running:
                return

            # Update status
            self.status_label.config(text="Status: Loading image...")
            self.root.update_idletasks()

            # Load and display the image
            img = Image.open(buf)
            
            # Calculate new dimensions maintaining aspect ratio
            canvas_width = self.airspace_canvas.winfo_width()
            canvas_height = self.airspace_canvas.winfo_height()
            
            # Calculate maximum dimensions (90% of frame size)
            max_width = int(canvas_width * 0.9)
            max_height = int(canvas_height * 0.9)
            
            # Calculate new dimensions maintaining aspect ratio
            width, height = img.size
            if width > height:
                new_width = min(width, max_width)
                new_height = int(height * (new_width / width))
            else:
                new_height = min(height, max_height)
                new_width = int(width * (new_height / height))
            
            # Ensure minimum size
            new_width = max(new_width, 400)
            new_height = max(new_height, 300)
            
            # Resize image for better performance
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.airspace_image = ImageTk.PhotoImage(img)

            # Center the image in the canvas
            x = max((canvas_width - new_width) // 2, 0)
            y = max((canvas_height - new_height) // 2, 0)
            self.airspace_canvas.delete('all')
            self.airspace_canvas.create_image(x, y, anchor='nw', image=self.airspace_image)
            self.airspace_canvas.configure(scrollregion=self.airspace_canvas.bbox('all'))
            buf.close()

            # Update status
            self.status_label.config(text=f"Status: {self.airspace.name} airspace visualization complete.")

        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Failed to visualize airspace: {error_msg}")
            plt.close('all')
        finally:
            # Reset visualization state and button states
            self.visualization_running = False
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def show_v2_features(self):
        """Show a modal window demonstrating V2 features (reachability and shortest path) using current airspace data, without extra explanations."""
        if not self.airspace:
            messagebox.showwarning("No Data", "Please load airspace data first.")
            return

        window = tk.Toplevel(self.root)
        window.title("Path Finding Features")
        window.geometry('1000x800')
        window.transient(self.root)
        
        # Center the window
        x = self.root.winfo_x() + (self.root.winfo_width() - 1000) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 800) // 2
        window.geometry(f'+{x}+{y}')
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Reachability tab
        reachability_frame = ttk.Frame(notebook, padding="10")
        notebook.add(reachability_frame, text="Reachability Analysis")
        
        # Controls only, no description
        example_frame = ttk.LabelFrame(reachability_frame, text="Airspace Reachability", padding="10")
        example_frame.pack(fill='both', expand=True)
        
        control_frame = ttk.Frame(example_frame)
        control_frame.pack(fill='x', pady=5)
        
        ttk.Label(control_frame, text="Select start point:").pack(side='left', padx=5)
        point_var = tk.StringVar(control_frame)
        point_names = [f"{point.number} ({point.name})" for point in self.airspace.nav_points]
        point_dropdown = ttk.Combobox(control_frame, textvariable=point_var, 
                                    values=point_names, state="readonly", width=20)
        point_dropdown.pack(side='left', padx=5)
        if point_names:
            point_dropdown.set(point_names[0])
        
        canvas_frame = ttk.Frame(example_frame)
        canvas_frame.pack(fill='both', expand=True, pady=5)
        y_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical')
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        canvas = tk.Canvas(canvas_frame, bg='white',
                         yscrollcommand=y_scrollbar.set,
                         xscrollcommand=x_scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        y_scrollbar.config(command=canvas.yview)
        x_scrollbar.config(command=canvas.xview)
        
        def show_reachability():
            try:
                point_info = point_var.get()
                point_number = int(point_info.split()[0])
                start_point = self.airspace.get_nav_point(point_number)
                if not start_point:
                    raise ValueError(f"Point {point_number} not found")
                fig = self.airspace.plot(
                    show_points=True,
                    show_segments=True,
                    show_airports=True,
                    figsize=(12, 9),
                    point_color='blue',
                    segment_color='gray',
                    airport_color='red',
                    point_size=30,
                    segment_width=0.5,
                    airport_size=150,
                    point_alpha=0.7,
                    segment_alpha=0.3,
                    airport_alpha=0.9
                )
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
                ax = fig.axes[0]
                for point in reachable:
                    ax.plot(point.longitude, point.latitude, 'go', 
                           markersize=15, alpha=0.6, label='Reachable' if point == start_point else "")
                ax.plot(start_point.longitude, start_point.latitude, 'ro',
                       markersize=20, alpha=0.8, label='Start Point')
                ax.legend(['Airport', 'Reachable', 'Start Point'], 
                         loc='upper right', fontsize='small')
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close(fig)
                buf.seek(0)
                img = Image.open(buf)
                photo = ImageTk.PhotoImage(img)
                canvas.delete('all')
                canvas.create_image(0, 0, anchor='nw', image=photo)
                canvas.image = photo
                canvas.configure(scrollregion=canvas.bbox('all'))
                reachable_names = [f"{p.number} ({p.name})" for p in reachable]
                status_text = f"From point {point_number}, you can reach {len(reachable)} points:\n" + \
                            ", ".join(reachable_names)
                self.reach_status_text.config(state='normal')
                self.reach_status_text.delete(1.0, 'end')
                self.reach_status_text.insert('end', status_text)
                self.reach_status_text.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(control_frame, text="Show Reachability", 
                  command=show_reachability).pack(side='left', padx=5)
        
        # Shortest Path tab
        path_frame = ttk.Frame(notebook, padding="10")
        notebook.add(path_frame, text="Shortest Path (A*)")
        path_example_frame = ttk.LabelFrame(path_frame, text="Airspace Shortest Path", padding="10")
        path_example_frame.pack(fill='both', expand=True)
        path_control_frame = ttk.Frame(path_example_frame)
        path_control_frame.pack(fill='x', pady=5)
        ttk.Label(path_control_frame, text="Origin:").pack(side='left', padx=5)
        origin_var = tk.StringVar(path_control_frame)
        origin_dropdown = ttk.Combobox(path_control_frame, textvariable=origin_var,
                                     values=point_names, state="readonly", width=20)
        origin_dropdown.pack(side='left', padx=5)
        if point_names:
            origin_dropdown.set(point_names[0])
        ttk.Label(path_control_frame, text="Destination:").pack(side='left', padx=5)
        dest_var = tk.StringVar(path_control_frame)
        dest_dropdown = ttk.Combobox(path_control_frame, textvariable=dest_var,
                                   values=point_names, state="readonly", width=20)
        dest_dropdown.pack(side='left', padx=5)
        if point_names:
            dest_dropdown.set(point_names[-1])
        path_canvas_frame = ttk.Frame(path_example_frame)
        path_canvas_frame.pack(fill='both', expand=True, pady=5)
        path_y_scrollbar = ttk.Scrollbar(path_canvas_frame, orient='vertical')
        path_y_scrollbar.pack(side='right', fill='y')
        path_x_scrollbar = ttk.Scrollbar(path_canvas_frame, orient='horizontal')
        path_x_scrollbar.pack(side='bottom', fill='x')
        path_canvas = tk.Canvas(path_canvas_frame, bg='white',
                              yscrollcommand=path_y_scrollbar.set,
                              xscrollcommand=path_x_scrollbar.set)
        path_canvas.pack(side='left', fill='both', expand=True)
        path_y_scrollbar.config(command=path_canvas.yview)
        path_x_scrollbar.config(command=path_canvas.xview)
        def find_path():
            try:
                origin_info = origin_var.get()
                dest_info = dest_var.get()
                origin_number = int(origin_info.split()[0])
                dest_number = int(dest_info.split()[0])
                origin = self.airspace.get_nav_point(origin_number)
                destination = self.airspace.get_nav_point(dest_number)
                if not origin or not destination:
                    raise ValueError("Selected points not found")
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
                while open_set:
                    current_number = min(open_set, key=lambda x: f_score.get(x, float('inf')))
                    current = self.airspace.get_nav_point(current_number)
                    if current_number == destination.number:
                        path = []
                        while current_number in came_from:
                            path.append(self.airspace.get_nav_point(current_number))
                            current_number = came_from[current_number]
                        path.append(origin)
                        path.reverse()
                        fig = self.airspace.plot(
                            show_points=True,
                            show_segments=True,
                            show_airports=True,
                            figsize=(12, 9),
                            point_color='blue',
                            segment_color='gray',
                            airport_color='red',
                            point_size=30,
                            segment_width=0.5,
                            airport_size=150,
                            point_alpha=0.7,
                            segment_alpha=0.3,
                            airport_alpha=0.9
                        )
                        ax = fig.axes[0]
                        path_lons = [p.longitude for p in path]
                        path_lats = [p.latitude for p in path]
                        ax.plot(path_lons, path_lats, 'r-', linewidth=2, alpha=0.8, label='Path')
                        ax.plot(origin.longitude, origin.latitude, 'go',
                               markersize=20, alpha=0.8, label='Start')
                        ax.plot(destination.longitude, destination.latitude, 'mo',
                               markersize=20, alpha=0.8, label='End')
                        ax.legend(['Airport', 'Path', 'Start', 'End'], 
                                 loc='upper right', fontsize='small')
                        total_distance = sum(get_cost(path[i], path[i+1]) 
                                          for i in range(len(path)-1))
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                        plt.close(fig)
                        buf.seek(0)
                        img = Image.open(buf)
                        photo = ImageTk.PhotoImage(img)
                        path_canvas.delete('all')
                        path_canvas.create_image(0, 0, anchor='nw', image=photo)
                        path_canvas.image = photo
                        path_canvas.configure(scrollregion=path_canvas.bbox('all'))
                        path_points = [f"{p.number} ({p.name})" for p in path]
                        status_text = f"Path: {' -> '.join(path_points)}\n" + \
                                    f"Total distance: {total_distance:.2f} km"
                        self.path_status_text.config(state='normal')
                        self.path_status_text.delete(1.0, 'end')
                        self.path_status_text.insert('end', status_text)
                        self.path_status_text.config(state='disabled')
                        return
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
                self.path_status_text.config(state='normal')
                self.path_status_text.delete(1.0, 'end')
                self.path_status_text.insert('end', f"No path found from {origin_number} to {dest_number}")
                self.path_status_text.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(path_control_frame, text="Find Path", 
                  command=find_path).pack(side='left', padx=5)

    def _show_reachability(self):
        if not self.airspace or not self.airspace.nav_points:
            self.reach_status_text.config(state='normal')
            self.reach_status_text.delete(1.0, 'end')
            self.reach_status_text.insert('end', "No airspace data loaded.")
            self.reach_status_text.config(state='disabled')
            return
        point_info = self.reach_point_var.get()
        if not point_info:
            self.reach_status_text.config(state='normal')
            self.reach_status_text.delete(1.0, 'end')
            self.reach_status_text.insert('end', "Select a start point.")
            self.reach_status_text.config(state='disabled')
            return
        point_number = int(point_info.split()[0])
        start_point = self.airspace.get_nav_point(point_number)
        if not start_point:
            self.reach_status_text.config(state='normal')
            self.reach_status_text.delete(1.0, 'end')
            self.reach_status_text.insert('end', f"Point {point_number} not found.")
            self.reach_status_text.config(state='disabled')
            return

        # Set visualization state to prevent automatic redraw
        self.visualization_running = True
        
        try:
            fig = self.airspace.plot(
                show_points=True,
                show_segments=True,
                show_airports=True,
                figsize=(12, 9),
                point_color='blue',
                segment_color='gray',
                airport_color='red',
                point_size=30,
                segment_width=0.5,
                airport_size=150,
                point_alpha=0.7,
                segment_alpha=0.3,
                airport_alpha=0.9
            )
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
            ax = fig.axes[0]
            for point in reachable:
                ax.plot(point.longitude, point.latitude, 'go', 
                       markersize=15, alpha=0.6, label='Reachable' if point == start_point else "")
            ax.plot(start_point.longitude, start_point.latitude, 'ro',
                   markersize=20, alpha=0.8, label='Start Point')
            ax.legend(['Airport', 'Reachable', 'Start Point'], 
                     loc='upper right', fontsize='small')
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img = Image.open(buf)
            photo = ImageTk.PhotoImage(img)
            self.airspace_canvas.delete('all')
            self.airspace_canvas.create_image(0, 0, anchor='nw', image=photo)
            self.airspace_canvas.image = photo
            self.airspace_canvas.configure(scrollregion=self.airspace_canvas.bbox('all'))
            reachable_names = [f"{p.number} ({p.name})" for p in reachable]
            status_text = f"From point {point_number}, you can reach {len(reachable)} points:\n" + \
                        ", ".join(reachable_names)
            self.reach_status_text.config(state='normal')
            self.reach_status_text.delete(1.0, 'end')
            self.reach_status_text.insert('end', status_text)
            self.reach_status_text.config(state='disabled')
        finally:
            # Reset visualization state
            self.visualization_running = False

    def _find_path(self):
        if not self.airspace or not self.airspace.nav_points:
            self.path_status_text.config(state='normal')
            self.path_status_text.delete(1.0, 'end')
            self.path_status_text.insert('end', "No airspace data loaded.")
            self.path_status_text.config(state='disabled')
            return
        origin_info = self.path_origin_var.get()
        dest_info = self.path_dest_var.get()
        if not origin_info or not dest_info:
            self.path_status_text.config(state='normal')
            self.path_status_text.delete(1.0, 'end')
            self.path_status_text.insert('end', "Select both origin and destination.")
            self.path_status_text.config(state='disabled')
            return
        origin_number = int(origin_info.split()[0])
        dest_number = int(dest_info.split()[0])
        origin = self.airspace.get_nav_point(origin_number)
        destination = self.airspace.get_nav_point(dest_number)
        if not origin or not destination:
            self.path_status_text.config(state='normal')
            self.path_status_text.delete(1.0, 'end')
            self.path_status_text.insert('end', "Selected points not found.")
            self.path_status_text.config(state='disabled')
            return

        # Set visualization state to prevent automatic redraw
        self.visualization_running = True
        
        try:
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
            while open_set:
                current_number = min(open_set, key=lambda x: f_score.get(x, float('inf')))
                current = self.airspace.get_nav_point(current_number)
                if current_number == destination.number:
                    path = []
                    while current_number in came_from:
                        path.append(self.airspace.get_nav_point(current_number))
                        current_number = came_from[current_number]
                    path.append(origin)
                    path.reverse()
                    fig = self.airspace.plot(
                        show_points=True,
                        show_segments=True,
                        show_airports=True,
                        figsize=(12, 9),
                        point_color='blue',
                        segment_color='gray',
                        airport_color='red',
                        point_size=30,
                        segment_width=0.5,
                        airport_size=150,
                        point_alpha=0.7,
                        segment_alpha=0.3,
                        airport_alpha=0.9
                    )
                    ax = fig.axes[0]
                    path_lons = [p.longitude for p in path]
                    path_lats = [p.latitude for p in path]
                    ax.plot(path_lons, path_lats, 'r-', linewidth=2, alpha=0.8, label='Path')
                    ax.plot(origin.longitude, origin.latitude, 'go',
                           markersize=20, alpha=0.8, label='Start')
                    ax.plot(destination.longitude, destination.latitude, 'mo',
                           markersize=20, alpha=0.8, label='End')
                    ax.legend(['Airport', 'Path', 'Start', 'End'], 
                             loc='upper right', fontsize='small')
                    total_distance = sum(get_cost(path[i], path[i+1]) 
                                      for i in range(len(path)-1))
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                    plt.close(fig)
                    buf.seek(0)
                    img = Image.open(buf)
                    photo = ImageTk.PhotoImage(img)
                    self.airspace_canvas.delete('all')
                    self.airspace_canvas.create_image(0, 0, anchor='nw', image=photo)
                    self.airspace_canvas.image = photo
                    self.airspace_canvas.configure(scrollregion=self.airspace_canvas.bbox('all'))
                    path_points = [f"{p.number} ({p.name})" for p in path]
                    status_text = f"Path: {' -> '.join(path_points)}\n" + \
                                f"Total distance: {total_distance:.2f} km"
                    self.path_status_text.config(state='normal')
                    self.path_status_text.delete(1.0, 'end')
                    self.path_status_text.insert('end', status_text)
                    self.path_status_text.config(state='disabled')
                    return
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
            self.path_status_text.config(state='normal')
            self.path_status_text.delete(1.0, 'end')
            self.path_status_text.insert('end', f"No path found from {origin_number} to {dest_number}")
            self.path_status_text.config(state='disabled')
        finally:
            # Reset visualization state
            self.visualization_running = False

    def stop_visualization(self):
        """Stop the current visualization process"""
        if self.visualization_running:
            self.visualization_running = False
            self.status_label.config(text="Status: Visualization stopped.")
            plt.close('all')  # Close all matplotlib figures
            self.visualize_button.configure(state='normal')
            self.stop_visualize_button.configure(state='disabled')
            self.root.update_idletasks()

    def on_window_ready(self, event):
        """Handle window ready event"""
        if event.widget == self.root and self.airspace and not self.visualization_running:
            self.visualize_airspace()

def main():
    root = tk.Tk()
    app = AirspaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
