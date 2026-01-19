# Quick Start Guide - P4 Sync with Progress Bar

## Prerequisites

```bash
# Install P4Python
pip install p4python

# Optional: Install tqdm for better progress bars
pip install tqdm

# Set environment variables
export P4PORT=ssl:perforce.example.com:1666
export P4USER=your_username
export P4CLIENT=your_workspace
```

## Option 1: Simple Example (Quickest)

```bash
python simple_sync_progress.py
```

**Output:**
```
Starting Sync...
Syncing files (Files)
Total: 150
[========================================] 100.0% (150/150)
Operation completed: 150/150
```

## Option 2: Full Demo (Most Features)

```bash
# Basic text progress
python p4_sync_progress_demo.py --basic

# Visual progress bar (requires tqdm)
python p4_sync_progress_demo.py --tqdm

# Custom configuration
python p4_sync_progress_demo.py \
  --port ssl:perforce:1666 \
  --user john \
  --client john-workspace \
  --path //depot/main/... \
  --tqdm
```

## Customization Examples

### 1. Custom Progress Class

```python
import P4

class MyProgress(P4.Progress):
    def update(self, position):
        print(f"Downloaded: {position} files")

p4 = P4.P4()
p4.progress = MyProgress()
p4.connect()
p4.run_sync("//...")
p4.disconnect()
```

### 2. With Logging

```python
import P4
import logging

class LoggingProgress(P4.Progress):
    def __init__(self):
        P4.Progress.__init__(self)
        self.logger = logging.getLogger(__name__)
    
    def update(self, position):
        self.logger.info(f"Progress: {position}/{self.total}")

# Use it
logging.basicConfig(level=logging.INFO)
p4 = P4.P4()
p4.progress = LoggingProgress()
```

### 3. Progress with GUI (tkinter)

```python
import P4
import tkinter as tk
from tkinter import ttk

class GUIProgress(P4.Progress):
    def __init__(self, progressbar):
        P4.Progress.__init__(self)
        self.progressbar = progressbar
    
    def setTotal(self, total):
        self.total = total
        self.progressbar['maximum'] = total
    
    def update(self, position):
        self.progressbar['value'] = position

# Create GUI
root = tk.Tk()
progress = ttk.Progressbar(root, length=300)
progress.pack()

p4 = P4.P4()
p4.progress = GUIProgress(progress)
```

## Common Use Cases

### Sync Entire Depot
```bash
python p4_sync_progress_demo.py --path //... --tqdm
```

### Sync Specific Project
```bash
python p4_sync_progress_demo.py --path //depot/project/... --tqdm
```

### Sync with Force
```python
p4.run_sync('-f', '//...')  # Force sync
```

### Sync to Specific Revision
```python
p4.run_sync('//...@12345')  # Sync to changelist 12345
p4.run_sync('//...@2024/01/01')  # Sync to date
```

## Troubleshooting

### "P4Python module not found"
```bash
pip install p4python
```

### "Connection refused"
```bash
# Check your P4PORT setting
echo $P4PORT
p4 info  # Test connection
```

### "Client unknown"
```bash
# Check your P4CLIENT setting
echo $P4CLIENT
p4 clients  # List available clients
```

### Progress not showing
- Make sure you're syncing enough files (progress may not trigger for 1-2 files)
- Check Perforce server version (requires 2014.1+)
- Try with `-f` flag to force sync: `p4.run_sync('-f', '//...')`

## More Information

See `SYNC_PROGRESS_EXAMPLES.md` for:
- Detailed API documentation
- Advanced usage patterns
- Complete examples
- Integration guides
