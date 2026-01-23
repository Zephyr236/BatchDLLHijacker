import zipfile
import os
from concurrent.futures import ThreadPoolExecutor
MAX_WORKERS = min(32, os.cpu_count() * 4 + 1)

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
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in entries:
            if i.is_file():
                # print(i.path)
                # unzip(i.path)
                executor.submit(unzip,i.path)
