import os
import shutil
import argparse
import colorama
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import settings_lib

DRYRUN = False

def list_mp3_files(file_folder, library_folder):
    """List all MP3 files in the given folder."""
    try:
        for filename in os.listdir(file_folder):
            if filename.endswith('.mp3'):
                full_path = os.path.join(file_folder, filename)  # Get full path
                organize(full_path, library_folder)  # Pass full path to allocate
    except FileNotFoundError:
        print(f"Error: The folder '{file_folder}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to access '{file_folder}'.")


def read_mp3_tags(file_path):
    """Read specified tags from an MP3 file."""
    try:
        # Load the MP3 file with EasyID3 for easy access to common tags
        audio = MP3(file_path, ID3=EasyID3)

        # Extract the desired tags
        author = audio.get('artist', ["Unknown Artist"])[0]  # Get artist name
        album = audio.get('album', ["Unknown Album"])[0]  # Get album name
        title = audio.get('title', ["Untitled"])[0]  # Get title

        # Get track number and disc number, return empty string if not found
        track_number = audio.get('tracknumber', [None])[0]
        disc_number = audio.get('discnumber', [None])[0]

        return {
            "author": author,
            "album": album,
            "title": title,
            "track_number": track_number,
            "disc_number": disc_number
        }

    except Exception as e:
        print(f"Error reading tags from {file_path}: {e}")
        return None


def organize(original_file_path, library_folder):
    """Copy MP3 file to a structured folder based on author and album."""
    print(f"Organizing: {original_file_path}")

    # Extract tags
    tags = read_mp3_tags(original_file_path)
    author = tags.get("author")
    album = tags.get("album")
    title = tags.get("title")
    track_number = tags.get("track_number")
    disc_number = tags.get("disc_number")

    # Create the directory structure: library_folder/author/album
    target_folder = os.path.join(library_folder, author, album)

    # Create the target folder if it does not exist
    os.makedirs(target_folder, exist_ok=True)

    # Construct the new filename
    if track_number is None:
        new_filename = f"{title}.mp3".strip()
        # print("No track number")
    elif disc_number is None:
        new_filename = f"{track_number} {title}.mp3".strip()
        # print("Track number but no disc number")
    else:
        new_filename = f"{disc_number}.{track_number} {title}.mp3".strip()
        # print("Both disc and track number")
    assert new_filename[0] != '.'

    # Full path for the new file
    new_file_path = os.path.join(target_folder, new_filename)

    # Check for overwriting
    if os.path.exists(new_file_path):
        print(colorama.Fore.LIGHTYELLOW_EX,
              f"Warning: The file already exists in the destination folder. No file has been overwritten, check destination folder for details.",
              colorama.Style.RESET_ALL)

        # Get current date and time for suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{disc_number}.{track_number} {title}_overwriting_attempt_{timestamp}.mp3".strip()
        new_file_path = os.path.join(target_folder, new_filename)

    # Copy the original MP3 file to the new location with the new name
    # shutil.copy2(original_file_path, new_file_path)
    if not DRYRUN:
        shutil.move(original_file_path, new_file_path)

    print(f" Moved to '{new_file_path}'")


def main():
    settings = settings_lib.load_settings()
    rip_dir = settings["rip_dir"]
    lib_dir = settings["lib_dir"]

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Organize the MP3 files ripped moving them into the user's music library.")
    parser.add_argument('-s', '--source_folder', type=str, default=rip_dir,
                        help='The folder containing MP3 files (default: lib_dir specified in settings.json).')
    parser.add_argument('-l', '--library_folder', type=str, default=lib_dir,
                        help='The music library folder (default: lib_dir specified in settings.json).')

    # Parse arguments
    args = parser.parse_args()

    # Organizing
    list_mp3_files(args.source_folder, args.library_folder)


if __name__ == "__main__":
    main()
