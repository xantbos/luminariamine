targetDir = "X:\\python\\luminaria\\"
pathToADB = "M:\\Downloads\\platform-tools_r31.0.3-windows\\platform-tools\\adb.exe"

keepMapsFlag = False

####EDIT NOTHING BELOW THIS####

import os
import shutil
import sys
import subprocess

errString = "no devices/emulators found"

# pre-run lib check
try:
    import UnityPy
except ModuleNotFoundError:
    if os.path.isfile('requirements.txt'):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r' 'requirements.txt'])
        except Exception as e:
            print("Error occurred installing required packages. Please install 'requirements.txt' to run the script.")
            input("Press enter to terminate the script...")
            sys.exit()
    else:
        print("You are missing 'requirements.txt' which has required package details.")
        input("Press enter to terminate the script...")
        sys.exit()

#check for structure
if not os.path.isdir('decrypted_full'):
    os.mkdir("decrypted_full")

# did I clean up after my last run
if os.path.isdir('decrypted'):
    os.system('cmd /c "robocopy {0}decrypted\\caches {0}decrypted_full\\caches /E /MOVE"'.format(targetDir))
    if os.path.isdir('decrypted'):
        shutil.rmtree("decrypted")

if os.path.isfile('changed_files.txt'):
    os.remove('changed_files.txt')

if os.path.isfile('diffout.txt'):
    os.remove('diffout.txt')

# get to work you lazy sod
print("Attempting connection to android device...")
result = subprocess.run([pathToADB, "shell", "ls"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if errString in result.stderr:
    print("You need to plug in your android device via USB and have USB debugging enabled for this script to work.")
    input("Press enter key to terminate...")
else:
    print("Connection established!")
    #input("Press enter to run diffsource...")
    print("Diffing content between local copy and device copy...")# (a file will open once this script is completed)")
    os.system(f'cmd /c "py diffls.py {targetDir} {pathToADB}"')
    #os.system(r'start diffout.txt')
    print("You can unplug the phone now.")
    
    # nuke locations to save time
    if os.path.isdir('diff\\caches\\map\\location\\' and not keepMapsFlag):
        print("Pruning location maps to speed up decryption... (if you need these files toggle keepMapsFlag)")
        shutil.rmtree('diff\\caches\\map\\location\\')

    #input("Press enter to run decrypter...")
    print("Running decryption script...")
    os.system('cmd /c "py decrypter.py"')
    #input("Press enter to run newkeyfinder...")
    print("Diffing keys... (a file will open once this script is completed)")
    os.system('cmd /c "py newkeyfinder.py"')
    os.system(r'start changed_files.json')

    #input("Press enter to run cleanup scripts...")
    print("CLEANUP CREW GO!", end=" ")
    if os.path.isdir("diff"):
        print("\nMoving new files to master source...")
        result = subprocess.run(["robocopy", f'{targetDir}diff\\caches', f'{targetDir}source_old\\caches', "/E", "/MOVE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        #os.system('cmd /c "robocopy {0}diff\\caches {0}source_old\\caches /E /MOVE"'.format(targetDir))
        shutil.rmtree("diff")
    else:
        print("...but no cleanup was required.")
print("""
██████╗  ██████╗ ███╗   ██╗███████╗██╗
██╔══██╗██╔═══██╗████╗  ██║██╔════╝██║
██║  ██║██║   ██║██╔██╗ ██║█████╗  ██║
██║  ██║██║   ██║██║╚██╗██║██╔══╝  ╚═╝
██████╔╝╚██████╔╝██║ ╚████║███████╗██╗
╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝
""")
print("\nLuminaria mine complete. Enjoy your assets.")
input("\n\nPress enter key to terminate script...")