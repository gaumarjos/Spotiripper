import os
import shutil
import argparse
import colorama
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import settings_lib


def organize(mp3_file, library_folder):
    """Process the MP3 file name."""
    print(f"Organizing: {mp3_file}")
    copy_and_organize_mp3(mp3_file, library_folder)


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
        author = audio.get('artist', ["Unknown"])[0]  # Get artist name
        album = audio.get('album', ["Unknown"])[0]  # Get album name
        title = audio.get('title', ["Unknown"])[0]  # Get title

        # Get track number and disc number, return empty string if not found
        track_number = audio.get('tracknumber', [""])[0] if audio.get('tracknumber') else ""
        disc_number = audio.get('discnumber', [""])[0] if audio.get('discnumber') else ""

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


def copy_and_organize_mp3(original_file_path, library_folder):
    """Copy MP3 file to a structured folder based on author and album."""
    # Extract tags
    tags = read_mp3_tags(original_file_path)
    author = tags.get("author", "Unknown Artist")
    album = tags.get("album", "Unknown Album")
    title = tags.get("title", "Untitled")
    track_number = tags.get("track_number", "").strip()  # Remove any extra spaces
    disc_number = tags.get("disc_number", "").strip()  # Remove any extra spaces

    # Create the directory structure: library_folder/author/album
    target_folder = os.path.join(library_folder, author, album)

    # Create the target folder if it does not exist
    os.makedirs(target_folder, exist_ok=True)

    # Construct the new filename
    new_filename = f"{disc_number}.{track_number} {title}.mp3".strip()

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
    shutil.copy2(original_file_path, new_file_path)

    print(f" Copied to '{new_file_path}'")


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
    list_mp3_files(args.file_folder, args.library_folder)


if __name__ == "__main__":
    main()
