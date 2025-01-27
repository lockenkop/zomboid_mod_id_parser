from steam.webapi import WebAPI
import re
import httpx
import os
from bs4 import BeautifulSoup

api = None
# read the Steam API key from a file, if there is no file, the key will be None
try:
    with open('key.txt', 'r') as f:
        KEY = f.read().strip()
    api = WebAPI(key=KEY)
except FileNotFoundError:
    print("File 'key.txt' not found, trying environment variable")

try:
    KEY = os.environ['STEAM_API_KEY']
    api = WebAPI(key=KEY)
except KeyError:
    print("Environment variable 'STEAM_API_KEY' not found, defaulting to no key")
    
if not api:
    api = WebAPI(key=None)

def main():

    # specify the workshop ids of the mods you want to get the modnames of separated by a semicolon
    workshop_ids = ""
    if not workshop_ids:
        try:
            with open('workshop_ids.txt', 'r') as f:
                workshop_ids = f.read().strip()
        except FileNotFoundError:
            print("Please specify the workshop ids in the script, or create a file named 'workshop_ids.txt' and put the mod workshop ids in it")
            return False

    workshop_ids_list = workshop_ids.split(";")
    print(f"Found {len(workshop_ids_list)} workshop ids")
    modnames = []

    for workshop_id in workshop_ids_list:
        try:
            description = get_description_via_api(api, modnames, workshop_id)
            modname = find_modname(description)
            if modname:
                modnames.append(modname)
                continue
            else:    
                raise(KeyError)
        except:
            print(f"Failed to find modname for modid {workshop_id} via API\n trying via HTML")

            description = get_description_via_html(workshop_id)
            modname = find_modname(description)
            if modname:
                modnames.append(modname)
                continue
            else:
                print(f"Failed to find modname for modid {workshop_id} via HTML\nmake sure the mod description contains 'Mod ID: <modname>'")
                raise(KeyError)
            
    len_workshop_ids = len(workshop_ids_list)
    len_modnames = len(modnames)
    print(f"Found {len_modnames} modnames out of {len_workshop_ids} workshop ids")
    if len(workshop_ids_list) != len(modnames):
        print("Failed to get modnames for some mods")
        return False
    else:
        print("All modnames found")
    
    print("\n\n")
    print(';'.join(modnames))

def get_description_via_api(api, modnames, modid):
    response = api.ISteamRemoteStorage.GetPublishedFileDetails(itemcount=1, publishedfileids=[modid])
    description = response['response']['publishedfiledetails'][0]['description']
    return description
    

def get_description_via_html(modid):
    response = httpx.get('https://steamcommunity.com/sharedfiles/filedetails/?id=' + modid)
    soup = BeautifulSoup(response.text, 'html.parser')
    description_block = soup.find('div', class_='workshopItemDescription')
    description = description_block.get_text(strip=True)
    return description

def find_modname(description):
    matches = re.findall(r'Mod ID\s*:\s*([^\r\n]+)', description)
    if matches:
        return matches[0]

if __name__ == "__main__":
    main()
