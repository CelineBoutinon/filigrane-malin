import os
import sys

# Get the absolute directory where run.exe actually lives on the disk
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Force the working directory there
os.chdir(base_path)

from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = os.path.join(base_path, "app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())