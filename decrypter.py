####EDIT NOTHING BELOW THIS####

import os
import UnityPy
import json

source_dir = "source"
extract_dir = "decrypted"

diffFlag = False

if os.path.exists("diff"):
    source_dir = "diff"
    diffFlag = True

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
        
def ensure_legal(file_name):
    invalid = '<>:"|?* '

    for char in invalid:
        file_name = file_name.replace(char, '_')
    if "Clone" in file_name:
        file_name = file_name.replace("Clone", "C")
    return file_name

def print_headers(allFile):
    print(f'Files to decrypt: {str(allFile)}')
    
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

def decrypt_asset(targetfolder, assetpath):
    env = UnityPy.load(assetpath)
    last_out = ""
    error_log = ""
    for obj in env.objects:
        try:
            if obj.type.name == "AudioClip":
                clip = obj.read()
                safe_name = ensure_legal(clip.name.replace("/", "\\"))
                ensure_dir(f'{targetfolder}\{safe_name}')
                for name, data in clip.samples.items():
                    with open(f'{targetfolder}\{safe_name}.wav', "wb") as f:
                        f.write(data)
            elif obj.type.name in ["Texture2D", "Sprite"]:
                data = obj.read()
                safe_name = ensure_legal(data.name.replace("/", "\\"))
                ensure_dir(f'{targetfolder}\{safe_name}')
                # create dest based on original path
                dest = f'{targetfolder}\{safe_name}'
                # correct extension
                dest, ext = os.path.splitext(dest)
                dest = dest + ".png"
                data.image.save(dest)
                if diffFlag:
                    ensure_dir(f'{extract_dir}\\_images\\{os.path.basename(dest)}')
                    data.image.save(f'{extract_dir}\\_images\\{os.path.basename(dest)}')
            elif obj.type.name == "TextAsset":
                # export asset
                data = obj.read()
                # check if sneaky video asset
                if "ftypmp4" in bytes(data.m_Script[4:11]).decode('utf-8'):
                    safe_name = ensure_legal(data.name.replace("/", "\\"))
                    #print(safe_name)
                    ensure_dir(f'{targetfolder}\{safe_name}')
                    #print(f'{targetfolder}\{safe_name}')
                    with open(f'{targetfolder}\{safe_name}.mp4', 'wb') as f:
                        f.write(data.m_Script)
                    if diffFlag:
                        ensure_dir(f'{extract_dir}\\_videos\\{os.path.basename(safe_name)}')
                        with open(f'{extract_dir}\\_videos\\{os.path.basename(safe_name)}.mp4', 'wb') as f:
                            f.write(data.m_Script)
                else:
                    with open(path, "wb") as f:
                        f.write(bytes(data.script))
                    # edit asset
                    fp = os.path.join(targetfolder, data.name)
                    with open(fp, "rb") as f:
                        data.script = f.read()
                    data.save()
            elif obj.type.name == "MonoBehaviour":
                data = obj.read()
                safe_name = ensure_legal(data.name.replace("/", "\\"))
                ensure_dir(f'{targetfolder}\{safe_name}')
                if obj.serialized_type.nodes:
                    # save decoded data
                    tree = obj.read_typetree()
                    fp = os.path.join(targetfolder, f"{safe_name}.json")
                    with open(fp, "wt", encoding = "utf8") as f:
                        json.dump(tree, f, ensure_ascii = False, indent = 4)
                else:
                    # save raw relevant data (without Unity MonoBehaviour header)
                    fp = os.path.join(targetfolder, f"{safe_name}.bin")
                    with open(fp, "wb") as f:
                        f.write(data.raw_data)
                # edit
                if obj.serialized_type.nodes:
                    tree = obj.read_typetree()
                    # apply modifications to the data within the tree
                    obj.save_typetree(tree)
                else:
                    with open(replace_dir, data.name) as f:
                        data.save(raw_data = f.read())
            elif obj.type.name == "Mesh":
                data = obj.read()
                safe_name = ensure_legal(data.name.replace("/", "\\"))
                ensure_dir(f'{targetfolder}\{safe_name}')
                with open(f'{targetfolder}\{safe_name}.obj', "wt", newline = "") as f:
                        # newline = "" is important
                        f.write(data.export())
            elif obj.type.name == "Font":
                font : Font = obj.read()
                if font.m_FontData:
                    extension = ".ttf"
                    if font.m_FontData[0:4] == b"OTTO":
                        extension = ".otf"

                with open(os.path.join(path, font.name+extension), "wb") as f:
                    f.write(font.m_FontData)
            elif obj.type.name == "GameObject":
                pass
                # data = obj.read()
                # if "em" in data.name:
                    # print(f'{data}\n{dir(data)}\n\n')
            elif obj.type.name == "AssetBundle":
                pass
            elif obj.type.name == "Transform":
                pass
            elif obj.type.name == "MonoScript":
                pass
            else:
                pass
                #print(f'Unhandled type {obj.type.name}')
            #print(f'Object {obj} processed.')
            last_out += f'{obj}, '
        except Exception as e:
            #print(f'Object {obj} failed: {e}')
            error_log += f'Object {obj} failed: {e}\n'
    return f'Object(s) {last_out[:-2]} processed.', error_log

def recursive_folder_search(folder):
    print("Populating file list...")
    totalFiles = 0
    currentFile = 0
    for root, folders, files in os.walk(folder):
        totalFiles += len(files)
    print_headers(totalFiles)
    last_out = ""
    error_log = ""
    for root, folders, files in os.walk(folder):
        targetroot = extract_dir + root[root.index("\\"):] if "\\" in root else ""
        #print(f'source: {root}\ntarget: {targetroot}\n\n')
        for file in files:
            currentFile += 1
            #print(root + file)
            #decrypt_asset(targetroot + "\\" , root + "\\" + file)
            last_out, error_log = decrypt_asset(targetroot + "\\" , root + "\\" + file)
            #print_output(currentFile, totalFiles, last_out, error_log)
            printProgressBar(currentFile, totalFiles)
    with open('errorlog.txt', "wt") as f:
        f.write(error_log)

recursive_folder_search(source_dir)
print("Finished!")