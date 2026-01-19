# P4Python Sync Progress Bar Examples

This directory contains example scripts demonstrating how to use P4Python with progress bars for sync operations.

## Overview

P4Python provides a `Progress` callback class that allows you to track the progress of Perforce operations like sync, submit, and clone. These examples show different ways to implement progress tracking with visual feedback.

## Scripts

### 1. `simple_sync_progress.py` - Quick Start Example

A minimal, easy-to-understand example showing the basics of progress callbacks.

**Features:**
- Simple ASCII progress bar
- Console output with percentage
- Basic progress tracking
- ~100 lines of code

**Usage:**
```bash
# Make sure P4PORT, P4USER, P4CLIENT environment variables are set
export P4PORT=ssl:perforce.example.com:1666
export P4USER=your_username
export P4CLIENT=your_workspace

# Run the script
python simple_sync_progress.py
```

### 2. `p4_sync_progress_demo.py` - Full-Featured Demo

A comprehensive example with multiple progress bar implementations and command-line options.

**Features:**
- Two progress implementations: Basic and tqdm
- Command-line argument parsing
- Configurable server settings
- Detailed progress tracking
- Production-ready error handling

**Usage:**
```bash
# Basic text progress (no dependencies)
python p4_sync_progress_demo.py --basic

# Visual progress bar with tqdm (requires: pip install tqdm)
python p4_sync_progress_demo.py --tqdm

# Custom server configuration
python p4_sync_progress_demo.py --port ssl:perforce:1666 --user john --client john-ws

# Sync specific path
python p4_sync_progress_demo.py --path //depot/main/... --tqdm
```

## P4Python Progress API

### Progress Class

The `P4.Progress` base class provides these callback methods:

```python
class Progress:
    def init(self, type):
        """Called when operation starts. Type: TYPE_SENDFILE=1, TYPE_RECEIVEFILE=2, TYPE_TRANSFER=3, TYPE_COMPUTATION=4"""
        pass
    
    def setDescription(self, description, unit):
        """Called with operation description and unit type (UNIT_PERCENT=1, UNIT_FILES=2, UNIT_KBYTES=3, UNIT_MBYTES=4)"""
        pass
    
    def setTotal(self, total):
        """Called with total amount to process"""
        pass
    
    def update(self, position):
        """Called repeatedly with current progress position"""
        pass
    
    def done(self, fail):
        """Called when operation completes. fail=1 if operation failed"""
        pass
```

### Constants

**Operation Types:**
- `TYPE_SENDFILE = 1` - Sending files to server (submit)
- `TYPE_RECEIVEFILE = 2` - Receiving files from server (sync)
- `TYPE_TRANSFER = 3` - Network transfer
- `TYPE_COMPUTATION = 4` - Server computation

**Unit Types:**
- `UNIT_PERCENT = 1` - Percentage (0-100)
- `UNIT_FILES = 2` - Number of files
- `UNIT_KBYTES = 3` - Kilobytes
- `UNIT_MBYTES = 4` - Megabytes

## Example Implementation

Here's a minimal progress bar implementation:

```python
import P4

class MyProgress(P4.Progress):
    def __init__(self):
        P4.Progress.__init__(self)
        self.total = 0
        
    def setTotal(self, total):
        self.total = total
        
    def update(self, position):
        if self.total > 0:
            percent = (position / self.total) * 100
            print(f"Progress: {percent:.1f}%")

# Use it with P4
p4 = P4.P4()
p4.progress = MyProgress()
p4.connect()
p4.run_sync("//...")
p4.disconnect()
```

## Requirements

### Basic Requirements
- Python 3.6+
- P4Python library installed (`pip install p4python`)
- Access to a Perforce server

### Optional Requirements
- `tqdm` library for enhanced progress bars (`pip install tqdm`)

## Installation

1. Install P4Python:
```bash
pip install p4python
```

2. (Optional) Install tqdm for better progress bars:
```bash
pip install tqdm
```

3. Configure Perforce environment:
```bash
export P4PORT=your_server:1666
export P4USER=your_username
export P4CLIENT=your_workspace
```

## Testing Without a Perforce Server

If you don't have access to a Perforce server, you can:

1. **Set up a local test server:**
   ```bash
   # Download p4d (Perforce server daemon)
   # Start a test server
   p4d -r /path/to/server/root -p 1666
   ```

2. **Use the existing test framework:**
   - See `p4test.py` for examples of setting up test servers
   - The test suite creates temporary Perforce servers for testing

## How It Works

### Progress Callback Flow

1. **Connect to P4 server** and set progress callback
2. **Start sync operation** - `init()` is called
3. **Server sends metadata** - `setDescription()` and `setTotal()` are called
4. **Transfer files** - `update()` is called repeatedly with current position
5. **Complete operation** - `done()` is called

### Example Flow for Sync

```
init(type=2)                    # TYPE_RECEIVEFILE - starting sync
setDescription("Sync", unit=2)  # Operation: Sync, Unit: Files
setTotal(100)                   # 100 files to sync
update(0)                       # Starting
update(10)                      # 10 files done
update(20)                      # 20 files done
...
update(100)                     # All files done
done(fail=0)                    # Success
```

## Advanced Usage

### Combined Progress and Output Handler

You can combine progress tracking with output handling:

```python
class ProgressAndHandler(P4.Progress, P4.OutputHandler):
    def __init__(self):
        P4.Progress.__init__(self)
        P4.OutputHandler.__init__(self)
        
    def outputStat(self, stat):
        # Handle output statistics
        return P4.OutputHandler.HANDLED
        
    def update(self, position):
        # Handle progress updates
        pass

# Use both interfaces
callback = ProgressAndHandler()
p4.run_sync("//...", progress=callback, handler=callback)
```

### Progress for Different Operations

Progress callbacks work with multiple P4 operations:

```python
# Sync with progress
p4.progress = MyProgress()
p4.run_sync("//...")

# Submit with progress
p4.progress = MyProgress()
p4.run_submit()

# Clone with progress (Perforce Helix Core 2017.1+)
p4.progress = MyProgress()
p4.run_clone("//depot/...")
```

## Troubleshooting

### Progress Callbacks Not Called

If progress callbacks aren't being invoked:

1. **Check P4 version:** Progress callbacks require Perforce 2014.1+
2. **Verify operation type:** Not all commands support progress
3. **Check file count:** Progress may not trigger for very small syncs
4. **Server configuration:** Some servers may have progress disabled

### Connection Issues

```python
try:
    p4.connect()
except P4.P4Exception as e:
    print(f"Connection failed: {e}")
    # Check P4PORT, P4USER, P4CLIENT settings
```

## References

- [P4Python Documentation](https://www.perforce.com/manuals/p4python/)
- [Perforce Python API Guide](https://www.perforce.com/manuals/p4python/Content/P4Python/python.programming.html)
- [Progress Class Reference](https://www.perforce.com/manuals/p4python/Content/P4Python/python.progress.html)

## Contributing

These are example scripts for educational purposes. Feel free to adapt them for your needs:

- Add custom progress visualizations
- Integrate with logging frameworks
- Add GUI progress bars
- Create web-based progress tracking

## License

These examples are provided as-is for use with P4Python. See the main LICENSE.txt file for the P4Python library license.
