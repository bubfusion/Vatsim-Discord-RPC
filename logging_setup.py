from pypresence import Presence
import requests
import tkinter as tk
import customtkinter as ctk
import os
import sys
import configparser
from datetime import datetime, timezone
from update import check_for_update
from CTkMessagebox import CTkMessagebox
import webbrowser
import logging
from logging.handlers import RotatingFileHandler
import vatsim_api

log = None
roaming_path = os.path.join(os.getenv('APPDATA'), "VATSIM-Discord-RPC")
log_file = roaming_path + "\log.log"

def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    my_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, 
                                     backupCount=2, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    log = logging.getLogger('root')
    log.setLevel(logging.INFO)

    # Avoid adding multiple handlers if setup_logging is called more than once
    if not log.handlers:
        log.addHandler(my_handler)

    return log
