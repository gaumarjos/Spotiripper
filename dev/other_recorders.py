if self.recorder == "PIEZO":
    subprocess.Popen(
        'osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"',
        shell=True, stdout=subprocess.PIPE).stdout.read()

elif self.recorder == "QT":
    subprocess.Popen(
        'osascript -e "tell application \\"QuickTime Player\\" to activate" -e "tell application \\"QuickTime Player\\" to start (new audio recording)"',
        shell=True, stdout=subprocess.PIPE).stdout.read()



if self.recorder == "PIEZO":
    subprocess.Popen(
        'osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"',
        shell=True, stdout=subprocess.PIPE).stdout.read()

elif self.recorder == "QT":
    command = ["osascript",
               "-e",
               "set tFile to \"" + self.tmp_storage_location + self.tmp_m4a_file_name + "\" as posix file",
               "-e", "do shell script \"touch \" & quoted form of posix path of tFile",
               "-e", "tell application \"QuickTime Player\"",
               "-e", "pause document 1",
               "-e", "save document 1 in tFile",
               "-e", "stop document 1",
               "-e", "close document 1 saving no",
               "-e", "quit",
               "-e", "end tell"]
    p = subprocess.Popen(command)

    time.sleep(1.000)
    print("Converting to mp3...")

    # Convert m4a to mp3 using ffmpeg
    try:
        subprocess.call(['ffmpeg', '-i', f'{self.tmp_storage_location + self.tmp_m4a_file_name}',
                         f'{self.tmp_storage_location + self.tmp_mp3_file_name}'])
    except Exception as e:
        print(e)
        print('Error While Converting Audio')