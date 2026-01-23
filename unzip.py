import zipfile
import os
def unzip(file):
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(file.replace(".zip",""))
            print(f"unzip {file}")
    except:
        print(f"{file} error")
        os.remove(file)

folder='download'
with os.scandir(folder) as entries:
    for i in entries:
        if i.is_file():
            # print(i.path)
            unzip(i.path)
