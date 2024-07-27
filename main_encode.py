import os
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

class OpenFile:
    def __init__(self, file_name):
        self.file = file_name
        self.new_dir_name = None
        self.base_name = None

    def convert_pdf_to_txt(self):
        print("Converting .pdf to .txt...", end="", flush=True)
        try:
            with open(self.file, "rb") as file:
                content = file.read()
        except Exception as e:
            print(f" Error: {e}")
            return None

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_name = os.path.basename(self.file).replace('.pdf', '')
        self.new_dir_name = f"history/{current_time}_{self.base_name}"
        os.makedirs(self.new_dir_name, exist_ok=True)

        new_file_name = f"{self.new_dir_name}/{self.base_name}.txt"
        with open(new_file_name, "wb") as new_file:
            new_file.write(content)

        print(" Done")
        return new_file_name

class BinaryConvert:
    @staticmethod
    def convert_to_binary(file_path, chunk_size=1024*1024):
        print("Converting to Binary...", end="", flush=True)
        binary_file_name = file_path.replace(".txt", "_binary.txt")

        with open(file_path, 'rb') as input_file, open(binary_file_name, 'w') as binary_file:
            while True:
                chunk = input_file.read(chunk_size)
                if not chunk:
                    break
                binary_chunk = ''.join(format(byte, '08b') for byte in chunk)
                binary_file.write(binary_chunk)

        print(" Done")
        return binary_file_name

    @staticmethod
    def convert_to_frames(file_path, new_dir_name, chunk_size=1280*720, padding_value="0"):
        print("Converting to Frames...", end="", flush=True)
        
        frames_dir = os.path.join(new_dir_name, "binary_frames")
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)

        with open(file_path, 'r') as binary_file:
            chunk_number = 0
            while True:
                chunk = binary_file.read(chunk_size)
                if not chunk:
                    break
                
                padding_length = chunk_size - len(chunk)
                padded_chunk = chunk + padding_value * padding_length
                
                chunk_file_name = os.path.join(frames_dir, f"chunk_{chunk_number}.txt")
                with open(chunk_file_name, 'w') as chunk_file:
                    chunk_file.write(padded_chunk)
                chunk_number += 1

        print(" Done")
        return frames_dir

class ConvertImage:
    @staticmethod
    def convert_frames_to_images(frames_dir, new_dir_name):
        print("Converting frames to images...", end="", flush=True)
        
        images_dir = os.path.join(new_dir_name, "image_frames")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        frame_files = sorted([f for f in os.listdir(frames_dir) if f.startswith("chunk_")])
        
        for frame_file in frame_files:
            with open(os.path.join(frames_dir, frame_file), 'r') as file:
                binary_content = file.read()

            binary_data = np.array([int(b) for b in binary_content], dtype=np.uint8)
            width, height = 1280, 720
            binary_data = binary_data.reshape((height, width))
            
            image = Image.fromarray(binary_data * 255)
            image = image.convert('L')

            image_file_name = os.path.join(images_dir, f"{os.path.splitext(frame_file)[0]}.png")
            image.save(image_file_name)

        print(" Done")
        return images_dir

class ConvertVideo:
    @staticmethod
    def create_video_from_frames(frames_dir, video_file_path, width=1280, height=720, fps=30):
        print("Creating video from frames...", end="", flush=True)
        
        frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".png")]
                             ,key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[1]))
        if not frame_files:
            raise ValueError("No frame files found in the specified directory.")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_file_path, fourcc, fps, (width, height))
        
        for frame_file in frame_files:
            frame_path = os.path.join(frames_dir, frame_file)
            frame = cv2.imread(frame_path)
            if frame is None:
                print(f"Warning: {frame_file} could not be read.")
                continue
            video_writer.write(frame)
        
        video_writer.release()
        print(" Done")
        return video_file_path

def main():

    file = input("Enter the path to the file you want converted to a video file: ")

    while not os.path.isfile(file):
        FileNotFoundError("The specified file does not exist.")
        file = input("Enter the path to the file you want converted to a video file: ")
        if file.lower() in ['exit', 'e', 'q', 'quit']:
            print("Exiting program...")
            exit(0)

    open_file = OpenFile(file)
    
    txt_file = open_file.convert_pdf_to_txt()
    if txt_file is None:
        return

    bin_file = BinaryConvert.convert_to_binary(txt_file)
    frames_dir = BinaryConvert.convert_to_frames(bin_file, open_file.new_dir_name)
    
    image_converter = ConvertImage()
    images_dir = image_converter.convert_frames_to_images(frames_dir, open_file.new_dir_name)
    
    video_converter = ConvertVideo()
    video_file_path = os.path.join(open_file.new_dir_name, "output_video.mp4")
    video_file = video_converter.create_video_from_frames(images_dir, video_file_path)

if __name__ == "__main__":
    main()
