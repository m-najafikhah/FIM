#File integrty monitoring new version
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(filename='file_monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def read_files_to_monitor(file_path):
    file_list = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    file_list.append(line)
        return file_list
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []

def read_previous_file_state(state_file):
    file_state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as state:
                for line in state:
                    line = line.strip()
                    if line:
                        parts = line.split(":")
                        filename = ":".join(parts[:-1])
                        checksum = parts[-1]
                        file_state[filename] = checksum
            logging.info(f"Previous file state loaded from '{state_file}'.")
        except Exception as e:
            logging.error(f"Error while reading previous file state: {str(e)}")
    return file_state

def save_current_file_state(state_file, file_state):
    try:
        with open(state_file, "w") as state:
            for filename, checksum in file_state.items():
                state.write(f"{filename}:{checksum}\n")
        logging.info("Current file state saved.")
    except Exception as e:
        logging.error(f"Error while saving current file state: {str(e)}")

def calculate_sha256_checksum(file_path):
    with open(file_path, "rb") as file:
        content = file.read()
        return hashlib.sha256(content).hexdigest()

def main():
    file_list = read_files_to_monitor("files_to_monitor.conf")
    state_file = "file_state.txt"
    file_state = read_previous_file_state(state_file)
    changed_files = []

    for filename in file_list:
        if os.path.isfile(filename):
            checksum = calculate_sha256_checksum(filename)
            if filename in file_state:
                if checksum != file_state[filename]:
                    changed_files.append(filename)
                    logging.info(f"File '{filename}' has changed.")
            else:
                changed_files.append(filename)
                logging.info(f"New file '{filename}' detected.")
            file_state[filename] = checksum
        else:
            logging.warning(f"File '{filename}' does not exist!")

    save_current_file_state(state_file, file_state)

    if changed_files:
        logging.info("The following files have changed:")
        for file in changed_files:
            logging.info(file)
    else:
        logging.info("No changes detected.")

if __name__ == "__main__":
    main()
