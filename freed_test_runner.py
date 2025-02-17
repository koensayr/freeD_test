import unittest
import sys
from colorama import init, Fore, Style
from test_freed_validator import TestFreeDValidator
from freed_validator import FreeDPacket, parse_freed_packet

class FreeDTestRunner:
    def __init__(self):
        init()  # Initialize colorama for colored output
        self.test_results = []
        
    def generate_test_packet(self, **kwargs):
        """Generate a test packet with specified parameters"""
        default_values = {
            'packet_id': 0x44,      # 'D'
            'packet_type': 0x01,    # Position/rotation data
            'version': 0x02,        # Protocol version 2
            'frame_number': 1000,
            'x_pos': 1000.0,
            'y_pos': -500.0,
            'z_pos': 2000.0,
            'pan': 45.0,
            'tilt': -30.0,
            'roll': 0.0,
            'zoom': 1.0,
            'focus': 0.5
        }
        values = {**default_values, **kwargs}
        
        # Convert values to byte format
        data = bytearray()
        data.append(values['packet_id'])
        data.append(values['packet_type'])
        data.append(values['version'])
        data.extend(values['frame_number'].to_bytes(4, 'big'))
        
        # Position data (scaled by 64)
        for pos in ['x_pos', 'y_pos', 'z_pos']:
            scaled = int(values[pos] * 64)
            data.extend(scaled.to_bytes(4, 'big', signed=True))
        
        # Rotation data (scaled by 32768)
        for rot in ['pan', 'tilt', 'roll']:
            scaled = int(values[rot] * 32768)
            data.extend(scaled.to_bytes(4, 'big', signed=True))
            
        # Optional lens data
        data.extend(int(values['zoom'] * 32768).to_bytes(4, 'big', signed=True))
        data.extend(int(values['focus'] * 32768).to_bytes(4, 'big', signed=True))
        
        return bytes(data)
    
    def run_test(self, name, packet_data, expected_valid):
        """Run a single test and record the result"""
        print(f"\n{Fore.CYAN}Running test:{Style.RESET_ALL} {name}")
        print("-" * 60)
        
        packet, is_valid = parse_freed_packet(packet_data)
        
        if is_valid == expected_valid:
            result = f"{Fore.GREEN}PASS{Style.RESET_ALL}"
            details = "Validation result matches expected"
        else:
            result = f"{Fore.RED}FAIL{Style.RESET_ALL}"
            details = f"Expected valid={expected_valid}, got valid={is_valid}"
        
        print(f"Result: {result}")
        print(f"Details: {details}")
        
        if is_valid and packet:
            print("\nPacket Contents:")
            print(f"  Frame: {packet.frame_number}")
            print(f"  Position: X={packet.x_pos:.2f}, Y={packet.y_pos:.2f}, Z={packet.z_pos:.2f}")
            print(f"  Rotation: Pan={packet.pan:.2f}, Tilt={packet.tilt:.2f}, Roll={packet.roll:.2f}")
            print(f"  Lens: Zoom={packet.zoom:.2f}, Focus={packet.focus:.2f}")
        elif packet_data:
            print("\nRaw packet data:")
            print(f"  Hex: {packet_data.hex()}")
            
        self.test_results.append({
            'name': name,
            'passed': is_valid == expected_valid,
            'details': details
        })
    
    def run_all_tests(self):
        """Run a comprehensive suite of tests"""
        print(f"\n{Fore.YELLOW}=== FreeD Protocol Validation Test Suite ==={Style.RESET_ALL}")
        
        # Test 1: Valid standard packet
        self.run_test(
            "Standard Valid Packet",
            self.generate_test_packet(),
            expected_valid=True
        )
        
        # Test 2: Invalid packet ID
        self.run_test(
            "Invalid Packet ID",
            self.generate_test_packet(packet_id=0x45),  # Wrong ID
            expected_valid=False
        )
        
        # Test 3: Invalid packet type
        self.run_test(
            "Invalid Packet Type",
            self.generate_test_packet(packet_type=0x02),  # Wrong type
            expected_valid=False
        )
        
        # Test 4: Extreme values
        self.run_test(
            "Extreme Values",
            self.generate_test_packet(
                x_pos=99999.9,
                y_pos=-99999.9,
                pan=179.9,
                tilt=-89.9
            ),
            expected_valid=True
        )
        
        # Test 5: Zero values
        self.run_test(
            "Zero Values",
            self.generate_test_packet(
                x_pos=0.0,
                y_pos=0.0,
                z_pos=0.0,
                pan=0.0,
                tilt=0.0,
                roll=0.0
            ),
            expected_valid=True
        )
        
        # Print summary
        print(f"\n{Fore.YELLOW}=== Test Summary ==={Style.RESET_ALL}")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t['passed'])
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
        print(f"Failed: {Fore.RED}{total_tests - passed_tests}{Style.RESET_ALL}")
        
        if total_tests == passed_tests:
            print(f"\n{Fore.GREEN}All tests passed!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}Some tests failed. Check details above.{Style.RESET_ALL}")
            failed_tests = [t for t in self.test_results if not t['passed']]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"- {test['name']}: {test['details']}")

def print_packet_info(packet, source_info=""):
    """Print formatted packet information"""
    if packet:
        print(f"\n{Fore.CYAN}Received packet from {source_info}{Style.RESET_ALL}")
        print(f"Frame: {packet.frame_number}")
        print(f"Position: X={packet.x_pos:.2f}, Y={packet.y_pos:.2f}, Z={packet.z_pos:.2f}")
        print(f"Rotation: Pan={packet.pan:.2f}, Tilt={packet.tilt:.2f}, Roll={packet.roll:.2f}")
        print(f"Lens: Zoom={packet.zoom:.2f}, Focus={packet.focus:.2f}")

def network_test_mode(ip, port, duration=60, log_file=None):
    """
    Listen for FreeD packets from a specific IP and port
    
    Args:
        ip (str): IP address to listen on
        port (int): Port number to listen on
        duration (int): How long to listen for packets in seconds
    """
    import socket
    import time
    from datetime import datetime
    
    print(f"\n{Fore.YELLOW}=== FreeD Network Test Mode ==={Style.RESET_ALL}")
    print(f"Listening on {ip}:{port} for {duration} seconds...")
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)  # 1 second timeout for clean exit
    try:
        sock.bind((ip, port))
    except socket.error as e:
        print(f"{Fore.RED}Error binding to {ip}:{port}: {e}{Style.RESET_ALL}")
        return
    
    start_time = time.time()
    last_rate_check = start_time
    packet_count = 0
    valid_count = 0
    invalid_count = 0
    rate_window_packets = 0
    
    # Setup logging if requested
    log_file_handle = None
    if log_file:
        try:
            log_file_handle = open(log_file, 'w')
            log_file_handle.write("timestamp,source_ip,source_port,valid,frame,x_pos,y_pos,z_pos,pan,tilt,roll,zoom,focus\n")
        except IOError as e:
            print(f"{Fore.RED}Error opening log file: {e}{Style.RESET_ALL}")
            log_file = None
    
    def log_packet(timestamp, addr, packet, is_valid):
        """Log packet data to CSV file"""
        if log_file_handle:
            if is_valid and packet:
                log_file_handle.write(f"{timestamp},{addr[0]},{addr[1]},true,{packet.frame_number},"
                                    f"{packet.x_pos:.2f},{packet.y_pos:.2f},{packet.z_pos:.2f},"
                                    f"{packet.pan:.2f},{packet.tilt:.2f},{packet.roll:.2f},"
                                    f"{packet.zoom:.2f},{packet.focus:.2f}\n")
            else:
                log_file_handle.write(f"{timestamp},{addr[0]},{addr[1]},false,,,,,,,,,\n")
            log_file_handle.flush()
    
    try:
        print(f"Press Ctrl+C to stop...")
        while time.time() - start_time < duration:
            current_time = time.time()
            
            # Calculate and display packet rate every second
            if current_time - last_rate_check >= 1.0:
                rate = rate_window_packets / (current_time - last_rate_check)
                print(f"\rPacket Rate: {rate:.1f} packets/sec", end="")
                rate_window_packets = 0
                last_rate_check = current_time
            try:
                data, addr = sock.recvfrom(4096)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                packet_count += 1
                rate_window_packets += 1
                
                packet, is_valid = parse_freed_packet(data)
                if is_valid:
                    valid_count += 1
                    print(f"\n\n{Fore.CYAN}Received packet from {addr[0]}:{addr[1]}{Style.RESET_ALL}")
                    print(f"Time: {timestamp}")
                    print_packet_info(packet)
                else:
                    invalid_count += 1
                    print(f"\n\n{Fore.RED}Invalid packet from {addr[0]}:{addr[1]}{Style.RESET_ALL}")
                    print(f"Time: {timestamp}")
                    print(f"Raw data: {data.hex()}")
                
                log_packet(timestamp, addr, packet, is_valid)
                
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
    
    finally:
        sock.close()
        if log_file_handle:
            log_file_handle.close()
        
    # Print summary
    print(f"\n{Fore.YELLOW}=== Network Test Summary ==={Style.RESET_ALL}")
    print(f"Total packets received: {packet_count}")
    print(f"Valid packets: {Fore.GREEN}{valid_count}{Style.RESET_ALL}")
    print(f"Invalid packets: {Fore.RED}{invalid_count}{Style.RESET_ALL}")
    if packet_count > 0:
        valid_percentage = (valid_count / packet_count) * 100
        print(f"Valid packet rate: {valid_percentage:.1f}%")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='FreeD Protocol Test Runner')
    parser.add_argument('--network', action='store_true',
                      help='Run in network test mode')
    parser.add_argument('--ip', default='0.0.0.0',
                      help='IP address to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=6000,
                      help='Port number to listen on (default: 6000)')
    parser.add_argument('--duration', type=int, default=60,
                      help='Duration to listen for packets in seconds (default: 60)')
    parser.add_argument('--log', type=str,
                      help='Log file path for packet data (CSV format)')
    
    args = parser.parse_args()
    
    if args.network:
        network_test_mode(args.ip, args.port, args.duration)
    else:
        runner = FreeDTestRunner()
        runner.run_all_tests()
