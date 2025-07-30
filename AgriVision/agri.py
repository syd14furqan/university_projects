import cv2
import os
import sys
import numpy as np
import logging
from datetime import datetime

def calculate_green_area():
    """
    Process images from working_images directory to identify green areas.
    Returns a dictionary with processing status and file paths.
    """
    # Set up logging
    log_file = os.path.join("data", "processing_log.txt")
    os.makedirs("data", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting green area calculation at {datetime.now()}")
    
    response = {
        'status': 'error',
        'message': 'Unknown error',
        'files': {
            'original': '',
            'mask': '',
            'result': ''
        },
        'metrics': {
            'total_pixels': 0,
            'green_pixels': 0,
            'green_percentage': 0,
            'estimated_real_percentage': 0  # Added for zoom scale adjusted percentage
        }
    }

    try:
        # 1. Verify input directory exists (correct the directory name)
        input_dir = "working images"  # Match the name used in the Shiny app
        if not os.path.exists(input_dir):
            error_msg = f"'{input_dir}' directory not found"
            logger.error(error_msg)
            response['message'] = error_msg
            return response

        # 2. Check for images
        images = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not images:
            error_msg = f"No images found in '{input_dir}' folder"
            logger.error(error_msg)
            response['message'] = error_msg
            return response

        # Log found images
        logger.info(f"Found {len(images)} images. Using {images[0]}")

        # 3. Process first image
        img_path = os.path.join(input_dir, images[0])
        img = cv2.imread(img_path)
        if img is None:
            error_msg = f"Failed to read image: {img_path}"
            logger.error(error_msg)
            response['message'] = error_msg
            return response

        # Get image dimensions for logging
        height, width, channels = img.shape
        logger.info(f"Image dimensions: {width}x{height}, {channels} channels")

        # 4. Process image with improved green detection for BMS College area
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Multiple green color ranges to capture different types of vegetation
        # First range - bright green vegetation
        lower_green1 = np.array([35, 40, 40])
        upper_green1 = np.array([85, 255, 255])
        mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
        
        # Second range - olive/darker greens
        lower_green2 = np.array([28, 30, 30])
        upper_green2 = np.array([34, 255, 255])
        mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
        
        # Combine masks
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((3, 3), np.uint8)  # Smaller kernel for more detail
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Create result with green areas highlighted
        res = cv2.bitwise_and(img, img, mask=mask)
        
        # Add a green overlay for better visualization
        green_highlight = np.zeros_like(img)
        green_highlight[:,:] = [0, 255, 0]  # Pure green
        green_overlay = cv2.bitwise_and(green_highlight, green_highlight, mask=mask)
        
        # Blend original with highlight
        alpha = 0.3  # Transparency factor
        res = cv2.addWeighted(res, 1, green_overlay, alpha, 0)
        
        # Calculate green area metrics
        total_pixels = width * height
        green_pixels = cv2.countNonZero(mask)
        green_percentage = (green_pixels / total_pixels) * 100 if total_pixels else 0
        
        # Apply zoom scale correction - this will adjust the percentage based on zoom level
        # Assuming a medium zoom level in urban/campus area, multiply by a correction factor
        # The factor is higher for urban areas where green space is more scattered
        zoom_correction_factor = 1.8  # Adjusted for urban/campus satellite imagery
        estimated_real_percentage = min(green_percentage * zoom_correction_factor, 100.0)
        
        # Store metrics in response
        response['metrics'] = {
            'total_pixels': total_pixels,
            'green_pixels': green_pixels,
            'green_percentage': round(green_percentage, 2),
            'estimated_real_percentage': round(estimated_real_percentage, 2)
        }
        
        logger.info(f"Green area calculation: {green_pixels} green pixels out of {total_pixels} total pixels")
        logger.info(f"Raw percentage: {green_percentage:.2f}%")
        logger.info(f"Zoom adjusted percentage: {estimated_real_percentage:.2f}%")

        # 5. Save outputs with absolute paths (in parent directory as in original Shiny code)
        output_files = {
            'original': os.path.abspath("original.png"),
            'mask': os.path.abspath("mask.png"),
            'result': os.path.abspath("result.png")
        }
        
        # Save additional detailed results to data folder
        data_files = {
            'original_data': os.path.join("data", "original.png"),
            'mask_data': os.path.join("data", "mask.png"),
            'result_data': os.path.join("data", "result.png")
        }

        # Save images
        cv2.imwrite(output_files['original'], img)
        cv2.imwrite(output_files['mask'], mask)
        cv2.imwrite(output_files['result'], res)
        
        # Save copies to data folder too
        for key, path in data_files.items():
            if key == 'original_data':
                cv2.imwrite(path, img)
            elif key == 'mask_data':
                cv2.imwrite(path, mask)
            elif key == 'result_data':
                cv2.imwrite(path, res)
        
        # 6. Save green area percentage to a text file
        with open(os.path.join("data", "green_area.txt"), 'w') as f:
            f.write(f"Image: {img_path}\n")
            f.write(f"Total Pixels: {total_pixels}\n")
            f.write(f"Green Pixels: {green_pixels}\n")
            f.write(f"Raw Green Area Percentage: {green_percentage:.2f}%\n")
            f.write(f"Zoom-Adjusted Green Area Percentage: {estimated_real_percentage:.2f}%\n")
            f.write(f"Zoom Correction Factor: {zoom_correction_factor}\n")
            f.write(f"Analysis Date: {datetime.now()}\n")
            f.write(f"Location: BMS College of Engineering, Bangalore\n")

        # 7. Verify outputs were created
        if all(os.path.exists(f) for f in output_files.values()):
            response.update({
                'status': 'success',
                'message': 'Processing completed successfully',
                'files': output_files
            })
            logger.info("Processing completed successfully")
        else:
            missing_files = [f for f in output_files.values() if not os.path.exists(f)]
            error_msg = f"Failed to save output files: {missing_files}"
            logger.error(error_msg)
            response['message'] = error_msg

    except Exception as e:
        error_msg = f"Error in calculate_green_area: {str(e)}"
        logger.error(error_msg, exc_info=True)
        response['message'] = error_msg

    return response

# Run the function if script is executed directly
if __name__ == "__main__":
    result = calculate_green_area()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result['status'] == 'success':
        print(f"Raw green percentage: {result['metrics']['green_percentage']}%")
        print(f"Zoom-adjusted green percentage: {result['metrics']['estimated_real_percentage']}%")