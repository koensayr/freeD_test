import unittest
from freed_validator import FreeDPacket, parse_freed_packet

class TestFreeDValidator(unittest.TestCase):
    def test_valid_packet_basic(self):
        # Create a sample FreeD packet with minimum data (29 bytes)
        # Packet format:
        # - ID: 'D' (0x44)
        # - Type: 0x01
        # - Version: 0x02
        # - Frame: 1000
        # - Position: (1000mm, -500mm, 2000mm)
        # - Rotation: (45deg, -30deg, 0deg)
        packet_data = bytes.fromhex(
            '44'      # ID ('D')
            '01'      # Type
            '02'      # Version
            '000003E8'  # Frame 1000
            '00010000'  # X: 1000mm * 64
            'FFFF8000'  # Y: -500mm * 64
            '00020000'  # Z: 2000mm * 64
            '00004000'  # Pan: 45deg * 32768
            'FFFFD555'  # Tilt: -30deg * 32768
            '00000000'  # Roll: 0deg * 32768
        )
        
        packet, is_valid = parse_freed_packet(packet_data)
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(packet)
        self.assertEqual(packet.packet_id, 0x44)
        self.assertEqual(packet.packet_type, 0x01)
        self.assertEqual(packet.version, 0x02)
        self.assertEqual(packet.frame_number, 1000)
        self.assertAlmostEqual(packet.x_pos, 1000.0)
        self.assertAlmostEqual(packet.y_pos, -500.0)
        self.assertAlmostEqual(packet.z_pos, 2000.0)
        self.assertAlmostEqual(packet.pan, 45.0)
        self.assertAlmostEqual(packet.tilt, -30.0)
        self.assertAlmostEqual(packet.roll, 0.0)
        
    def test_valid_packet_with_lens(self):
        # Test packet with zoom and focus data (37 bytes)
        packet_data = bytes.fromhex(
            '44'      # ID ('D')
            '01'      # Type
            '02'      # Version
            '000003E8'  # Frame 1000
            '00010000'  # X: 1000mm * 64
            'FFFF8000'  # Y: -500mm * 64
            '00020000'  # Z: 2000mm * 64
            '00004000'  # Pan: 45deg * 32768
            'FFFFD555'  # Tilt: -30deg * 32768
            '00000000'  # Roll: 0deg * 32768
            '00008000'  # Zoom: 1.0 * 32768
            '00004000'  # Focus: 0.5 * 32768
        )
        
        packet, is_valid = parse_freed_packet(packet_data)
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(packet)
        self.assertAlmostEqual(packet.zoom, 1.0)
        self.assertAlmostEqual(packet.focus, 0.5)
        
    def test_invalid_packet_id(self):
        # Test packet with wrong ID (not 'D')
        packet_data = bytes.fromhex('45' + '00' * 28)  # Wrong ID, rest zeroed
        packet, is_valid = parse_freed_packet(packet_data)
        self.assertFalse(is_valid)
        self.assertIsNone(packet)
        
    def test_invalid_packet_type(self):
        # Test packet with wrong type (not 0x01)
        packet_data = bytes.fromhex('44' + '02' + '00' * 27)  # Wrong type, rest zeroed
        packet, is_valid = parse_freed_packet(packet_data)
        self.assertFalse(is_valid)
        self.assertIsNone(packet)
        
    def test_invalid_packet_length(self):
        # Test packet that's too short
        packet_data = bytes.fromhex('44' + '01' + '02' + '00' * 10)  # Only 13 bytes
        packet, is_valid = parse_freed_packet(packet_data)
        self.assertFalse(is_valid)
        self.assertIsNone(packet)

if __name__ == '__main__':
    unittest.main()
