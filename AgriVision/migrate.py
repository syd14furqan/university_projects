import shutil
import os
from datetime import datetime, timedelta
import logging
import platform

def migrate_screenshots():
    """
    Migrate screenshots from common locations to the working directory.
    Returns the count of files successfully copied.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='migration_log.txt',
        filemode='a'
    )
    
    # Define paths based on operating system
    if platform.system() == "Windows":
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        screenshots_path = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
    elif platform.system() == "Darwin":  # macOS
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        screenshots_path = os.path.join(os.path.expanduser("~"), "Pictures")
    else:  # Linux
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        screenshots_path = os.path.join(os.path.expanduser("~"), "Pictures")
    
    destination_path = "working images"  # Relative path in the app directory
    
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
        logging.info(f"Created destination directory: {destination_path}")
    
    # Get recent time (last 24 hours)
    one_day_ago = datetime.now() - timedelta(days=1)
    
    # Image file extensions to look for
    image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
    
    # Screenshot name patterns to look for
    screenshot_patterns = ("screenshot", "image", "capture", "snip", "screen", "print")
    
    # Count of moved files
    moved_count = 0
    
    # Function to check and copy images
    def process_directory(directory_path):
        nonlocal moved_count
        
        if not os.path.exists(directory_path):
            logging.warning(f"Directory does not exist: {directory_path}")
            return
        
        logging.info(f"Checking {directory_path} for screenshots...")
        
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                
                # Check if file is a screenshot by extension and optionally by name
                is_image = filename.lower().endswith(image_extensions)
                
                # For Desktop, be more strict about naming
                if directory_path == desktop_path:
                    is_screenshot = any(pattern in filename.lower() for pattern in screenshot_patterns)
                    if not (is_image and is_screenshot):
                        continue
                else:
                    # For Screenshots folder, any image is fine
                    if not is_image:
                        continue
                
                # Check if file is readable and recent (last 24 hours)
                try:
                    # Get file creation time as a datetime object
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    # Check if file is recent - fixed comparison
                    if file_time > one_day_ago:
                        # Copy the file to the destination folder (use copy instead of move to preserve originals)
                        dest_file = os.path.join(destination_path, filename)
                        
                        # Handle duplicate filenames
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_file):
                            dest_file = os.path.join(destination_path, f"{base}_{counter}{ext}")
                            counter += 1
                        
                        shutil.copy2(file_path, dest_file)
                        logging.info(f"Copied {filename} to {destination_path} as {os.path.basename(dest_file)}")
                        moved_count += 1
                except (PermissionError, OSError) as e:
                    logging.error(f"Error accessing {file_path}: {str(e)}")
                    continue
        except Exception as e:
            logging.error(f"Error processing directory {directory_path}: {str(e)}")
    
    # Process Desktop
    process_directory(desktop_path)
    
    # Process Screenshots folder
    process_directory(screenshots_path)
    
    log_message = f"Migration complete. Copied {moved_count} screenshots."
    logging.info(log_message)
    print(log_message)
    
    return moved_count

# Run the function if script is executed directly
if __name__ == "__main__":
    result = migrate_screenshots()
    print(f"Copied {result} screenshots")