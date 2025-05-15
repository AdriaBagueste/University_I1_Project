from math import radians, sin, cos, sqrt, atan2

class NavPoint:
    def __init__(self, number: int, name: str, latitude: float, longitude: float):
        """Initialize a navigation point with its number, name, and coordinates.
        
        Args:
            number (int): The node number from nav.txt file
            name (str): The name of the navigation point
            latitude (float): Geographical latitude in degrees
            longitude (float): Geographical longitude in degrees
        """
        self.number = number
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = []  # List of connected NavPoints
        
    def __eq__(self, other):
        """Two NavPoints are equal if they have the same number"""
        if not isinstance(other, NavPoint):
            return False
        return self.number == other.number
        
    def __hash__(self):
        """Make NavPoint hashable for use in sets"""
        return hash(self.number)
        
    def __str__(self):
        """String representation of the NavPoint"""
        return f"{self.name} ({self.number})"
        
    def __repr__(self):
        """Detailed string representation of the NavPoint"""
        return f"NavPoint({self.number}, '{self.name}', {self.latitude}, {self.longitude})"

def Distance(point1: NavPoint, point2: NavPoint) -> float:
    """Calculate the great-circle distance between two points in kilometers.
    
    Uses the Haversine formula to calculate the distance between two points
    on a sphere (Earth) given their latitude and longitude in degrees.
    
    Args:
        point1 (NavPoint): First navigation point
        point2 (NavPoint): Second navigation point
        
    Returns:
        float: Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude to radians
    lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
    lat2, lon2 = radians(point2.latitude), radians(point2.longitude)
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def LoadNavPoints(filename: str) -> list:
    """Load navigation points from a file.
    
    The file should be in the format:
    number name latitude longitude
    
    Args:
        filename (str): Path to the navigation points file
        
    Returns:
        list: List of NavPoint objects
    """
    nav_points = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse the line
                try:
                    number, name, lat, lon = line.split()
                    nav_point = NavPoint(
                        number=int(number),
                        name=name,
                        latitude=float(lat),
                        longitude=float(lon)
                    )
                    nav_points.append(nav_point)
                except ValueError as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        
    return nav_points

def GetNavPointByNumber(nav_points: list, number: int) -> NavPoint:
    """Find a NavPoint by its number.
    
    Args:
        nav_points (list): List of NavPoint objects
        number (int): Number to search for
        
    Returns:
        NavPoint: The found NavPoint or None if not found
    """
    for point in nav_points:
        if point.number == number:
            return point
    return None

def GetNavPointByName(nav_points: list, name: str) -> NavPoint:
    """Find a NavPoint by its name.
    
    Args:
        nav_points (list): List of NavPoint objects
        name (str): Name to search for
        
    Returns:
        NavPoint: The found NavPoint or None if not found
    """
    for point in nav_points:
        if point.name == name:
            return point
    return None

def PlotNavPoint(point: NavPoint, ax=None, color='blue', size=20, alpha=1.0):
    """Plot a navigation point on a matplotlib axis.
    
    Args:
        point (NavPoint): The navigation point to plot
        ax: Matplotlib axis (if None, a new one will be created)
        color (str): Color for the point
        size (int): Size of the point
        alpha (float): Transparency for the point
    """
    import matplotlib.pyplot as plt
    
    if ax is None:
        _, ax = plt.subplots()
        
    ax.scatter(point.longitude, point.latitude, color=color, s=size, alpha=alpha, zorder=2, label=point.name)
    ax.annotate(point.name, (point.longitude, point.latitude), xytext=(5, 5), textcoords='offset points', fontsize=8, alpha=alpha, zorder=3)
    
    return ax 