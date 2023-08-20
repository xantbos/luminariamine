####EDIT NOTHING BELOW THIS####

import json
import os 

originalpath = "decrypted_full\\caches\\lang_en\\texts\\commonterm\\"
newpath = "decrypted\\caches\\lang_en\\texts\\commonterm\\"

if os.path.isdir(originalpath) and os.path.isdir(newpath):
    try:
        changes = {}
        for file in os.listdir(newpath):
            keyTotal = 0
            print(f'Detecting new keys in {file}...'.ljust(43), end="")
            changes[file] = {}
            with open(f'{originalpath}{file}', 'r', encoding='utf-8') as old:
                olddata = json.load(old)
            with open(f'{newpath}{file}', 'r', encoding='utf-8') as new:
                newdata = json.load(new)
            fixedoldkeylist = {}
            fixednewkeylist = {}
            for values in newdata["m_Entries"]:
                fixednewkeylist[values["m_Id"]] = values["m_Value"]
            for values in olddata["m_Entries"]:
                fixedoldkeylist[values["m_Id"]] = values["m_Value"]
            
            # compare keys
            for key in fixednewkeylist:
                # if the key doesn't exist in old list, append
                if key in fixedoldkeylist:
                    if fixednewkeylist[key] != fixedoldkeylist[key]:
                        changes[file][key] = fixednewkeylist[key]
                        keyTotal+=1
                else:
                    changes[file][key] = fixednewkeylist[key]
                    keyTotal+=1
            print(f'{keyTotal} keys added or modified.'.rjust(26))
            
    except Exception as e:
        print(e)

    with open('changed_files.json', 'w', encoding='utf-8') as outfile:
         json.dump(changes, outfile, indent=2, ensure_ascii=False)
         
else:
    print("No keyfiles to diff.")