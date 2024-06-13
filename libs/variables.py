# variables.py
import customtkinter as ctk
from libs.loadSaveConf import *

LOGGED_USER = ''
LOGGED_USER_DB = ''
DB_STATE = 'Non connesso'
GUI_SCALE = 0
KEYWIDTH = 0
KEYHEIGHT = 0

def set_logged_user(username, db_name):
    global LOGGED_USER
    global LOGGED_USER_DB
    LOGGED_USER = username
    LOGGED_USER_DB = db_name

def set_gui_scale(scale):
    global GUI_SCALE
    GUI_SCALE = scale

def set_key_size(width, height):
    global KEYWIDTH
    global KEYHEIGHT
    KEYWIDTH = width
    KEYHEIGHT = height

def update_gui_scale(new_value):
    set_gui_scale(new_value)
    ctk.set_widget_scaling(GUI_SCALE/100)  # widget dimensions and text size
    save_config("gui_scale", GUI_SCALE)

def update_color(new_value):
    global COLOR
    COLOR = new_value
    save_config("color", COLOR)
    ctk.set_default_color_theme(load_config("color"))

def update_num_board(new_value):
    global NUM_BOARD_SIZE

    NUM_BOARD_SIZE = new_value
    save_config("keywidth", NUM_BOARD_SIZE)
    save_config("keyheight", NUM_BOARD_SIZE)
    set_key_size(NUM_BOARD_SIZE, NUM_BOARD_SIZE)
