#!/usr/bin/env python3
"""Command-line interface for FreeD Protocol Validator toolkit."""

import sys
import argparse
from . import (
    main as validator_main,
    test_main,
    replay_main,
    simulate_main,
    analyze_main,
    __version__
)

def main():
    parser = argparse.ArgumentParser(
        description='FreeD Protocol Validator Toolkit'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'freed-validator {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Validator command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Run the UDP packet validator'
    )
    validate_parser.add_argument(
        '--ip',
        default='0.0.0.0',
        help='IP address to listen on (default: 0.0.0.0)'
    )
    validate_parser.add_argument(
        '--port',
        type=int,
        default=6000,
        help='Port number to listen on (default: 6000)'
    )
    
    # Test command
    test_parser = subparsers.add_parser(
        'test',
        help='Run the test suite'
    )
    test_parser.add_argument(
        '--network',
        action='store_true',
        help='Run in network test mode'
    )
    
    # Replay command
    replay_parser = subparsers.add_parser(
        'replay',
        help='Replay recorded packet data'
    )
    replay_parser.add_argument(
        'log_file',
        help='Path to the FreeD packet log CSV file'
    )
    
    # Simulate command
    simulate_parser = subparsers.add_parser(
        'simulate',
        help='Generate test patterns'
    )
    simulate_parser.add_argument(
        'pattern',
        choices=['circle', 'figure8', 'oscillate'],
        help='Movement pattern to simulate'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze recorded data'
    )
    analyze_parser.add_argument(
        'log_file',
        help='Path to the FreeD packet log CSV file'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'validate':
            return validator_main()
        elif args.command == 'test':
            return test_main()
        elif args.command == 'replay':
            return replay_main()
        elif args.command == 'simulate':
            return simulate_main()
        elif args.command == 'analyze':
            return analyze_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
