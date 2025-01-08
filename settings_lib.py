import json
import os

def create_settings():
    settings = {
        "rip_dir": os.path.expanduser('~') + '/Downloads/Ripped/',
        "ripped_folder_structure": "flat",
        "spotipy_client_id": "",
        "spotipy_client_secret": "",
        "lib_dir": os.path.expanduser('~') + '/Music/Discoteca/'
    }
    json_data = json.dumps(settings, indent=4)
    with open("settings.json", "w") as outfile:
        outfile.write(json_data)


def load_settings():
    with open("settings.json", "r") as j:
        settings = json.load(j)
    return settings


def write_setting(pairs):
    # Read settings
    with open('settings.json', 'r') as j_in:
        settings = json.load(j_in)

    for pair in pairs:
        key = pair[0]
        value = pair[1]

        # Validate values
        if key == "rip_dir":
            if not value.endswith("/"):
                value = value + "/"

        # Modify settings
        settings[key] = value

    # Write settings
    json_data = json.dumps(settings, indent=4)
    with open("settings.json", "w") as j_out:
        j_out.write(json_data)
