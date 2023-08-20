japanFlag = True

####EDIT NOTHING BELOW THIS####

import os
import shutil
import sys
import subprocess

intPath = "com.bandainamcoent.toluminaria" if japanFlag else "com.bandainamcoent.toluminaria_en"

if len(sys.argv) >= 3:
    targetDir = f'{sys.argv[1]}diff\\'
    pathToADB = sys.argv[2]
else:
    targetDir = "X:\\python\\luminaria\\diff\\"
    pathToADB = "M:\\Downloads\\platform-tools_r31.0.3-windows\\platform-tools\\adb.exe"
    
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
        
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

def parseLS(content):
    files = {}
    currentPath = ""
    contentToParse = content
    while len(contentToParse) > 0:
        currentPath = contentToParse.pop(0)[:-1]
        discard = contentToParse.pop(0)
        doneFlag = False
        while not doneFlag:
            currentLine = contentToParse.pop(0)
            if currentLine == '':
                doneFlag = True
            else:
                if currentLine[0] == "d":
                    pass
                else:
                    currentLine = currentLine[11:]
                    fileName = currentLine[currentLine.rfind(":")+4:]
                    data = currentLine.split(" ")
                    data = [item for item in data if item.strip()]
                    fileSize = data[3]
                    files[f'{currentPath}/{fileName}'] = fileSize
    return files
                    
def listfiles(path):
    try:
        files = {}
        for dirName, subdirList, fileList in os.walk(path):
            dir = dirName.replace(path, '')
            for fname in fileList:
                filename = os.path.join(dir, fname)
                try:
                    filesize = os.path.getsize(path+filename)
                except:
                    filesize = 0
                files[filename.replace("\\", "/")] = filesize
        return files
    except Exception as e:
        print(e)

def pullFile(targetPath):
    purePath = os.path.dirname(targetPath)
    newPath = f'{targetDir}{purePath.replace(f"/sdcard/Android/data/{intPath}/files/cache/","")}'.replace("/", "\\") + "\\"
    ensure_dir(newPath)
    result = subprocess.run([pathToADB, "pull", targetPath, newPath], stdout=subprocess.PIPE)
                    
result = subprocess.run([pathToADB, "shell", "ls", "-lR", f"/sdcard/Android/data/{intPath}/files/cache"], stdout=subprocess.PIPE, text=True)
try:
    x = listfiles('source_old')
    y = parseLS(result.stdout.split("\n"))
    modlist = []
    for item in y:
        if item[63:] in x:
            if int(x[item[63:]]) != int(y[item]):
                modlist.append(item)
        else:
            modlist.append(item)
    print(f'Pulling {len(modlist)} files from device.')
    for index, item in enumerate(modlist):
        pullFile(item)
        printProgressBar(index+1, len(modlist))
    changedFiles = "\n".join(sorted(modlist))
    changedFiles += f"\n{len(modlist)} files modified."
    with open("diffout.txt", "w") as file:
    # Writing data to a file
        file.write(changedFiles)
except Exception as e:
    print(str(e))                