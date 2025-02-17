import socket
import struct
from dataclasses import dataclass
from typing import Tuple

@dataclass
class FreeDPacket:
    """FreeD protocol packet structure (version 2)"""
    packet_id: int      # Always 'D' (0x44)
    packet_type: int    # 0x01 for position/rotation data
    version: int        # Protocol version
    frame_number: int   # Frame counter
    x_pos: float       # Camera X position (mm)
    y_pos: float       # Camera Y position (mm)
    z_pos: float       # Camera Z position (mm)
    pan: float         # Pan angle (degrees)
    tilt: float        # Tilt angle (degrees)
    roll: float        # Roll angle (degrees)
    zoom: float        # Camera zoom
    focus: float       # Camera focus
    
def parse_freed_packet(data: bytes) -> Tuple[FreeDPacket, bool]:
    """
    Parse a FreeD protocol packet and validate its structure.
    Returns a tuple of (packet, is_valid).
    """
    if len(data) < 29:  # Minimum packet size for version 2
        return None, False
    
    try:
        # FreeD packet structure (29 bytes)
        # Byte order is big-endian
        packet_id = data[0]
        if packet_id != 0x44:  # 'D'
            return None, False
            
        packet_type = data[1]
        if packet_type != 0x01:  # Position/rotation data
            return None, False
            
        version = data[2]
        frame_number = struct.unpack('>I', data[3:7])[0]
        
        # Position data (mm, 3 x 32-bit integers)
        x_pos = struct.unpack('>i', data[7:11])[0] / 64.0
        y_pos = struct.unpack('>i', data[11:15])[0] / 64.0
        z_pos = struct.unpack('>i', data[15:19])[0] / 64.0
        
        # Rotation data (degrees, 3 x 32-bit integers)
        pan = struct.unpack('>i', data[19:23])[0] / 32768.0
        tilt = struct.unpack('>i', data[23:27])[0] / 32768.0
        roll = struct.unpack('>i', data[27:31])[0] / 32768.0
        
        # Optional zoom and focus (if packet is longer)
        zoom = 0.0
        focus = 0.0
        if len(data) >= 37:
            zoom = struct.unpack('>i', data[31:35])[0] / 32768.0
            focus = struct.unpack('>i', data[35:39])[0] / 32768.0
        
        packet = FreeDPacket(
            packet_id=packet_id,
            packet_type=packet_type,
            version=version,
            frame_number=frame_number,
            x_pos=x_pos,
            y_pos=y_pos,
            z_pos=z_pos,
            pan=pan,
            tilt=tilt,
            roll=roll,
            zoom=zoom,
            focus=focus
        )
        return packet, True
        
    except (struct.error, IndexError) as e:
        return None, False

def main():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 6000)  # Default FreeD port is often 6000
    print(f'Starting UDP server on {server_address}')
    sock.bind(server_address)
    
    try:
        while True:
            data, address = sock.recvfrom(4096)
            packet, is_valid = parse_freed_packet(data)
            
            if is_valid:
                print(f'\nReceived valid FreeD packet from {address}:')
                print(f'Frame: {packet.frame_number}')
                print(f'Position (mm): X={packet.x_pos:.2f}, Y={packet.y_pos:.2f}, Z={packet.z_pos:.2f}')
                print(f'Rotation (deg): Pan={packet.pan:.2f}, Tilt={packet.tilt:.2f}, Roll={packet.roll:.2f}')
                if packet.zoom or packet.focus:
                    print(f'Lens: Zoom={packet.zoom:.2f}, Focus={packet.focus:.2f}')
            else:
                print(f'\nReceived invalid packet from {address}')
                print(f'Raw data: {data.hex()}')
    
    except KeyboardInterrupt:
        print('\nShutting down...')
    finally:
        sock.close()

if __name__ == '__main__':
    main()
