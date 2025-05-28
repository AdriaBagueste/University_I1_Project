from navPoint import NavPoint, Distance, GetNavPointByNumber

class NavSegment:
    def __init__(self, origin_number: int, destination_number: int, distance: float):
        """Initialize a navigation segment with its origin, destination, and distance.
        
        Args:
            origin_number (int): The origin node number
            destination_number (int): The destination node number
            distance (float): Distance in kilometers
        """
        self.origin_number = origin_number
        self.destination_number = destination_number
        self.distance = distance
        self.origin = None  # Will be set to NavPoint object
        self.destination = None  # Will be set to NavPoint object
        
    def __eq__(self, other):
        """Two NavSegments are equal if they connect the same points"""
        if not isinstance(other, NavSegment):
            return False
        return (self.origin_number == other.origin_number and 
                self.destination_number == other.destination_number)
                
    def __hash__(self):
        """Make NavSegment hashable for use in sets"""
        return hash((self.origin_number, self.destination_number))
        
    def __str__(self):
        """String representation of the NavSegment"""
        return f"{self.origin_number} -> {self.destination_number} ({self.distance:.2f} km)"
        
    def __repr__(self):
        """Detailed string representation of the NavSegment"""
        return f"NavSegment({self.origin_number}, {self.destination_number}, {self.distance})"

def LoadNavSegments(filename: str, nav_points: list) -> list:
    """Load navigation segments from a file and link them to NavPoints.
    
    The file should be in the format:
    origin_number destination_number distance
    
    Args:
        filename (str): Path to the segments file
        nav_points (list): List of NavPoint objects to link with segments
        
    Returns:
        list: List of NavSegment objects
    """
    from navPoint import GetNavPointByNumber
    
    nav_segments = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse the line
                try:
                    orig_num, dest_num, dist = line.split()
                    segment = NavSegment(
                        origin_number=int(orig_num),
                        destination_number=int(dest_num),
                        distance=float(dist)
                    )
                    
                    # Link to NavPoints
                    segment.origin = GetNavPointByNumber(nav_points, segment.origin_number)
                    segment.destination = GetNavPointByNumber(nav_points, segment.destination_number)
                    
                    if segment.origin and segment.destination:
                        # Add to neighbors list
                        segment.origin.neighbors.append(segment.destination)
                        nav_segments.append(segment)
                    else:
                        print(f"Warning: Could not find NavPoints for segment {segment}")
                        
                except ValueError as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        
    return nav_segments

def GetSegmentsByOrigin(nav_segments: list, origin_number: int) -> list:
    """Find all segments starting from a given origin point.
    
    Args:
        nav_segments (list): List of NavSegment objects
        origin_number (int): Origin point number to search for
        
    Returns:
        list: List of NavSegment objects starting from the origin
    """
    return [seg for seg in nav_segments if seg.origin_number == origin_number]

def GetSegmentsByDestination(nav_segments: list, destination_number: int) -> list:
    """Find all segments ending at a given destination point.
    
    Args:
        nav_segments (list): List of NavSegment objects
        destination_number (int): Destination point number to search for
        
    Returns:
        list: List of NavSegment objects ending at the destination
    """
    return [seg for seg in nav_segments if seg.destination_number == destination_number]

def PlotNavSegment(segment: NavSegment, nav_points: list, ax=None, color='gray', width=1.0, alpha=1.0):
    """Plot a navigation segment on a matplotlib axis.
    
    Args:
        segment (NavSegment): The segment to plot
        nav_points (list): List of NavPoint objects
        ax: Matplotlib axis (if None, a new one will be created)
        color (str): Color for the segment
        width (float): Width of the line
        alpha (float): Transparency of the line
    """
    import matplotlib.pyplot as plt
    
    if ax is None:
        _, ax = plt.subplots()
        
    origin = GetNavPointByNumber(nav_points, segment.origin_number)
    destination = GetNavPointByNumber(nav_points, segment.destination_number)
    if origin and destination:
        ax.plot([origin.longitude, destination.longitude], [origin.latitude, destination.latitude], color=color, linewidth=width, alpha=alpha, zorder=1)
        
    return ax 