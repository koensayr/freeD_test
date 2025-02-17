import socket
import time
import math
import argparse
from datetime import datetime
from freed_replayer import create_freed_packet

def generate_circle_pattern(radius: float, height: float, period: float, 
                          current_time: float) -> tuple:
    """Generate a circular movement pattern"""
    angle = (current_time * 2 * math.pi) / period
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = height
    
    # Calculate pan/tilt based on position
    pan = math.degrees(angle)  # Point towards center
    tilt = 0  # Keep level
    roll = 0  # Keep level
    
    return x, y, z, pan, tilt, roll

def generate_figure_eight(size: float, height: float, period: float, 
                         current_time: float) -> tuple:
    """Generate a figure-eight (lemniscate) pattern"""
    t = (current_time * 2 * math.pi) / period
    x = size * math.cos(t) / (1 + math.sin(t)**2)
    y = size * math.sin(t) * math.cos(t) / (1 + math.sin(t)**2)
    z = height
    
    # Calculate pan/tilt
    pan = math.degrees(math.atan2(y, x))
    tilt = 0
    roll = 0
    
    return x, y, z, pan, tilt, roll

def generate_oscillation(amplitude: float, height: float, period: float,
                        current_time: float) -> tuple:
    """Generate an oscillating pattern"""
    t = (current_time * 2 * math.pi) / period
    x = amplitude * math.sin(t)
    y = 0
    z = height + (amplitude * math.cos(t) / 2)
    
    # Calculate pan/tilt
    pan = 30 * math.sin(t)  # Oscillate pan
    tilt = 15 * math.cos(t)  # Oscillate tilt
    roll = 0
    
    return x, y, z, pan, tilt, roll

def simulate_freed_data(pattern: str, target_ip: str, target_port: int, 
                       duration: float = 0.0, packet_rate: int = 30):
    """Simulate FreeD camera movement patterns"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame = 0
    period = 10.0  # seconds for one complete pattern
    start_time = time.time()
    
    # Pattern parameters
    size = 1000.0  # mm
    height = 2000.0  # mm
    
    pattern_funcs = {
        'circle': lambda t: generate_circle_pattern(size, height, period, t),
        'figure8': lambda t: generate_figure_eight(size, height, period, t),
        'oscillate': lambda t: generate_oscillation(size, height, period, t)
    }
    
    if pattern not in pattern_funcs:
        print(f"Invalid pattern. Choose from: {', '.join(pattern_funcs.keys())}")
        return
    
    print(f"Simulating {pattern} pattern at {packet_rate} Hz")
    print(f"Sending to {target_ip}:{target_port}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            if duration > 0 and elapsed >= duration:
                break
            
            # Generate position and rotation based on pattern
            x, y, z, pan, tilt, roll = pattern_funcs[pattern](elapsed)
            
            # Create and send packet
            packet = create_freed_packet(
                frame=frame,
                x=x, y=y, z=z,
                pan=pan, tilt=tilt, roll=roll,
                zoom=1.0, focus=0.5
            )
            
            sock.sendto(packet, (target_ip, target_port))
            
            # Status update every second
            if frame % packet_rate == 0:
                print(f"\rFrame: {frame}, "
                      f"Pos: ({x:.1f}, {y:.1f}, {z:.1f}), "
                      f"Rot: ({pan:.1f}, {tilt:.1f}, {roll:.1f})", end="")
            
            frame += 1
            
            # Maintain packet rate
            next_packet = start_time + (frame / packet_rate)
            sleep_time = next_packet - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        sock.close()
    
    print("\nSimulation complete!")
    print(f"Sent {frame} frames over {elapsed:.1f} seconds")
    print(f"Average rate: {frame/elapsed:.1f} packets/second")

def main():
    parser = argparse.ArgumentParser(description='Simulate FreeD camera movement patterns')
    parser.add_argument('pattern', choices=['circle', 'figure8', 'oscillate'],
                      help='Movement pattern to simulate')
    parser.add_argument('--ip', default='127.0.0.1',
                      help='Target IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=6000,
                      help='Target port number (default: 6000)')
    parser.add_argument('--rate', type=int, default=30,
                      help='Packet rate in Hz (default: 30)')
    parser.add_argument('--duration', type=float, default=0.0,
                      help='Duration in seconds (default: 0 = run indefinitely)')
    
    args = parser.parse_args()
    
    try:
        simulate_freed_data(args.pattern, args.ip, args.port, 
                          args.duration, args.rate)
    except Exception as e:
        print(f"Error in simulation: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    main()
