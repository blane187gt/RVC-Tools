import os
import shutil
import subprocess
from mega import Mega  # Ensure this library is installed


def show_available(filepath,format=None):
    if format:
        print(f"Format: {format}")
        files = []
        for file in os.listdir(filepath):
            if file.endswith(format):
                print(f"Matches format: {file}")
                files.append(file)
            else:
                print(f"Does not match format: {file}")
        print(f"Matches: {files}")
        if len(files) < 1:
            return ['']
        return files
    if len(os.listdir(filepath)) < 1:
        return ['']
    return os.listdir(filepath)
def download_from_url(url, model=''):
    if not model:
        try:
            model = url.split('/')[-1].split('?')[0]
        except IndexError:
            return "You need to name your model. For example: My-Model", {"choices": show_available("assets/weights"), "__type__": "update"}
    
    url = url.replace('/blob/main/', '/resolve/main/', '/resolve/main/?download=true')
    model = model.replace('.pth', '').replace('.index', '').replace('.zip', '')
    print(f"Model name: {model}")

    if not url:
        return "URL cannot be left empty.", {"choices": show_available("assets/weights"), "__type__": "update"}
    
    url = url.strip()
    zip_dirs = ["zips", "unzips"]
    for directory in zip_dirs:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    os.makedirs("zips", exist_ok=True)
    os.makedirs("unzips", exist_ok=True)

    zipfile = model + '.zip'
    zipfile_path = './zips/' + zipfile

    try:
        if url.endswith('.pth'):
            subprocess.run(["wget", url, "-O", f'./assets/weights/{model}.pth'])
            return f"Successfully downloaded as {model}.pth", {"choices": show_available("assets/weights"), "__type__": "update"}
        elif url.endswith('.index'):
            os.makedirs(f'./logs/{model}', exist_ok=True)
            subprocess.run(["wget", url, "-O", f'./logs/{model}/added_{model}.index'])
            return f"Successfully downloaded as added_{model}.index", {"choices": show_available("assets/weights"), "__type__": "update"}
        
        if "drive.google.com" in url:
            subprocess.run(["gdown", url, "--fuzzy", "-O", zipfile_path])
        elif "mega.nz" in url:
            m = Mega()
            m.download_url(url, './zips')
        else:
            subprocess.run(["wget", url, "-O", zipfile_path])
        
        for filename in os.listdir("./zips"):
            file_path = os.path.join("./zips/", filename)
            if filename.endswith(".zip"):
                shutil.unpack_archive(file_path, "./unzips", 'zip')
                for root, dirs, files in os.walk('./unzips'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file.endswith(".index"):
                            os.makedirs(f'./logs/{model}', exist_ok=True)
                            shutil.copy2(file_path, f'./logs/{model}')
                        elif "G_" not in file and "D_" not in file and file.endswith(".pth"):
                            shutil.copy2(file_path, f'./assets/weights/{model}.pth')
            elif filename.endswith(".pth"):
                shutil.copy2(file_path, f'./assets/weights/{model}.pth')
            elif filename.endswith(".index"):
                os.makedirs(f'./logs/{model}', exist_ok=True)
                shutil.copy2(file_path, f'./logs/{model}/')
            else:
                return "No valid file found in the zip.", {"choices": show_available("assets/weights"), "__type__": "update"}
        
        shutil.rmtree("zips")
        shutil.rmtree("unzips")
        return "Success.", {"choices": show_available("assets/weights"), "__type__": "update"}
    except Exception as e:
        return f"There's been an error: {str(e)}", {"choices": show_available("assets/weights"), "__type__": "update"}
