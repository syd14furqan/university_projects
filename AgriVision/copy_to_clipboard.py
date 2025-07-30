import pyperclip
import os
import sys

def copy_to_clipboard():
    try:
        file_path = os.path.join('data', 'attributes.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print("Error: File is empty")
            return False
            
        pyperclip.copy(content)
        print(f"Copied {len(content)} characters to clipboard")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = copy_to_clipboard()
    sys.exit(0 if success else 1)