import socket
import time
import pandas as pd
import struct
from argparse import ArgumentParser
from datetime import datetime
from typing import Tuple, Optional

def create_freed_packet(frame: int, x: float, y: float, z: float,
                       pan: float, tilt: float, roll: float,
                       zoom: float = 0.0, focus: float = 0.0) -> bytes:
    """Create a FreeD protocol packet from given parameters"""
    # Convert values to appropriate scales
    x_int = int(x * 64)
    y_int = int(y * 64)
    z_int = int(z * 64)
    pan_int = int(pan * 32768)
    tilt_int = int(tilt * 32768)
    roll_int = int(roll * 32768)
    zoom_int = int(zoom * 32768)
    focus_int = int(focus * 32768)
    
    # Create packet
    packet = bytearray()
    packet.append(0x44)  # 'D'
    packet.append(0x01)  # Type
    packet.append(0x02)  # Version
    
    # Pack data in big-endian format
    packet.extend(struct.pack('>I', frame))  # Frame number
    packet.extend(struct.pack('>i', x_int))  # X position
    packet.extend(struct.pack('>i', y_int))  # Y position
    packet.extend(struct.pack('>i', z_int))  # Z position
    packet.extend(struct.pack('>i', pan_int))  # Pan
    packet.extend(struct.pack('>i', tilt_int))  # Tilt
    packet.extend(struct.pack('>i', roll_int))  # Roll
    packet.extend(struct.pack('>i', zoom_int))  # Zoom
    packet.extend(struct.pack('>i', focus_int))  # Focus
    
    return bytes(packet)

def replay_log(log_file: str, target_ip: str, target_port: int,
               speed_factor: float = 1.0, loop: bool = False) -> None:
    """Replay FreeD packets from a log file"""
    print(f"Loading log file: {log_file}")
    df = pd.read_csv(log_file)
    
    # Convert timestamp to datetime if not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending packets to {target_ip}:{target_port}")
    
    try:
        while True:
            start_time = time.time()
            first_packet_time = df['timestamp'].iloc[0]
            
            # Filter only valid packets
            valid_packets = df[df['valid'] == True].copy()
            if valid_packets.empty:
                print("No valid packets found in log file!")
                return
            
            packet_count = 0
            print(f"\nReplaying {len(valid_packets)} packets{' (loop enabled)' if loop else ''}")
            print(f"Playback speed: {speed_factor}x")
            print("Press Ctrl+C to stop...")
            
            for _, row in valid_packets.iterrows():
                # Calculate packet timing
                packet_timestamp = row['timestamp']
                relative_time = (packet_timestamp - first_packet_time).total_seconds()
                target_time = start_time + (relative_time / speed_factor)
                
                # Wait until it's time to send the packet
                current_time = time.time()
                if current_time < target_time:
                    time.sleep(target_time - current_time)
                
                # Create and send packet
                packet = create_freed_packet(
                    frame=int(row['frame']),
                    x=float(row['x_pos']),
                    y=float(row['y_pos']),
                    z=float(row['z_pos']),
                    pan=float(row['pan']),
                    tilt=float(row['tilt']),
                    roll=float(row['roll']),
                    zoom=float(row['zoom']),
                    focus=float(row['focus'])
                )
                
                sock.sendto(packet, (target_ip, target_port))
                packet_count += 1
                
                # Update progress
                progress = (packet_count / len(valid_packets)) * 100
                print(f"\rProgress: {progress:.1f}% ({packet_count}/{len(valid_packets)} packets)", end="")
            
            print("\nReplay complete!")
            
            if not loop:
                break
            
            print("\nRestarting replay...")
    
    except KeyboardInterrupt:
        print("\nPlayback stopped by user")
    finally:
        sock.close()

def main():
    parser = ArgumentParser(description='Replay FreeD packets from a log file')
    parser.add_argument('log_file', help='Path to the FreeD packet log CSV file')
    parser.add_argument('--ip', default='127.0.0.1',
                      help='Target IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=6000,
                      help='Target port number (default: 6000)')
    parser.add_argument('--speed', type=float, default=1.0,
                      help='Playback speed factor (default: 1.0)')
    parser.add_argument('--loop', action='store_true',
                      help='Loop playback continuously')
    
    args = parser.parse_args()
    
    try:
        replay_log(args.log_file, args.ip, args.port, args.speed, args.loop)
    except Exception as e:
        print(f"Error replaying log file: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    main()
