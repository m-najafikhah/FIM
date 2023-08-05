# Import necessary modules
import hashlib
import os
import logging
import subprocess

# Configure logging to log changes and errors to 'file_monitor.log' file
logging.basicConfig(filename='file_monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to read the list of files to be monitored from the configuration file
def read_files_to_monitor(file_path):
    file_list = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                # Ignore empty lines and lines starting with '#' (comments)
                if line and not line.startswith("#"):
                    file_list.append(line)
        return file_list
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []

# Function to read the previous state of the monitored files from the state file
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

# Function to save the current state of monitored files to the state file
def save_current_file_state(state_file, file_state):
    try:
        with open(state_file, "w") as state:
            for filename, checksum in file_state.items():
                state.write(f"{filename}:{checksum}\n")
        logging.info("Current file state saved.")
        # Set restrictive permissions for 'file_state.txt' to only allow the owner to read and write
        os.chmod(state_file, 0o600)
        if os.name == 'nt':
            # Windows system, use subprocess to set file permissions using icacls
            icacls_cmd1 = ["icacls", state_file, "/setowner", uid_of_monitoring_user] ##Please replace uid_of_monitoring_user with the actual username of the restricted user on Windows
            icacls_cmd2 = ["icacls", state_file, "/inheritance:r"]
            icacls_cmd3 = ["icacls", state_file, "/grant", uid_of_monitoring_user] ##Please replace uid_of_monitoring_user with the actual username of the restricted user on Windows
            subprocess.run(icacls_cmd1, shell=True, check=True)
            subprocess.run(icacls_cmd2, shell=True, check=True)
            subprocess.run(icacls_cmd3, shell=True, check=True)
    except Exception as e:
        logging.error(f"Error while saving current file state: {str(e)}")

# Function to calculate the SHA256 checksum of a given file
def calculate_sha256_checksum(file_path):
    with open(file_path, "rb") as file:
        content = file.read()
        return hashlib.sha256(content).hexdigest()

# Main function to monitor files
def main():
    # Read the list of files to monitor from 'files_to_monitor.conf'
    file_list = read_files_to_monitor("files_to_monitor.conf")
    # Load the previous state of monitored files from 'file_state.txt'
    state_file = "file_state.txt"
    file_state = read_previous_file_state(state_file)
    changed_files = []
    
    # Track files that are not present in the current monitoring session (i.e., deleted files)
    deleted_files = [filename for filename in file_state if filename not in file_list]

    for filename in file_list:
        if os.path.isfile(filename):
            # Calculate the SHA256 checksum of the file
            checksum = calculate_sha256_checksum(filename)
            if filename in file_state:
                if checksum != file_state[filename]:
                    # File content has changed since the last monitoring
                    changed_files.append(filename)
                    logging.info(f"File '{filename}' has changed.")
            else:
                # File is new and was not present in the previous monitoring state
                changed_files.append(filename)
                logging.info(f"New file '{filename}' detected.")
            file_state[filename] = checksum
        else:
            # File was present in the previous monitoring state but has been deleted
            if filename in file_state:
                deleted_files.append(filename)
                logging.info(f"File '{filename}' has been deleted!")

    # Remove deleted files from file_state
    for filename in deleted_files:
        file_state.pop(filename)
        logging.info("The " + filename + " removed from the config file.")

    # Save the current state of monitored files to 'file_state.txt'
    save_current_file_state(state_file, file_state)

    if changed_files:
        logging.info("The following files have changed:")
        for file in changed_files:
            logging.info(file)
    else:
        logging.info("No changes detected.")

# Entry point of the script
if __name__ == "__main__":
    # Set restrictive permissions for 'file_monitor.log' to only allow the owner to read and write
    os.chmod("file_monitor.log", 0o600)
    
    # Run the main function
    main()
