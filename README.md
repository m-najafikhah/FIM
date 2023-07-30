# FIM
File Integrity Monitoring
FIM is a tool used to monitor changes in files and identify unauthrized 
modifications. It helps detect and alert us to suspicious activities on 
our files, indicating possible attacks on our systems.

This is Basic File integrity Monitoring for a folder in any OS, But I just tested it on Windows 11.

When the script is run for the first time it can process all the files in the input list and store their current state. 
When the script is run again it is able to detect changes in the content of the files being monitored and will notify the user who is running the script.

I'd like to develop this tool. in the first step I'm going to add logging 
and create some function for organization of the code.
