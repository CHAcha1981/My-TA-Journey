import os
from PIL import Image

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def check_textures(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        if not (is_power_of_two(width) and is_power_of_two(height)):
                            print(f"{file}: {width}x{height}")
                except Exception as e:
                    print(f"Failed to open {file_path}: {e}")

if __name__ == "__main__":
    folder = input("请输入要检查的文件夹路径: ")
    check_textures(folder)



