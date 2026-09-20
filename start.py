import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("=" * 65)
    print("  ID SHIELD - AI Anti-Fraud Identity Verification Portal")
    print("=" * 65)
    
    # 1. Install dependencies
    print("\n[1/2] Verifying and installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Note on package install: {e}")

    # 2. Run Flask app
    print("\n[2/2] Launching ID Shield on http://127.0.0.1:5050 ...")
    print("      Open your browser and navigate to: http://127.0.0.1:5050")
    print("      Press Ctrl+C in this terminal to stop the server.\n")

    # Launch app
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
