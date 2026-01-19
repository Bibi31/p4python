#!/usr/bin/env python3
"""
Simple P4 Sync with Progress Bar Example

A minimal example showing how to use P4Python progress callbacks
for sync operations. This is a simplified version for quick testing.

Usage:
    python simple_sync_progress.py
"""

import P4


class SimpleProgressBar(P4.Progress):
    """Simple progress bar that prints to console."""
    
    def __init__(self):
        P4.Progress.__init__(self)
        self.total = 0
        self.current = 0
        
    def init(self, type):
        """Called when operation starts."""
        types = ["Unknown", "Submit", "Sync", "Clone"]
        print(f"\nStarting {types[type] if type < len(types) else 'Unknown'}...")
        
    def setDescription(self, description, unit):
        """Called with operation description."""
        units = ["Unknown", "Percent", "Files", "KBytes", "MBytes"]
        unit_name = units[unit] if unit < len(units) else "Unknown"
        print(f"{description} ({unit_name})")
        
    def setTotal(self, total):
        """Called with total amount to process."""
        self.total = total
        print(f"Total: {total}")
        
    def update(self, position):
        """Called with current progress position."""
        self.current = position
        if self.total > 0:
            percent = (position / self.total) * 100
            # Simple ASCII progress bar
            bar_width = 40
            filled = int(bar_width * position / self.total)
            bar = '=' * filled + '-' * (bar_width - filled)
            print(f'\r[{bar}] {percent:.1f}% ({position}/{self.total})', end='', flush=True)
        
    def done(self, fail):
        """Called when operation completes."""
        print()  # New line after progress bar
        if fail:
            print("Operation FAILED!")
        else:
            print(f"Operation completed: {self.current}/{self.total}")


def main():
    """Main function to demonstrate sync with progress."""
    
    # Create P4 connection
    p4 = P4.P4()
    
    # Configure connection (use environment variables or set here)
    # p4.port = "ssl:perforce.example.com:1666"
    # p4.user = "username"
    # p4.client = "workspace_name"
    
    # Attach progress callback
    p4.progress = SimpleProgressBar()
    
    try:
        # Connect to server
        print("Connecting to Perforce...")
        print(f"Port: {p4.port}")
        print(f"User: {p4.user}")
        print(f"Client: {p4.client}")
        
        p4.connect()
        print("Connected!\n")
        
        # Show server info
        info = p4.run_info()[0]
        print(f"Server: {info.get('serverAddress', 'Unknown')}")
        print(f"Version: {info.get('serverVersion', 'Unknown')}")
        
        # Perform sync with progress tracking
        print("\n" + "="*50)
        print("Syncing files...")
        print("="*50)
        
        # Sync current client workspace
        # Change path as needed: "//depot/...", "//depot/project/...", etc.
        result = p4.run_sync("//...")
        
        print("\n" + "="*50)
        print(f"Sync complete! {len(result)} files processed")
        print("="*50)
        
    except P4.P4Exception as e:
        print(f"\nError: {e}")
        
    finally:
        # Disconnect
        if p4.connected():
            p4.disconnect()
            print("\nDisconnected from Perforce")


if __name__ == "__main__":
    main()
