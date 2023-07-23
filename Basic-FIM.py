import hashlib
import os

file_list = []

# Read the list of files to monitor from files_to_monitor.conf
with open("files_to_monitor.conf", "r") as file:
    for line in file:
        line = line.strip()
        if line and not line.startswith("#"): #It ensures that only non-empty lines that are not commented out are processed.
            file_list.append(line)

state_file = "file_state.txt"
file_state = {}
# Initializes an empty dictionary that will be used to store the file state.
# The keys will be filenames, and the values will be the corresponding checksums.

# Read previous file state if it exists
if os.path.exists(state_file):
    # Checks if the state file exists in the file system.
    with open(state_file, "r") as state:
        # Opens the state file in read mode.
        for line in state:
            line = line.strip()
            if line:
                # Checks if the line is not empty.
                # Split the line into filename and checksum
                parts = line.split(":")
                filename = ":".join(parts[:-1])
                checksum = parts[-1]
                # Store the filename and checksum in the file_state dictionary
                file_state[filename] = checksum

changed_files = []

# Check for changes in file content
for filename in file_list:
    if os.path.isfile(filename):
        # Checks if the file exists.
        with open(filename, "rb") as file:
            content = file.read()
            # Calculate the SHA256 checksum of the file content
            checksum = hashlib.sha256(content).hexdigest()

        if filename in file_state:
            # Compare the checksum with the previous file state
            if checksum != file_state[filename]:
                # If the checksums don't match, add the filename to the changed_files list
                changed_files.append(filename)
        else:
            # If the file is new (not present in the previous file state), add it to the changed_files list
            changed_files.append(filename)

        # Update the file state with the new checksum
        file_state[filename] = checksum
    else:
        print(f"File '{filename}' does not exist!")

# Update the file state for future checks
with open(state_file, "w") as state:
    for filename, checksum in file_state.items():
        # Write the filename and checksum to the file_state.txt file
        state.write(f"{filename}:{checksum}\n")

# Output the changed files
if changed_files:
    print("The following files have changed:")
    for file in changed_files:
        print(file)
else:
    print("No changes detected.")
