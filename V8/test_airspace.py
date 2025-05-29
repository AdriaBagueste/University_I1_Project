from airSpace import AirSpace
import matplotlib.pyplot as plt
import os

def test_catalonia_airspace():
    """Test loading and visualizing Catalunya's airspace data."""
    # Create airspace instance
    airspace = AirSpace(name="Catalunya")
    
    # Get paths to data files
    base_dir = os.path.join(os.path.dirname(__file__), "airspace_catalonia")
    nav_file = os.path.join(base_dir, "Cat_nav.txt")
    seg_file = os.path.join(base_dir, "Cat_seg.txt")
    aer_file = os.path.join(base_dir, "Cat_aer.txt")
    
    # Load data
    print("Loading Catalunya airspace data...")
    success = airspace.load_data(nav_file, seg_file, aer_file)
    assert success, "Failed to load airspace data"
    
    # Print statistics
    print("\nAirspace Statistics:")
    print(airspace)
    
    # Test finding specific elements
    print("\nTesting element lookup:")
    
    # Test finding a navigation point
    point = airspace.get_nav_point(1)  # Try to find first point
    assert point is not None, "Failed to find navigation point"
    print(f"Found navigation point: {point}")
    
    # Test finding an airport
    airport = airspace.get_airport("LEBL")  # Barcelona airport
    assert airport is not None, "Failed to find Barcelona airport"
    print(f"Found airport: {airport}")
    print(f"SIDs: {airport.get_sids()}")
    print(f"STARs: {airport.get_stars()}")
    
    # Test finding segments
    segments = airspace.get_segments_from(point.number)
    assert segments, "Failed to find segments from point"
    print(f"\nFound {len(segments)} segments from point {point}:")
    for seg in segments[:3]:  # Show first 3 segments
        print(f"  {seg}")
    if len(segments) > 3:
        print("  ...")
        
    # Create visualization
    print("\nCreating visualization...")
    fig = airspace.plot(
        show_points=True,
        show_segments=True,
        show_airports=True,
        figsize=(15, 10),
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
    
    # Save plot
    output_file = os.path.join(os.path.dirname(__file__), "catalonia_airspace.png")
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot saved to: {output_file}")
    
    print("\nAll tests passed successfully!")

def test_spain_airspace():
    """Test loading and visualizing Spain's airspace data."""
    # Create airspace instance
    airspace = AirSpace(name="España")
    
    # Get paths to data files
    base_dir = os.path.join(os.path.dirname(__file__), "Airspace Spain")
    nav_file = os.path.join(base_dir, "Esp_nav.txt")
    seg_file = os.path.join(base_dir, "Esp_seg.txt")
    aer_file = os.path.join(base_dir, "Esp_aer.txt")
    
    # Check if files exist
    if not all(os.path.exists(f) for f in [nav_file, seg_file, aer_file]):
        print("\nSpain airspace data files not found, skipping test.")
        return
        
    # Load data
    print("\nLoading Spain airspace data...")
    success = airspace.load_data(nav_file, seg_file, aer_file)
    assert success, "Failed to load Spain airspace data"
    
    # Print statistics
    print("\nSpain Airspace Statistics:")
    print(airspace)
    
    # Create visualization
    print("\nCreating visualization...")
    fig = airspace.plot(
        show_points=True,
        show_segments=True,
        show_airports=True,
        figsize=(20, 15),
        point_color='green',
        segment_color='gray',
        airport_color='orange',
        point_size=20,
        segment_width=0.3,
        airport_size=100,
        point_alpha=0.6,
        segment_alpha=0.2,
        airport_alpha=0.8
    )
    
    # Save plot
    output_file = os.path.join(os.path.dirname(__file__), "spain_airspace.png")
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot saved to: {output_file}")

def test_europe_airspace():
    """Test loading and visualizing European airspace data."""
    # Create airspace instance
    airspace = AirSpace(name="Europe")
    
    # Get paths to data files
    base_dir = os.path.join(os.path.dirname(__file__), "ECAC airspace")
    nav_file = os.path.join(base_dir, "Eur_nav.txt")
    seg_file = os.path.join(base_dir, "Eur_seg.txt")
    aer_file = os.path.join(base_dir, "Eur_aer.txt")
    
    # Check if files exist
    if not all(os.path.exists(f) for f in [nav_file, seg_file, aer_file]):
        print("\nEuropean airspace data files not found, skipping test.")
        return
        
    # Load data
    print("\nLoading European airspace data...")
    success = airspace.load_data(nav_file, seg_file, aer_file)
    assert success, "Failed to load European airspace data"
    
    # Print statistics
    print("\nEuropean Airspace Statistics:")
    print(airspace)
    
    # Create visualization
    print("\nCreating visualization...")
    fig = airspace.plot(
        show_points=True,
        show_segments=True,
        show_airports=True,
        figsize=(25, 20),
        point_color='purple',
        segment_color='gray',
        airport_color='orange',
        point_size=15,
        segment_width=0.2,
        airport_size=80,
        point_alpha=0.5,
        segment_alpha=0.1,
        airport_alpha=0.7
    )
    
    # Save plot
    output_file = os.path.join(os.path.dirname(__file__), "europe_airspace.png")
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot saved to: {output_file}")

if __name__ == "__main__":
    print("Testing Catalunya Airspace Implementation")
    print("=" * 40)
    test_catalonia_airspace()
    
    print("\nTesting Spain Airspace Implementation")
    print("=" * 40)
    test_spain_airspace()
    
    print("\nTesting European Airspace Implementation")
    print("=" * 40)
    test_europe_airspace() 