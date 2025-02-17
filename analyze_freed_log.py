import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser
from datetime import datetime

def load_and_process_log(log_file):
    """Load and process the FreeD packet log file"""
    # Read CSV file
    df = pd.read_csv(log_file)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate time differences between packets
    df['time_diff'] = df['timestamp'].diff().dt.total_seconds()
    
    # Calculate instantaneous packet rate (rolling window of 10 packets)
    df['packet_rate'] = 1 / df['time_diff'].rolling(window=10).mean()
    
    return df

def plot_packet_analysis(df, output_prefix):
    """Generate analysis plots from the packet data"""
    # Set style
    plt.style.use('seaborn')
    
    # Plot 1: Packet Rate over Time
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['packet_rate'], label='Packet Rate')
    plt.title('FreeD Packet Rate Over Time')
    plt.xlabel('Time')
    plt.ylabel('Packets per Second')
    plt.grid(True)
    plt.savefig(f'{output_prefix}_packet_rate.png')
    plt.close()
    
    # Plot 2: Camera Position Trail (3D)
    valid_data = df[df['valid'] == True]
    if not valid_data.empty:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(valid_data['x_pos'], 
                           valid_data['y_pos'], 
                           valid_data['z_pos'],
                           c=valid_data.index,
                           cmap='viridis',
                           alpha=0.6)
        plt.colorbar(scatter, label='Time')
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.set_zlabel('Z Position (mm)')
        plt.title('Camera Position Trail')
        plt.savefig(f'{output_prefix}_position_trail.png')
        plt.close()
    
    # Plot 3: Camera Rotation Over Time
    if not valid_data.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(valid_data['timestamp'], valid_data['pan'], label='Pan')
        plt.plot(valid_data['timestamp'], valid_data['tilt'], label='Tilt')
        plt.plot(valid_data['timestamp'], valid_data['roll'], label='Roll')
        plt.title('Camera Rotation Over Time')
        plt.xlabel('Time')
        plt.ylabel('Degrees')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{output_prefix}_rotation.png')
        plt.close()

def print_statistics(df):
    """Print statistical analysis of the packet data"""
    print("\n=== FreeD Packet Analysis ===")
    
    # Basic stats
    total_packets = len(df)
    valid_packets = df['valid'].sum()
    duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds()
    
    print(f"\nBasic Statistics:")
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Total Packets: {total_packets}")
    print(f"Valid Packets: {valid_packets}")
    print(f"Invalid Packets: {total_packets - valid_packets}")
    print(f"Average Packet Rate: {total_packets/duration:.2f} packets/second")
    
    # Position and rotation stats for valid packets
    valid_data = df[df['valid'] == True]
    if not valid_data.empty:
        print(f"\nPosition Range (mm):")
        print(f"X: {valid_data['x_pos'].min():.2f} to {valid_data['x_pos'].max():.2f}")
        print(f"Y: {valid_data['y_pos'].min():.2f} to {valid_data['y_pos'].max():.2f}")
        print(f"Z: {valid_data['z_pos'].min():.2f} to {valid_data['z_pos'].max():.2f}")
        
        print(f"\nRotation Range (degrees):")
        print(f"Pan: {valid_data['pan'].min():.2f} to {valid_data['pan'].max():.2f}")
        print(f"Tilt: {valid_data['tilt'].min():.2f} to {valid_data['tilt'].max():.2f}")
        print(f"Roll: {valid_data['roll'].min():.2f} to {valid_data['roll'].max():.2f}")

def main():
    parser = ArgumentParser(description='Analyze FreeD packet log data')
    parser.add_argument('log_file', help='Path to the FreeD packet log CSV file')
    parser.add_argument('--output', default='freed_analysis',
                      help='Prefix for output files (default: freed_analysis)')
    
    args = parser.parse_args()
    
    try:
        # Load and process data
        print(f"Loading data from {args.log_file}...")
        df = load_and_process_log(args.log_file)
        
        # Generate analysis
        print("Generating statistical analysis...")
        print_statistics(df)
        
        print("\nGenerating plots...")
        plot_packet_analysis(df, args.output)
        
        print(f"\nAnalysis complete. Output files saved with prefix: {args.output}")
        
    except Exception as e:
        print(f"Error analyzing log file: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    main()
