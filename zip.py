import zipfile
import os

def zip_directory(directory_path, output_path):
    """
    压缩指定目录（不保留空文件夹）
    :param directory_path: 要压缩的目录路径
    :param output_path: 输出的zip文件路径
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算文件在zip中的相对路径
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)
    
    print(f"目录 '{directory_path}' 已成功压缩到 '{output_path}'")

# 使用示例
zip_directory('./Eyebin', './Eyebin.zip')
