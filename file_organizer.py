import configparser
import os
import shutil
from datetime import datetime, timedelta
from logger import log_info, log_error

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def organize_files_by_type(source_directory, organize_rules):
    for item in os.listdir(source_directory):                           # Here, you iterate through all the files in the provided directory. `os.listdir` lists all the files and folders in the specified path.
        source_path = os.path.join(source_directory, item)              # `os.path.join` is used to create the full path for each item.
        if os.path.isfile(source_path):                                 # It checks if the item is a file (not a folder) and gets the file extension, converting it to lowercase to ensure case-insensitive comparison.
            file_extension = item.split('.')[-1].lower()
            for folder, extensions in organize_rules.items():           # For each set of organization rules, it checks if the current file's extension matches any of those defined in the rules. If it matches, the file is moved to the designated folder, creating it if it doesn't exist.
                if file_extension in extensions:
                    target_directory = os.path.join(source_directory, folder)
                    os.makedirs(target_directory, exist_ok=True)
                    shutil.move(source_path, os.path.join(target_directory, item))
                    print(f'Moved: {item} ---> {target_directory}')
                    break

def archive_old_files(source_directory, days_threshold):                # This function archives files that are older than a certain number of days (days_threshold), moving them to an "Archive" folder.
    archive_directory = os.path.join(source_directory, "Archive")
    os.makedirs(archive_directory, exist_ok=True)
    threshold_date = datetime.now() - timedelta(days=days_threshold)

    for item in os.listdir(source_directory):
        # Check if the file is a file and not a directory
        if not os.path.isfile(os.path.join(source_directory, item)):
            continue
        # Check if the file is older than the threshold date
        last_modified_date = datetime.fromtimestamp(os.path.getmtime(os.path.join(source_directory, item)))
        if last_modified_date < threshold_date:
            shutil.move(os.path.join(source_directory, item), os.path.join(archive_directory, item))
            print(f'Archived: {item}')
        source_path = os.path.join(source_directory, item)
        if os.path.isfile(source_path):
            last_modified_date = datetime.fromtimestamp(os.path.getmtime(source_path))
            if last_modified_date < threshold_date:
                shutil.move(source_path, os.path.join(archive_directory, item))
                print(f'Archived: {item}')
    log_info(f'Archived files older than {days_threshold} days')

def main():
    config = load_config()
    source_directory = config['Settings']['source_directory']
    archive_threshold_days = int(config['Settings']['archive_threshold_days'])
    archive_enabled = config['Settings'].getboolean('archive_enabled')
    organize_rules = {section: extensions.split(', ') for section, extensions in config['OrganizeRules'].items()}

    organize_files_by_type(source_directory, organize_rules)
    if archive_enabled:
        archive_old_files(source_directory, archive_threshold_days)

if __name__ == "__main__":
    main()
