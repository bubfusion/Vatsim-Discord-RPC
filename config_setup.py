import os
import sys
import configparser

def resource_path(relative_path):
    '''Used for VATSIM.ico file during compiling'''
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_config():
    # Path for config.ini
    roaming_path = os.path.join(os.getenv('APPDATA'), "VATSIM-Discord-RPC")

    # If path does not exist, then creates it
    if not os.path.exists(roaming_path):
        os.makedirs(roaming_path)

    # Stores path for config file
    ini_file_path = os.path.join(roaming_path, 'config.ini')


    # If the config file does not exist, creates it with needed info
    if not os.path.exists(ini_file_path):
        with open(ini_file_path, 'w') as ini_file:
            ini_file.write('[Settings]\n')
            ini_file.write('cid=\n')

    # Config parser for reading and writing
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    return(config, ini_file_path)