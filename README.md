# # FreeD Protocol Validator

A Python tool for validating UDP packets following the FreeD protocol, commonly used with Unreal Engine for camera tracking data in virtual production.

## Installation

### Using Docker

```bash
# Pull and run the latest version
docker pull koensayr/freed
docker run -p 6000:6000/udp koensayr/freed

# Or build from source
docker build --target prod -t freed .
docker run -p 6000:6000/udp freed
```

Development with local file mounting:
```bash
# Build development image
docker build --target dev -t freed-dev .

# Run with local directory mounted
docker run -v $(pwd):/app -p 6000:6000/udp freed-dev
```

Specific command examples:
```bash
# Run test suite
docker run freed test --network

# Generate test pattern
docker run freed simulate circle

# Analyze log file (mounting local directory)
docker run -v $(pwd):/data freed analyze /data/freed_packets.csv
```

### Using Docker Compose

Multiple components can be run together using Docker Compose:

```bash
# Start validator with simulator
docker compose up validator simulator

# Development environment with hot reload
docker compose up dev

# Run multiple simulators
docker compose up validator
docker compose up --scale simulator=3 simulator

# Analyze log files
mkdir -p data
cp freed_packets.csv data/
docker compose --profile analysis up analyzer
```

Common Docker Compose patterns:
- `validator + simulator`: Test packet generation and validation
- `dev`: Development environment with live code changes
- `validator + multiple simulators`: Load testing
- `analyzer`: Batch processing of log files

### Using Homebrew (macOS)

```bash
# Add the tap
brew tap koensayr/freed_test

# Install the package
brew install freed-validator
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/koensayr/freed_test.git
   cd freed_test
   ```

2. Install using pip:
   ```bash
   pip install .
   ```

### Command Line Usage

After installation, use the `freed` command with various subcommands:

```bash
# Run the UDP packet validator
freed validate --ip 0.0.0.0 --port 6000

# Run the test suite
freed test [--network]

# Replay recorded packet data
freed replay freed_packets.csv

# Generate test patterns
freed simulate circle
freed simulate figure8
freed simulate oscillate

# Analyze recorded data
freed analyze freed_packets.csv
```

For help on any command:
```bash
freed --help
freed <command> --help
```

## Overview

The FreeD protocol is used to transmit real-time camera tracking data, including:
- Position (X, Y, Z) in millimeters
- Rotation (Pan, Tilt, Roll) in degrees
- Optional lens data (Zoom, Focus)

## Protocol Specification

The tool validates FreeD protocol version 2 packets with the following structure:

- Minimum packet size: 29 bytes
- Extended packet size (with lens data): 37 bytes

Packet structure:
```
Byte  0    : Packet ID ('D' = 0x44)
Byte  1    : Packet Type (0x01 for position/rotation data)
Byte  2    : Protocol Version
Bytes 3-6  : Frame Number (32-bit integer)
Bytes 7-18 : Position Data (X, Y, Z as 32-bit integers, scaled by 1/64)
Bytes 19-30: Rotation Data (Pan, Tilt, Roll as 32-bit integers, scaled by 1/32768)
Bytes 31-38: Lens Data (Optional - Zoom, Focus as 32-bit integers, scaled by 1/32768)
```

## Usage

1. Start the validator:
   ```bash
   python freed_validator.py
   ```
   This will start a UDP server listening on port 6000 (default FreeD port).

2. The validator will:
   - Listen for incoming UDP packets
   - Validate each packet against the FreeD protocol
   - Display parsed data for valid packets
   - Show diagnostic information for invalid packets

## Testing

The project includes three testing approaches:

### 1. Network Test Mode
Test with live FreeD protocol data:
```bash
# Listen on all interfaces, port 6000 (default)
python freed_test_runner.py --network

# Listen on specific IP and port
python freed_test_runner.py --network --ip 192.168.1.100 --port 6000

# Set custom duration (in seconds)
python freed_test_runner.py --network --duration 300

# Log packet data to CSV file
python freed_test_runner.py --network --log freed_packets.csv
```

This mode provides:
- Real-time packet rate monitoring (packets/second)
- CSV logging of all packet data with timestamps
- Real-time validation of incoming FreeD packets
- Detailed packet contents with timestamps
- Source IP and port information
- Statistics on valid/invalid packet rates
- Color-coded output for easy reading
- CSV logging for detailed analysis

### Data Analysis
The project includes a data analysis tool for logged FreeD packets:
```bash
# Basic analysis with default output
python analyze_freed_log.py freed_packets.csv

# Specify custom output prefix for generated files
python analyze_freed_log.py freed_packets.csv --output my_analysis
```

The analysis tool provides:
- Statistical analysis of packet data
  - Packet rates and timing
  - Position and rotation ranges
  - Valid/invalid packet ratios
- Visualization plots
  - Packet rate over time
  - 3D camera position trail
  - Rotation angles over time
- Output saved as PNG files for easy sharing

### Packet Replay
The project includes a replay tool for testing and simulation:
```bash
# Basic replay to localhost
python freed_replayer.py freed_packets.csv

# Replay to specific target
python freed_replayer.py freed_packets.csv --ip 192.168.1.100 --port 6000

# Adjust playback speed
python freed_replayer.py freed_packets.csv --speed 2.0  # 2x speed
python freed_replayer.py freed_packets.csv --speed 0.5  # Half speed

# Loop playback continuously
python freed_replayer.py freed_packets.csv --loop
```

The replay tool features:
- Accurate timing reproduction
- Speed adjustment (faster/slower playback)
- Continuous loop mode
- Progress monitoring
- Target IP/port configuration

### Pattern Simulation
The project includes a pattern simulator for generating test data:
```bash
# Generate circular movement pattern
python freed_simulator.py circle

# Generate figure-eight pattern with custom rate
python freed_simulator.py figure8 --rate 60

# Generate oscillating pattern to specific target
python freed_simulator.py oscillate --ip 192.168.1.100 --port 6000

# Run for specific duration
python freed_simulator.py circle --duration 30
```

Available patterns:
- `circle`: Circular movement at constant height
- `figure8`: Figure-eight (lemniscate) pattern
- `oscillate`: Oscillating movement with pan/tilt changes

Simulation features:
- Precise packet timing
- Configurable packet rate (Hz)
- Multiple movement patterns
- Adjustable duration
- Real-time position/rotation display

Example network test output:
```
=== FreeD Network Test Mode ===
Listening on 192.168.1.100:6000 for 60 seconds...

Received packet from 192.168.1.50:50000
Frame: 1234
Position: X=1000.50, Y=-500.25, Z=2000.75
Rotation: Pan=45.00, Tilt=-30.00, Roll=0.00
Lens: Zoom=1.00, Focus=0.50
Time: 14:25:30.123

=== Network Test Summary ===
Total packets received: 120
Valid packets: 118
Invalid packets: 2
Valid packet rate: 98.3%
```
### 2. Comprehensive Test Runner
Run the visual test suite with colored output:
```bash
python freed_test_runner.py
```

This provides:
- Clear pass/fail status for each test
- Detailed packet contents for valid packets
- Hex dumps for invalid packets
- Summary of all test results
- Color-coded output for easy reading

Test cases include:
- Standard valid packets
- Invalid packet IDs
- Invalid packet types
- Extreme value validation
- Zero value validation

### 3. Unit Tests
For development and integration purposes:
```bash
python -m unittest test_freed_validator.py -v
```

The unit test suite verifies:
- Basic position/rotation packets
- Extended packets with lens data
- Invalid packet handling
  - Wrong packet ID
  - Wrong packet type
  - Invalid packet length

## Example Output

For valid packets:
```
Received valid FreeD packet from ('192.168.1.100', 50000):
Frame: 1000
Position (mm): X=1000.00, Y=-500.00, Z=2000.00
Rotation (deg): Pan=45.00, Tilt=-30.00, Roll=0.00
Lens: Zoom=1.00, Focus=0.50
```

For invalid packets:
```
Received invalid packet from ('192.168.1.100', 50000)
Raw data: 450000...
```

Created with [**Solver**](https://solverai.com)