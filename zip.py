import zipfile
import os

def zip_directory(directory_path, output_path):

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)
    
    print(f"Directory '{directory_path}' has been compressed to '{output_path}'")

zip_directory('./Eyebin', './Eyebin.zip')
