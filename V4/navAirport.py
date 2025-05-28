from navPoint import NavPoint, GetNavPointByNumber, GetNavPointByName
from navSegment import NavSegment, GetSegmentsByOrigin, GetSegmentsByDestination

class NavAirport:
    def __init__(self, icao: str, name: str, latitude: float, longitude: float, 
                 elevation: float, nav_point: NavPoint = None):
        """Initialize a navigation airport with its basic information.
        
        Args:
            icao (str): ICAO code of the airport
            name (str): Name of the airport
            latitude (float): Latitude in degrees
            longitude (float): Longitude in degrees
            elevation (float): Elevation in feet
            nav_point (NavPoint): Associated navigation point (optional)
        """
        self.icao = icao
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.nav_point = nav_point
        self.sids = []  # List of SID names
        self.stars = []  # List of STAR names
        
    def __eq__(self, other):
        """Two NavAirports are equal if they have the same ICAO code"""
        if not isinstance(other, NavAirport):
            return False
        return self.icao == other.icao
        
    def __hash__(self):
        """Make NavAirport hashable for use in sets"""
        return hash(self.icao)
        
    def __str__(self):
        """String representation of the NavAirport"""
        return f"{self.icao} - {self.name}"
        
    def __repr__(self):
        """Detailed string representation of the NavAirport"""
        return (f"NavAirport({self.icao}, {self.name}, {self.latitude}, "
                f"{self.longitude}, {self.elevation})")
                
    def add_sid(self, sid_name: str):
        """Add a SID to the airport's list if not already present.
        
        Args:
            sid_name (str): Name of the SID to add
        """
        if sid_name not in self.sids:
            self.sids.append(sid_name)
            
    def add_star(self, star_name: str):
        """Add a STAR to the airport's list if not already present.
        
        Args:
            star_name (str): Name of the STAR to add
        """
        if star_name not in self.stars:
            self.stars.append(star_name)
            
    def get_sids(self) -> list:
        """Get the list of SIDs for this airport.
        
        Returns:
            list: List of SID names
        """
        return sorted(self.sids)
        
    def get_stars(self) -> list:
        """Get the list of STARs for this airport.
        
        Returns:
            list: List of STAR names
        """
        return sorted(self.stars)

def LoadNavAirports(filename: str, nav_points: list) -> list:
    """Load airports from a file and link them to NavPoints.
    
    The file should be in the format:
    ICAO
    SID1
    SID2
    ...
    STAR1
    STAR2
    ...
    ICAO
    ...
    
    Args:
        filename (str): Path to the airports file
        nav_points (list): List of NavPoint objects to link with airports
        
    Returns:
        list: List of NavAirport objects
    """
    nav_airports = []
    current_airport = None
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # If line is an ICAO code (4 letters)
                if len(line) == 4 and line.isalpha():
                    # If we have a previous airport, add it to the list
                    if current_airport is not None:
                        nav_airports.append(current_airport)
                    
                    # Create new airport
                    # For now, we'll use dummy coordinates and elevation
                    # These should be updated with actual data
                    current_airport = NavAirport(
                        icao=line,
                        name=f"Airport {line}",  # Placeholder name
                        latitude=0.0,  # Placeholder
                        longitude=0.0,  # Placeholder
                        elevation=0.0   # Placeholder
                    )
                    
                # If line ends with .D, it's a SID
                elif line.endswith('.D'):
                    if current_airport is not None:
                        current_airport.add_sid(line)
                        
                # If line ends with .A, it's a STAR
                elif line.endswith('.A'):
                    if current_airport is not None:
                        current_airport.add_star(line)
                        
        # Add the last airport if there is one
        if current_airport is not None:
            nav_airports.append(current_airport)
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        
    # TODO: Update airport coordinates and elevations with actual data
    # For now, we'll try to find matching NavPoints by name
    for airport in nav_airports:
        # Try to find a NavPoint with the airport's ICAO code
        nav_point = GetNavPointByName(nav_points, airport.icao)
        if nav_point is not None:
            airport.nav_point = nav_point
            airport.latitude = nav_point.latitude
            airport.longitude = nav_point.longitude
            # Elevation remains 0.0 as we don't have that data yet
            
    return nav_airports

def GetAirportByICAO(nav_airports: list, icao: str) -> NavAirport:
    """Find an airport by its ICAO code.
    
    Args:
        nav_airports (list): List of NavAirport objects
        icao (str): ICAO code to search for
        
    Returns:
        NavAirport: The airport with the given ICAO code, or None if not found
    """
    for airport in nav_airports:
        if airport.icao == icao:
            return airport
    return None

def PlotNavAirport(airport: NavAirport, ax=None, color='red', size=100, alpha=0.8):
    """Plot a navigation airport on a matplotlib axis.
    
    Args:
        airport (NavAirport): The airport to plot
        ax: Matplotlib axis (if None, a new one will be created)
        color (str): Color for the airport marker
        size (float): Size of the marker
        alpha (float): Transparency of the marker
    """
    import matplotlib.pyplot as plt
    
    if ax is None:
        _, ax = plt.subplots()
        
    # Plot airport location
    ax.scatter(airport.longitude, airport.latitude,
              color=color, s=size, alpha=alpha, zorder=2,
              label=f"{airport.icao} - {airport.name}")
              
    # Add airport label
    ax.annotate(airport.icao,
                (airport.longitude, airport.latitude),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8, alpha=alpha, zorder=3)
                
    return ax 