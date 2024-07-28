import os
import cv2
import numpy as np
from PIL import Image
from fpdf import FPDF
import datetime

class DecodeFile:
    @staticmethod
    def get_video_path():
        video_path = input("Enter the path to the .mp4 video file: ")
        if not os.path.isfile(video_path):
            raise FileNotFoundError("The specified video file does not exist.")
        return video_path

    @staticmethod
    def extract_frames_from_video(video_path, frames_dir):
        print("Extracting frames from video...", end="", flush=True)
        
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        
        video_capture = cv2.VideoCapture(video_path)
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_number = 0
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_file_name = os.path.join(frames_dir, f"frame_{frame_number}.png")
            cv2.imwrite(frame_file_name, frame)
            frame_number += 1

        video_capture.release()
        print(" Done")
        return frames_dir

    @staticmethod
    def convert_frames_to_binary(frames_dir, binary_file_path):
        print("Converting frames to binary...", end="", flush=True)
        
        binary_data = ""

        frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".png")]
                             , key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[1]))

        # print(frame_files)
        
        for frame_file in frame_files:
            frame_path = os.path.join(frames_dir, frame_file)
            image = Image.open(frame_path).convert('L')
            binary_content = np.array(image)

            binary_frame = []
            for row in binary_content:
                binary_frame.append(''.join('0' if pixel < 128 else '1' for pixel in row))
            
            binary_data += ''.join(binary_frame)

        with open(binary_file_path, 'w') as binary_file:
            binary_file.write(binary_data)

        print(" Done")
        return binary_file_path

    @staticmethod
    def convert_binary_to_text(binary_file_path, text_file_path):
        print("Converting binary to text...", end="", flush=True)
        
        with open(binary_file_path, 'r') as binary_file:
            binary_content = binary_file.read()

        # Remove padding
        binary_content = binary_content.rstrip('1')
        
        text_data = bytearray()
        for i in range(0, len(binary_content), 8):
            byte = binary_content[i:i+8]
            if len(byte) == 8:
                text_data.append(int(byte, 2))

        with open(text_file_path, 'wb') as text_file:
            text_file.write(text_data)

        print(" Done")
        return text_file_path

    @staticmethod
    def convert_txt_to_original(txt_file_path):
        valid_extensions = ["pdf", "zip", "docx", "jpg", "png"]  # List of valid file extensions
        user_extension = input("Please enter the desired file extension (e.g., pdf, zip, docx, jpg, png): ").strip().lower()
        
        if user_extension in valid_extensions:
            try:
                new_file_name = txt_file_path.replace(".txt", f".{user_extension}")
                print(f"Converting .txt file to .{user_extension}...", end="", flush=True)
                with open(txt_file_path, 'r') as file:
                    content = file.read()

                # Save the content to the new file with the desired extension
                with open(new_file_name, 'w') as file:
                    file.write(content)

                print(" Done")
                return new_file_name
            except Exception as e:
                print(f"Error converting to {user_extension.upper()}: {e}")
                return None
        else:
            print("Invalid file extension. Please try again.")
            return None


def main():
    
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    decoded_videos_dir = f"decoded_videos/{current_time}"
    if not os.path.exists(decoded_videos_dir):
        os.makedirs(decoded_videos_dir)
    
    video_path = DecodeFile.get_video_path()
    
    frames_dir = os.path.join(decoded_videos_dir, "extracted_frames")
    binary_file_path = os.path.join(decoded_videos_dir, "frames_binary.txt")
    text_file_path = os.path.join(decoded_videos_dir, "text_from_binary.txt")

    DecodeFile.extract_frames_from_video(video_path, frames_dir)
    DecodeFile.convert_frames_to_binary(frames_dir, binary_file_path)
    DecodeFile.convert_binary_to_text(binary_file_path, text_file_path)
    pdf_file_path = DecodeFile.convert_txt_to_original(text_file_path)
    
    if pdf_file_path:
        print(f"Original file reconstructed and saved at: {pdf_file_path}")
    else:
        print("Failed to convert the text file to PDF.")

if __name__ == "__main__":
    main()
