import os

def mapOpen():
    """
    Opens the Windows Maps application or falls back to web maps
    """
    try:
        # Try to open Windows Maps app
        os.system("explorer.exe shell:AppsFolder\\Microsoft.WindowsMaps_8wekyb3d8bbwe!App")
        print("Opening Windows Maps...")
    except Exception:
        # Fallback to web maps in default browser
        os.system("start https://www.google.com/maps")
        print("Opening web maps in browser...")

if __name__ == "__main__":
    mapOpen()