from os import listdir, walk, makedirs
from os.path import dirname, join, exists
from pathlib import Path
import sys
import os
from shutil import copytree, Error
from time import strftime, perf_counter

from activity import get_activity_data
from maincache import read_cache_entry
from report import chat_to_html, report_cache, report_activity
from simplecache import read_simple_cache

def main_menu():
    home_path = str(Path.home())
    print("===================================================")
    print("DISCFOR MAIN MENU")
    print("===================================================")
    print("1. Extraction from current file system")
    print("2. Select folder for extraction")
    print("3. Quit")
    selection = input("\nEnter choice: ")
    if selection == "1":
        print("\nPlease provide output path")
        output_path = input().strip()
        if not output_path:
            output_path = sys.path[0]
        discord_path = system_search(home_path)
        recovery(discord_path, output_path)
    elif selection == "2":
        print("\nPlease provide path for extraction")
        target_path = input().strip()
        if not exists(target_path):
            print(f"ERROR: {target_path} does not exist!")
        elif "Cache" in listdir(target_path) and "Local Storage" in listdir(target_path):
            print("Please provide output path")
            output_path = input().strip()
            if not output_path:
                output_path = sys.path[0]
            recovery(target_path, output_path)
        else:
            print("\nThis is not a Discord directory or something is missing")
    elif selection == "3":
        exit()
    else:
        print("Invalid choice. Enter 1-3")
    main_menu()

def system_search(search_dir):
    print("\nSearching system...")
    for root, dirs, _ in walk(search_dir):
        if "Discord" in dirs:
            discord_path = join(root, "Discord")
            if exists(join(discord_path, "Cache")) and exists(join(discord_path, "Local Storage")):
                print("\nDiscord folder found under:\n" + discord_path)
                return discord_path
    print("\nDiscord folder not found")
    return None

def create_recovery_dir(discord_path, output_path, backup):
    current_time = strftime("%Y%m%d%H%M%S")
    output_dir = join(output_path, f"Dump_{current_time}")
    makedirs(join(output_dir, "Extracted", "Images"), exist_ok=True)
    makedirs(join(output_dir, "Extracted", "Chat_logs"), exist_ok=True)
    makedirs(join(output_dir, "Extracted", "Video"), exist_ok=True)
    makedirs(join(output_dir, "Extracted", "Audio"), exist_ok=True)
    makedirs(join(output_dir, "Extracted", "Other"), exist_ok=True)
    makedirs(join(output_dir, "Reports", "Chat_logs"), exist_ok=True)
    if backup:
        discord_path = create_backup(discord_path, output_dir)
    return output_dir, discord_path

def create_backup(discord_path, output_dir):
    makedirs(join(output_dir, "Dumps"), exist_ok=True)
    cache_path = join(discord_path, "Cache", "Cache_Data")
    if exists(cache_path):
        copytree(cache_path, join(output_dir, "Dumps", "Cache"))
    local_storage_path = join(discord_path, "Local Storage")
    copytree(local_storage_path, join(output_dir, "Dumps", "Local Storage"))
    return join(output_dir, "Dumps")

def recovery(discord_path, output_path):
    if not discord_path:
        print("No valid Discord path found.")
        return
    backup = input("\nDo you want to create data backup? (y/n): ").strip().lower() in ["y", "yes"]
    output_dir, discord_path = create_recovery_dir(discord_path, output_path, backup)
    
    cache_data_list, all_entries, recovered, empty_entries, reconstructed = ([], 0, 0, 0, 0)
    cache_path = join(discord_path, "Cache", "Cache_Data")
    if exists(join(cache_path, "data_0")):
        print("\nBeginning data extraction...")
        cache_data_list, all_entries, recovered, empty_entries, reconstructed = read_cache_entry(discord_path, output_dir)
    else:
        print("\nBeginning data extraction using simple cache...")
        cache_data_list, all_entries, recovered, empty_entries, reconstructed = read_simple_cache(discord_path, output_dir)
    
    servers, channels, mails = get_activity_data(discord_path)
    chat_to_html(cache_data_list, output_dir)
    report_cache(cache_data_list, output_dir)
    report_activity(servers, channels, mails, output_dir)
    
    print("\nExtraction completed.")
    print(f"Total Entries: {all_entries}, Recovered: {recovered}, Empty: {empty_entries}, Reconstructed: {reconstructed}")
    print("Results stored in:", output_dir)

main_menu()