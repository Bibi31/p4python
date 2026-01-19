#!/usr/bin/env python3
"""
P4Python Sync Progress Bar Demo Script

This script demonstrates how to perform a Perforce sync operation with a progress bar.
It shows two implementations:
1. BasicProgress - Simple text-based progress output
2. ProgressBarSync - Visual progress bar using tqdm library (optional)

Prerequisites:
- P4Python library installed
- Access to a Perforce server
- Valid P4PORT, P4USER, P4CLIENT environment variables or configured below

Usage:
    python p4_sync_progress_demo.py [options]

Options:
    --basic         Use basic text progress (default)
    --tqdm          Use tqdm progress bar (requires: pip install tqdm)
    --port PORT     Perforce server address (e.g., ssl:perforce.example.com:1666)
    --user USER     Perforce username
    --client CLIENT Perforce client/workspace name
    --path PATH     File path to sync (default: //...)

Examples:
    # Basic progress with default settings
    python p4_sync_progress_demo.py --basic
    
    # With tqdm progress bar
    python p4_sync_progress_demo.py --tqdm
    
    # Custom server settings
    python p4_sync_progress_demo.py --port ssl:perforce:1666 --user john --client john-ws
    
    # Sync specific path
    python p4_sync_progress_demo.py --path //depot/main/...
"""

from __future__ import print_function
import sys
import os
import argparse

# Import P4 module
try:
    import P4
except ImportError:
    print("ERROR: P4Python module not found. Please install it first.")
    print("Installation: pip install p4python")
    sys.exit(1)


class BasicProgress(P4.Progress):
    """
    Basic text-based progress tracker for P4 sync operations.
    
    This class extends P4.Progress and provides simple console output
    showing the progress of sync operations.
    """
    
    # Progress type constants
    TYPES = ["Unknown", "Submit", "Sync", "Clone"]
    UNITS = ["Unknown", "Percent", "Files", "KBytes", "MBytes"]
    
    def __init__(self):
        P4.Progress.__init__(self)
        self.total = 0
        self.position = 0
        self.description = ""
        self.unit = 0
        self.type_name = "Unknown"
        
    def init(self, type):
        """Initialize progress tracking with the operation type."""
        self.type = type
        self.type_name = self.TYPES[type] if type < len(self.TYPES) else "Unknown"
        print(f"\n[Progress] Starting {self.type_name} operation...")
        
    def setDescription(self, description, unit):
        """Set description and units for the progress operation."""
        self.description = description
        self.unit = unit
        self.unit_name = self.UNITS[unit] if unit < len(self.UNITS) else "Unknown"
        print(f"[Progress] {description} ({self.unit_name})")
        
    def setTotal(self, total):
        """Set the total size/count for the operation."""
        self.total = total
        print(f"[Progress] Total: {total} {self.unit_name}")
        
    def update(self, position):
        """Update current progress position."""
        self.position = position
        if self.total > 0:
            percentage = (position / self.total) * 100
            # Print progress every 10% or on complete
            if position % max(1, self.total // 10) == 0 or position == self.total:
                print(f"[Progress] {percentage:.1f}% - {position}/{self.total} {self.unit_name}")
        else:
            # No total known, just show position
            print(f"[Progress] {position} {self.unit_name}")
            
    def done(self, fail):
        """Called when the operation completes."""
        if fail:
            print(f"[Progress] {self.type_name} FAILED!")
        else:
            print(f"[Progress] {self.type_name} completed successfully! ({self.position}/{self.total})")
        print()


class ProgressBarSync(P4.Progress):
    """
    Visual progress bar for P4 sync operations using tqdm library.
    
    This provides a more sophisticated progress bar with ETA and speed information.
    Requires: pip install tqdm
    """
    
    TYPES = ["Unknown", "Submit", "Sync", "Clone"]
    UNITS = ["Unknown", "Percent", "Files", "KBytes", "MBytes"]
    
    def __init__(self):
        P4.Progress.__init__(self)
        self.pbar = None
        self.type_name = "Unknown"
        
        # Check if tqdm is available
        try:
            import tqdm
            self.tqdm = tqdm
        except ImportError:
            print("WARNING: tqdm not installed. Using basic progress instead.")
            print("Install with: pip install tqdm")
            self.tqdm = None
    
    def init(self, type):
        """Initialize progress tracking with the operation type."""
        self.type = type
        self.type_name = self.TYPES[type] if type < len(self.TYPES) else "Unknown"
        if not self.tqdm:
            print(f"\n[Progress] Starting {self.type_name} operation...")
    
    def setDescription(self, description, unit):
        """Set description and units, initialize progress bar."""
        self.description = description
        self.unit = unit
        self.unit_name = self.UNITS[unit] if unit < len(self.UNITS) else "Unknown"
        
    def setTotal(self, total):
        """Set total and create the progress bar."""
        self.total = total
        if self.tqdm and total > 0:
            # Create tqdm progress bar
            self.pbar = self.tqdm.tqdm(
                total=total,
                desc=f"{self.type_name}: {self.description}",
                unit=self.unit_name.lower(),
                unit_scale=False,
                ncols=100,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
        elif not self.tqdm:
            print(f"[Progress] {self.description}: 0/{total} {self.unit_name}")
    
    def update(self, position):
        """Update progress bar position."""
        if self.pbar:
            # Update tqdm progress bar
            delta = position - self.pbar.n
            if delta > 0:
                self.pbar.update(delta)
        elif not self.tqdm and self.total > 0:
            # Fallback to basic output
            percentage = (position / self.total) * 100
            if position % max(1, self.total // 10) == 0 or position == self.total:
                print(f"[Progress] {percentage:.1f}% - {position}/{self.total} {self.unit_name}")
    
    def done(self, fail):
        """Close progress bar when operation completes."""
        if self.pbar:
            self.pbar.close()
        if fail:
            print(f"[Progress] {self.type_name} FAILED!")
        elif not self.tqdm:
            print(f"[Progress] {self.type_name} completed successfully!")


class SyncProgressDemo:
    """
    Main demo class that sets up P4 connection and performs sync with progress.
    """
    
    def __init__(self, port=None, user=None, client=None, progress_type="basic"):
        """
        Initialize P4 connection.
        
        Args:
            port: P4PORT server address
            user: P4USER username
            client: P4CLIENT workspace name
            progress_type: "basic" or "tqdm"
        """
        self.p4 = P4.P4()
        
        # Configure connection from parameters or environment
        if port:
            self.p4.port = port
        if user:
            self.p4.user = user
        if client:
            self.p4.client = client
            
        # Set up progress callback
        if progress_type == "tqdm":
            self.progress = ProgressBarSync()
        else:
            self.progress = BasicProgress()
            
        self.p4.progress = self.progress
        
    def connect(self):
        """Connect to P4 server and verify connection."""
        try:
            print(f"Connecting to Perforce server...")
            print(f"  Port: {self.p4.port}")
            print(f"  User: {self.p4.user}")
            print(f"  Client: {self.p4.client}")
            
            self.p4.connect()
            
            # Verify connection
            info = self.p4.run_info()
            if info:
                print(f"  Server version: {info[0].get('serverVersion', 'Unknown')}")
                print("Connected successfully!\n")
            return True
            
        except P4.P4Exception as e:
            print(f"ERROR: Failed to connect to Perforce server")
            print(f"  {e}")
            return False
    
    def sync(self, path="//..."):
        """
        Perform sync operation with progress tracking.
        
        Args:
            path: File path pattern to sync (default: //...)
        """
        try:
            print(f"Syncing files: {path}")
            print("-" * 60)
            
            # Run sync with progress callback
            result = self.p4.run_sync(path)
            
            print("-" * 60)
            print(f"Sync completed. Files processed: {len(result)}")
            
            # Show summary
            if result:
                print("\nSync Summary:")
                for item in result[:5]:  # Show first 5 items
                    if isinstance(item, dict):
                        depot_file = item.get('depotFile', 'Unknown')
                        action = item.get('action', 'Unknown')
                        rev = item.get('rev', '?')
                        print(f"  {depot_file}#{rev} - {action}")
                if len(result) > 5:
                    print(f"  ... and {len(result) - 5} more files")
            
            return True
            
        except P4.P4Exception as e:
            print(f"ERROR: Sync failed")
            print(f"  {e}")
            return False
    
    def disconnect(self):
        """Disconnect from P4 server."""
        if self.p4.connected():
            self.p4.disconnect()
            print("\nDisconnected from Perforce server.")


def main():
    """Main entry point for the demo script."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="P4Python Sync Progress Bar Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --basic
  %(prog)s --tqdm
  %(prog)s --port ssl:perforce:1666 --user john --client john-ws
  %(prog)s --path //depot/main/... --tqdm
        """
    )
    
    parser.add_argument(
        '--basic',
        action='store_true',
        help='Use basic text progress (default)'
    )
    parser.add_argument(
        '--tqdm',
        action='store_true',
        help='Use tqdm progress bar (requires: pip install tqdm)'
    )
    parser.add_argument(
        '--port',
        help='P4PORT - Perforce server address (e.g., ssl:perforce:1666)'
    )
    parser.add_argument(
        '--user',
        help='P4USER - Perforce username'
    )
    parser.add_argument(
        '--client',
        help='P4CLIENT - Perforce workspace/client name'
    )
    parser.add_argument(
        '--path',
        default='//...',
        help='File path to sync (default: //...)'
    )
    
    args = parser.parse_args()
    
    # Determine progress type
    progress_type = "tqdm" if args.tqdm else "basic"
    
    # Print header
    print("=" * 60)
    print("P4Python Sync Progress Bar Demo")
    print("=" * 60)
    print()
    
    # Create demo instance
    demo = SyncProgressDemo(
        port=args.port,
        user=args.user,
        client=args.client,
        progress_type=progress_type
    )
    
    # Run the demo
    try:
        if demo.connect():
            demo.sync(args.path)
    finally:
        demo.disconnect()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()
