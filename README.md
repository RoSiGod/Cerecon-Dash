# Cerecon-Dash

## Process Tracker

`process_tracker.py` is a small script that checks for running processes on the local machine and records their status in a SQLite database. It can be packaged into an executable and run in the background.

### Setup

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install psutil
   ```

2. Add process names you want to track
   ```bash
   python process_tracker.py --add-process "chrome.exe" --add-process "notepad.exe"
   ```

3. Run the tracker
   ```bash
   python process_tracker.py
   ```

The script will check every five minutes and mark a process as `running`, `not running` or `dormant` if it has not been seen for more than ten minutes.

### Building an executable

You can bundle the script as a single executable with [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile process_tracker.py
```

The generated executable in the `dist` folder can be distributed to users and will update `process_tracker.db` in the same directory when run.
