from navPoint import NavPoint, LoadNavPoints, PlotNavPoint
from navSegment import NavSegment, LoadNavSegments, PlotNavSegment
from navAirport import NavAirport, LoadNavAirports, PlotNavAirport
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
import numpy as np

class AirSpace:
    def __init__(self, name: str = "AirSpace"):
        """Initialize an airspace system.
        
        Args:
            name (str): Name of the airspace (e.g., "Catalunya", "España", "Europe")
        """
        self.name = name
        self.nav_points: List[NavPoint] = []
        self.nav_segments: List[NavSegment] = []
        self.nav_airports: List[NavAirport] = []
        
    def load_data(self, nav_file: str, seg_file: str, aer_file: str) -> bool:
        """Load all airspace data from files.
        
        Args:
            nav_file (str): Path to navigation points file
            seg_file (str): Path to segments file
            aer_file (str): Path to airports file
            
        Returns:
            bool: True if all files were loaded successfully
        """
        # Load navigation points first
        self.nav_points = LoadNavPoints(nav_file)
        if not self.nav_points:
            print("Error: Failed to load navigation points")
            return False
            
        # Load segments (requires nav_points)
        self.nav_segments = LoadNavSegments(seg_file, self.nav_points)
        if not self.nav_segments:
            print("Error: Failed to load navigation segments")
            return False
            
        # Load airports (requires nav_points)
        self.nav_airports = LoadNavAirports(aer_file, self.nav_points)
        if not self.nav_airports:
            print("Error: Failed to load airports")
            return False
            
        return True
        
    def get_nav_point(self, number: int) -> Optional[NavPoint]:
        """Get a navigation point by its number.
        
        Args:
            number (int): Navigation point number
            
        Returns:
            Optional[NavPoint]: The navigation point if found, None otherwise
        """
        for point in self.nav_points:
            if point.number == number:
                return point
        return None
        
    def get_airport(self, icao: str) -> Optional[NavAirport]:
        """Get an airport by its ICAO code.
        
        Args:
            icao (str): ICAO code of the airport
            
        Returns:
            Optional[NavAirport]: The airport if found, None otherwise
        """
        for airport in self.nav_airports:
            if airport.icao == icao:
                return airport
        return None
        
    def get_segments_from(self, origin_number: int) -> List[NavSegment]:
        """Get all segments starting from a navigation point.
        
        Args:
            origin_number (int): Origin point number
            
        Returns:
            List[NavSegment]: List of segments starting from the origin
        """
        return [seg for seg in self.nav_segments if seg.origin_number == origin_number]
        
    def get_segments_to(self, destination_number: int) -> List[NavSegment]:
        """Get all segments ending at a navigation point.
        
        Args:
            destination_number (int): Destination point number
            
        Returns:
            List[NavSegment]: List of segments ending at the destination
        """
        return [seg for seg in self.nav_segments if seg.destination_number == destination_number]
        
    def plot(self, show_points: bool = True, show_segments: bool = True,
             show_airports: bool = True, figsize: Tuple[int, int] = (12, 8),
             point_color: str = 'blue', segment_color: str = 'gray',
             airport_color: str = 'red', point_size: int = 20,
             segment_width: float = 0.5, airport_size: int = 100,
             point_alpha: float = 0.6, segment_alpha: float = 0.3,
             airport_alpha: float = 0.8) -> plt.Figure:
        """Plot the entire airspace system."""
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(1, 1, left=0.1, right=0.9, top=0.9, bottom=0.1)
        ax = fig.add_subplot(gs[0, 0])

        # Calculate the bounds of the airspace, ignoring outliers
        if self.nav_points:
            lats = np.array([point.latitude for point in self.nav_points])
            lons = np.array([point.longitude for point in self.nav_points])
            if self.nav_airports:
                lats = np.concatenate([lats, [airport.latitude for airport in self.nav_airports]])
                lons = np.concatenate([lons, [airport.longitude for airport in self.nav_airports]])
            
            # Compute mean and std
            lat_mean, lat_std = np.mean(lats), np.std(lats)
            lon_mean, lon_std = np.mean(lons), np.std(lons)
            
            # Use only points within 2 std of the mean for axis limits
            lat_mask = (lats > lat_mean - 2*lat_std) & (lats < lat_mean + 2*lat_std)
            lon_mask = (lons > lon_mean - 2*lon_std) & (lons < lon_mean + 2*lon_std)
            lats_in = lats[lat_mask]
            lons_in = lons[lon_mask]
            
            # Add more padding to the longitude axis
            lat_padding = (max(lats_in) - min(lats_in)) * 0.1
            lon_padding = (max(lons_in) - min(lons_in)) * 0.25
            
            # Set a minimum longitude range (e.g., 1 degree)
            min_lon_range = 1.0
            lon_min = min(lons_in) - lon_padding
            lon_max = max(lons_in) + lon_padding
            if lon_max - lon_min < min_lon_range:
                mid = (lon_max + lon_min) / 2
                lon_min = mid - min_lon_range / 2
                lon_max = mid + min_lon_range / 2
            
            ax.set_xlim(lon_min, lon_max)
            ax.set_ylim(min(lats_in) - lat_padding, max(lats_in) + lat_padding)

        # Plot elements
        if show_segments:
            for segment in self.nav_segments:
                PlotNavSegment(segment, self.nav_points, ax, color=segment_color, width=segment_width, alpha=segment_alpha)
        if show_points:
            for point in self.nav_points:
                PlotNavPoint(point, ax, color=point_color, size=point_size, alpha=point_alpha)
        if show_airports:
            for airport in self.nav_airports:
                PlotNavAirport(airport, ax, color=airport_color, size=airport_size, alpha=airport_alpha)

        ax.set_title(f"{self.name} Airspace System", pad=20)
        ax.set_xlabel("Longitude", labelpad=10)
        ax.set_ylabel("Latitude", labelpad=10)

        if show_airports and self.nav_airports:
            ax.legend(["Airport"], loc='upper right', fontsize='small', bbox_to_anchor=(0.98, 0.98))

        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, linestyle='--', alpha=0.3)
        fig.tight_layout(pad=2.0)
        return fig
        
    def save_plot(self, filename: str, **plot_kwargs):
        """Save a plot of the airspace system to a file.
        
        Args:
            filename (str): Path to save the plot
            **plot_kwargs: Additional arguments to pass to plot()
        """
        fig = self.plot(**plot_kwargs)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
    def get_statistics(self) -> dict:
        """Get statistics about the airspace system.
        
        Returns:
            dict: Dictionary containing various statistics
        """
        return {
            'name': self.name,
            'num_nav_points': len(self.nav_points),
            'num_segments': len(self.nav_segments),
            'num_airports': len(self.nav_airports),
            'airports': [f"{airport.icao} ({airport.name})" for airport in self.nav_airports],
            'total_sids': sum(len(airport.sids) for airport in self.nav_airports),
            'total_stars': sum(len(airport.stars) for airport in self.nav_airports)
        }
        
    def __str__(self) -> str:
        """String representation of the airspace system."""
        stats = self.get_statistics()
        return (f"{self.name} Airspace System\n"
                f"Navigation Points: {stats['num_nav_points']}\n"
                f"Segments: {stats['num_segments']}\n"
                f"Airports: {stats['num_airports']}\n"
                f"Total SIDs: {stats['total_sids']}\n"
                f"Total STARs: {stats['total_stars']}")
                
    def __repr__(self) -> str:
        """Detailed string representation of the airspace system."""
        stats = self.get_statistics()
        return (f"AirSpace(name='{self.name}', "
                f"nav_points={stats['num_nav_points']}, "
                f"segments={stats['num_segments']}, "
                f"airports={stats['num_airports']})") 