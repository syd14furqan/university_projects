#Part 1: Capture Images of Multiple People
import cv2
import os

# Directory to store captured images
image_dir = "known_faces"

# Function to ensure the directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to capture images of multiple people and encode them
def capture_new_users(directory, num_people):
    cap = cv2.VideoCapture(0)
    for i in range(num_people):
        name = input(f"Enter name of person {i+1}: ")
        print(f"Capturing images for {name}. Press 'c' to capture an image.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            cv2.imshow('Capture Image', frame)
            if cv2.waitKey(1) & 0xFF == ord('c'):
                image_path = os.path.join(directory, f"{name}_{i+1}.jpg")
                cv2.imwrite(image_path, frame)
                print(f"Image captured and saved as {image_path}")
                break
    cap.release()
    cv2.destroyAllWindows()

# Main function for part 1
def main_part1():
    ensure_dir(image_dir)
    num_people = int(input("Enter the number of people to capture: "))
    capture_new_users(image_dir, num_people)

if _name_ == "_main_":
    main_part1()






#Part 2: Attendance System
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Directory to store captured images
image_dir = "known_faces"

# Function to encode faces in the images from a directory
def encode_faces_from_dir(directory):
    known_encodings = []
    known_names = []
    
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Failed to load image: {image_path}")
            continue
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) > 0:
            known_encodings.append(face_encodings[0])
            known_names.append(os.path.splitext(filename)[0])
    
    return known_encodings, known_names

# Function to mark attendance
def mark_attendance(known_encodings, known_names, attendance_listbox):
    cap = cv2.VideoCapture(0)
    print("Taking attendance. Press 'q' to stop.")

    recognized_faces = set()  # Set to keep track of recognized faces
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                
                # Check if this face has been recognized before
                if name not in recognized_faces:
                    # Add the recognized face to the set
                    recognized_faces.add(name)
                    
                    # Draw a rectangle around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Display the name
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Update attendance listbox
                    attendance_listbox.insert(tk.END, f"Name: {name}, Time: {current_time}, Present: Yes")
            
        cv2.imshow('Live Attendance', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Main function for part 2
def main_part2():
    # Create Tkinter window
    root = tk.Tk()
    root.title("Attendance")
    
    # Create a frame for attendance display
    attendance_frame = ttk.Frame(root)
    attendance_frame.pack(padx=10, pady=10)
    
    # Create a scrollbar for attendance listbox
    scrollbar = ttk.Scrollbar(attendance_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create a listbox to display attendance
    attendance_listbox = tk.Listbox(attendance_frame, yscrollcommand=scrollbar.set, width=50, height=20)
    attendance_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=attendance_listbox.yview)
    
    # Path to the attendance Excel file
    attendance_file_path = "attendance.xlsx"
    
    # Encode known faces from the directory
    known_encodings, known_names = encode_faces_from_dir(image_dir)
    
    print("Database recorded.")
    
    # Take live attendance
    mark_attendance(known_encodings, known_names, attendance_listbox)
    
    root.mainloop()

if _name_ == "_main_":
    main_part2()
