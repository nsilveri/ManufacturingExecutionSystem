import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from ctkdlib.custom_widgets import *
from CTkMessagebox import CTkMessagebox
from CTkTable import *
import psycopg2
from psycopg2 import sql
import time
from datetime import datetime, timedelta
import sys
import subprocess
import json
import os
from libs import CTkPopupKeyboard
import tkinter as tk
import shutil
#from CTkPDFViewer import *

ORIGINAL_WIDTH =  800
ORIGINAL_HEIGHT = 500

LOGGED_USER = ''
LOGGED_USER_DB = ''
DB_STATE = 'Non connesso'

DRAW_NUM = ''

PADX = 5
ELAPSED_TIME_LABEL_X = 0.1
ELAPSED_TIME_LABEL_Y = 0.3
RELY_TIMER_BUTTONS = 0.59

DATA_ORDER_CHANGE = False

TABLE_ORDERS_ROW = 10

UPDATE_TIMER_DELAY = 100

LOAD_TEMP = True
MENU_MODIFICA_DATI = False

selected_row = None
selected_column = None
prev_selected_row = None
prev_selected_column= None
column_name = None
column_value = None
new_date = None

recent_orders = []

selected_checkbox = None
selected_checkbox_text = ''

root_width = ORIGINAL_WIDTH
root_height = ORIGINAL_HEIGHT

selected_order = None

numpad_x = 0
numpad_y = 0

db_index_names = {
    1: "orario_inizio",
    2: "orario_fine",
    3: "numero_disegno",
    4: "tempo_taglio",
    5: "tempo_tornitura",
    6: "tempo_fresatura",
    7: "tempo_elettroerosione",
    8: "tempo_ciclo_totale",
    9: "tempo_setup",
    10: "numero_pezzi",
    11: "note_lavorazione"
}

def load_config(conf_item, default=None):
    default_config = {
        "gui_scale": 0,
        "theme": "Light",
        "color": "blue",
        "pg_host": "",
        "pg_port": "",
        "pg_user": "",
        "pg_passwd": "",
        "draw_directory": "",
        "draw_mode_checkbox": 1,
        "keywidth": 75,
        "keyheight": 75,
        "num_board_scale": 100,
        "update_directory": ""
    }
    
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
            if conf_item in config_data:
                return config_data[conf_item]
            else:
                print(f"Configuration '{conf_item}' not found, adding to config file with default value.")
                config_data[conf_item] = default
                with open("config.conf", "w") as updated_config_file:
                    json.dump(config_data, updated_config_file)
                return default
    except FileNotFoundError:
        # Se il file di configurazione non esiste, creiamo un nuovo file di configurazione con le impostazioni predefinite
        print(f"Configuration file not found, creating new config file with default value for '{conf_item}'.")
        config_data = default_config
        with open("config.conf", "w") as new_config_file:
            json.dump(config_data, new_config_file)
        return default_config[conf_item]

def save_config(conf_item, value):
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        config_data = {}

    config_data[conf_item] = value

    with open("config.conf", "w") as config_file:
        json.dump(config_data, config_file)

ctk.set_appearance_mode(load_config("theme"))
ctk.set_default_color_theme(load_config("color"))

db_config = {
    'host':     load_config('pg_host'),      #'SPH-SERVER-PRODUZIONE'
    'port':     load_config('pg_port'),      #'5432',
    'user':     load_config('pg_user'),      #'postgres',
    'password': load_config('pg_passwd')     #'SphDbProduzione'
}

def update_gui_scale(new_value):
    global GUI_SCALE
    GUI_SCALE = new_value
    save_config("gui_scale", GUI_SCALE)

def update_num_board(new_value):
    global NUM_BOARD_SIZE
    global KEYWIDTH
    global KEYHEIGHT
    NUM_BOARD_SIZE = new_value
    save_config("keywidth", NUM_BOARD_SIZE)
    save_config("keyheight", NUM_BOARD_SIZE)
    KEYWIDTH = NUM_BOARD_SIZE
    KEYHEIGHT = NUM_BOARD_SIZE

def update_color(new_value):
    global COLOR
    COLOR = new_value
    save_config("color", COLOR)
    ctk.set_default_color_theme(load_config("color"))

THEME = load_config("theme", "blue")
GUI_SCALE = load_config("gui_scale", 0)
COLOR = load_config("color", "blue")
KEYWIDTH = load_config("keywidth", 75)
KEYHEIGHT = load_config("keyheight", 75)

selected_start_datetime = None

def restart_program():
    python = sys.executable
    subprocess.call([python, sys.argv[0]])

def _map(value, from_low, from_high, to_low, to_high):
    # Mappa il valore dall'intervallo di partenza all'intervallo di destinazione
    if to_high != 0:
        return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low
    else:
        return value
    
def _map_win_x(value):
    value_adapted = int(_map(value, 0, ORIGINAL_WIDTH, 0, root_width))
    return value_adapted

def _map_win_y(value):
    value_adapted = int(_map(value, 0, ORIGINAL_HEIGHT, 0, root_height))
    return value_adapted

def _map_rel_x(value):
    value_adapted = int(_map(value, 0, ORIGINAL_WIDTH, 0, root_width))
    return value_adapted

def _map_rel_y(value):
    value_adapted = int(_map(value, 0, ORIGINAL_HEIGHT, 0, root_height))
    return value_adapted

def _map_frame_x(value):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, value, 0, (value + GUI_SCALE)))
        #print("value_frame_x: " + str(value) + "---> " + str(value_adapted))
        return value_adapted
    else:
        return value

def _map_frame_y(value):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, value, 0, (value + GUI_SCALE)))
        #print("value_frame_y: " + str(value) + "---> " + str(value_adapted) + "")
        return value_adapted
    else:
        return value
    
def _map_item_x(value, frame_dim_x):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, frame_dim_x, 0, (frame_dim_x + GUI_SCALE)))
        #print("value_item_x: " + str(value) + "---> " + str(value_adapted))
        return value_adapted
    else:
        return value

def _map_item_y(value, frame_dim_y):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, frame_dim_y, 0, (frame_dim_y + GUI_SCALE)))
        #print("value_item_y: " + str(value) + "---> " + str(value_adapted) + "")
        return value_adapted
    else:
        return value


def switch_page(page):
    pages = [home_page, singup_page, login_page, modify_order_page]
    for i in pages:
        i.pack_forget()
    page.pack(expand=True, fill='both')

    fixed_widgets = []
    for widget in fixed_widgets:
        widget.lift()
        widget.place(x=widget.winfo_x(), y=widget.winfo_y())

def ask_question_choice(message):
     # Creazione del messaggio di messagebox
    msg = CTkMessagebox(
        master= home_page,
        title="Conferma ordine", 
        message= message,
        width=500,
        icon="question", 
        option_1="Conferma", 
        option_2="No" 
    )

    # Ottieni la risposta dal messagebox
    response = msg.get()
    
    if response=="Conferma":
        return True
    elif response=="No":
        return False

root = ctk.CTk()
root.title("MES Industry")
root.geometry((f"{ORIGINAL_WIDTH}x{ORIGINAL_HEIGHT}"))
root.resizable(False, False)

home_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
home_page.pack(expand=True, fill='both')
singup_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
login_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
modify_order_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)

def check_draw_exist_connection(db_config, codice_disegno):
    try:
        # Connessione al database
        conn = psycopg2.connect(**{**db_config, 'dbname': LOGGED_USER_DB})
        cur = conn.cursor()

        # Esegue la query per verificare se il codice di disegno esiste nella tabella 'ordini'
        cur.execute("SELECT * FROM ordini WHERE numero_disegno = %s", (codice_disegno,))
        records = cur.fetchall()  # Recupera tutti i record corrispondenti alla query
        conn.close()

        if records:
            # Se ci sono record corrispondenti, restituisci tutti i dati dei record trovati
            print(f"records: {records}")
            return records
        else:
            print("Nessun record trovato.")
            return None

    except (Exception, psycopg2.DatabaseError) as error:
        print("Errore durante la connessione al database:", error)
        return None

def get_pdf_files_in_directory(directory_path):
    # Verifica se il percorso specificato è una directory
    if not os.path.isdir(directory_path):
        print(f"{directory_path} non è una directory valida.")
        return []

    pdf_files = []
    roots = set()
    pdf_names = set()

    # Attraversa ricorsivamente tutte le sottocartelle
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file).replace(directory_path, '')
                pdf_files.append(full_path)
                roots.add(root)
                pdf_names.add(os.path.splitext(file)[0])

    if len(roots) == 1:
        # Se tutti i file PDF si trovano nella stessa directory, aggiungi solo i nomi dei PDF a pdf_files
        pdf_files = list(pdf_names)
    else:
        # Se ci sono PDF in directory diverse, aggiungi i percorsi completi
        pdf_files = list(pdf_files)

    print(f"\nroots: {len(roots)} - {roots}")
    print(f"\nfiles: {len(pdf_files)} - {pdf_files}")

    return pdf_files

directory_path = load_config("draw_directory")
file_list = get_pdf_files_in_directory(directory_path)

#FRAME TITLE
FRAME_TITLE_WIDTH = 152
FRAME_TITLE_HEIGHT = 40
frame_app_title = ctk.CTkFrame(
    master=home_page, 
    width=_map_item_x(162, FRAME_TITLE_WIDTH), 
    height=_map_item_y(40, FRAME_TITLE_HEIGHT)
    )

frame_app_title.place(x=0, y=0)

label_app_title = ctk.CTkLabel(
    master=frame_app_title,
    font=ctk.CTkFont(
        'Roboto',
        size=26),
    bg_color=[
        'gray86',
        'gray17'],
    height=0,
    text="MES Industry",
    justify="left")
label_app_title.place(x=0, y=0)


#FRAME CONNESSIONE
FRAME_CONN_WIDTH = 152
FRAME_CONN_HEIGHT = 30

frame_connection_title = ctk.CTkFrame(
    master=home_page, 
    width=_map_frame_x(FRAME_CONN_WIDTH),
    height=_map_frame_y(FRAME_CONN_HEIGHT)
    )



connection_state_text = "Utente: " + LOGGED_USER + "DB: " + DB_STATE

label_connessione = ctk.CTkLabel(
    master=frame_connection_title,
    font=ctk.CTkFont(
        'Roboto',
        size=15),
    bg_color=['gray86','gray17'],
    height=10,
    text= connection_state_text,
    justify="left")

label_connessione.place(x=_map_item_x(10, FRAME_CONN_WIDTH), rely=0.2)

def update_db_user_state():
    if(LOGGED_USER == ''):
        LOGGED_USER_AUX = 'Ness.utente'
    else:
        LOGGED_USER_AUX = LOGGED_USER
    connection_state_text = "Accesso: " + LOGGED_USER_AUX + " DB: " + str(DB_STATE)  + "    "
    label_connessione.configure(text=connection_state_text)

    # Calcola la larghezza del testo del messaggio di stato della connessione
    text_width = ctk.CTkFont('Roboto', size=15).measure(connection_state_text)

    # Aggiorna la larghezza del frame e del label in base alla larghezza del testo
    frame_connection_title.configure(width=_map_frame_x(text_width + 10))  # Aggiungi un po' di spazio extra
    label_connessione.configure(width=_map_frame_x(text_width + 10))

    # Ora posiziona il label al centro del frame
    label_connessione.place(x=_map_item_x(10, FRAME_CONN_WIDTH), rely=0.5, anchor="w")  # Ancoraggio a sinistra

#FRAME LOGIN SETTINGS
LOG_SET_FRAME_WIDTH = 106# + 20
LOG_SET_FRAME_HEIGHT = 40# + 20
frame_log_setting = ctk.CTkFrame(
    master=home_page, 
    width=_map_frame_x(LOG_SET_FRAME_WIDTH), 
    height=_map_frame_y(LOG_SET_FRAME_HEIGHT)
    )

login_button = ctk.CTkButton(
    master=frame_log_setting,
    bg_color=[
        'gray86',
        'gray17'],
    width=_map_item_x(50 + 5, LOG_SET_FRAME_WIDTH),
    height=_map_item_y(30 + 5, LOG_SET_FRAME_HEIGHT),
    text="Login",
    command=lambda: switch_page(login_page))

login_button.place(x=_map_item_x(6, LOG_SET_FRAME_WIDTH), y=_map_item_y(4, LOG_SET_FRAME_HEIGHT))

setting_button = ctk.CTkButton(
    master=frame_log_setting,
    bg_color=[
        'gray86',
        'gray17'],
    compound="left",
    width=_map_item_x(36 + 5, LOG_SET_FRAME_WIDTH),
    height=_map_item_y(30 + 5, LOG_SET_FRAME_HEIGHT),
    text="",
    image=ctk.CTkImage(
        Image.open(r'libs\gear_icon.png'),
        size=(20,20)),
        command=lambda: switch_page(singup_page))
setting_button.place(x=_map_item_x(64, LOG_SET_FRAME_WIDTH), y=_map_item_y(4, LOG_SET_FRAME_HEIGHT))

#FRAME SETUP TIME 
SETUP_TIME_FRAME_WIDTH = 210
SETUP_TIME_FRAME_HEIGHT_MANUAL = 100
SETUP_TIME_FRAME_HEIGHT_AUTO = 150

setup_paused_time = 0  # Variabile per memorizzare il tempo trascorso prima della pausa
setup_elapsed_time = 0  # Variabile per memorizzare il tempo trascorso total
elapsed_seconds = 0
setup_minutes = 0
setup_seconds = 0
time_setup_timer_current_button = None

# Funzione per avviare il setup
def start_setup():
    global setup_start_time, setup_paused_time, setup_elapsed_time, time_setup_timer_current_button
    time_setup_timer_current_button = 'start'
    setup_button_stop.configure(state= "enabled")
    setup_button_inizio.configure(state= "disabled")
    if setup_start_time is None:
        setup_start_time = time.time()
    else:
        # Se c'è un tempo di pausa memorizzato, aggiungilo al tempo trascorso
        setup_paused_time = time.time() - setup_paused_time  # Calcola il tempo di pausa
        setup_start_time += setup_paused_time  # Aggiungi il tempo di pausa al tempo iniziale
    update_elapsed_time_setup()  # Avvia l'aggiornamento del tempo trascorso

# Funzione per fermare il setup
def stop_setup():
    global setup_start_time, setup_paused_time, setup_elapsed_time, time_setup_timer_current_button
    time_setup_timer_current_button = 'stop'
    setup_button_stop.configure(state= "disabled")
    setup_button_inizio.configure(state= "enabled")
    if setup_start_time is not None:
        setup_paused_time = time.time()  # Memorizza il tempo trascorso prima della pausa
        setup_elapsed_time += setup_paused_time - setup_start_time  # Aggiorna il tempo totale trascorso
        # setup_start_time = None  # Non resettare setup_start_time

# Funzione per resettare il setup
def reset_setup(type_req = None):
    global setup_start_time, setup_paused_time, setup_elapsed_time, time_setup_timer_current_button, setup_minutes, setup_seconds
    if type_req == None:
        if(not ask_question_choice("Sei sicuro di voler resettare il timer di setup?")):
            return
    time_setup_timer_current_button = 'reset'
    setup_button_stop.configure(state="disabled")
    setup_button_inizio.configure(state= "enabled")
    setup_start_time = None  # Resetta setup_start_time
    setup_paused_time = 0  # Resetta il tempo di pausa
    setup_elapsed_time = 0  # Resetta il tempo trascorso totale
    setup_minutes = 0
    setup_seconds = 0
    setup_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso


#GENERAZIONE FRAME
frame_setup_time = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(SETUP_TIME_FRAME_WIDTH), 
    height=_map_frame_y(SETUP_TIME_FRAME_HEIGHT_MANUAL)
)

#GENERAZIONE LABEL
tempo_setup_label = ctk.CTkLabel(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di setup (min)"
)
tempo_setup_label.place(x=_map_item_x(18, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(6, SETUP_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_setup_num = CTkSpinbox(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=_map_item_x(76, SETUP_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, SETUP_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20']
)
tempo_setup_num.place(x=_map_item_x(10, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(43, SETUP_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE CHECKBOX
setup_time_checkbox = ctk.CTkCheckBox(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_setup_time
setup_time_checkbox.place(relx=0.65, rely=0.1)

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
setup_button_inizio = ctk.CTkButton(
    master=frame_setup_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: start_setup()
)

setup_button_stop = ctk.CTkButton(
    master=frame_setup_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: stop_setup()
)

setup_button_reset = ctk.CTkButton(
    master=frame_setup_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: reset_setup()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
setup_time_elapsed_label = ctk.CTkLabel(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'], 
    text="{:d}:{:02d}".format(setup_minutes, setup_seconds)
)
setup_time_elapsed_label.place(relx=0.1, rely=0.6)

setup_start_time = None

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_setup():
    global time_setup_timer_current_button, elapsed_seconds, setup_seconds, setup_minutes, setup_start_time
    if setup_start_time is not None and time_setup_timer_current_button == 'start':
        if tempo_setup_num.get() != setup_minutes and not setup_time_checkbox.get():
            time_diff = int(tempo_setup_num.get()) - setup_minutes
            time_diff_seconds = time_diff * 60
            setup_start_time -= time_diff_seconds

        elapsed_seconds = int(time.time() - setup_start_time)
        setup_minutes = elapsed_seconds // 60
        setup_seconds = elapsed_seconds % 60
        setup_time_elapsed_label.configure(text="{:d}:{:02d}".format(setup_minutes, setup_seconds))
        if setup_minutes != tempo_setup_num.get() and setup_time_checkbox.get():
            tempo_setup_num.configure(value=setup_minutes)
    frame_setup_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_setup)  # Richiama se stesso ogni secondo

def carica_temp():
    global LOAD_TEMP
    global selected_start_datetime, tempo_setup_num, pezzi_select_num, tempo_taglio_num, tempo_fresatura_num, tempo_tornitura_num, tempo_elettro_num, menu_tendina_disegni, draw_num_entry, note_num_entry
    default_temp = {"selected_start_datetime": None, "tempo_setup_num": 0, "pezzi_select_num": 0, "tempo_taglio_num": 0, "tempo_fresatura_num": 0, "tempo_tornitura_num": 0, "tempo_elettro_num": 0, "menu_tendina_disegni": "Sel. num. disegno", "draw_num_entry": "", "note_num_entry": ""}
    if LOAD_TEMP:
        if LOGGED_USER != '':
            file_name = f"{LOGGED_USER}_temp.json"
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
                    print(data == default_temp)
                    print(f'data: {data} \ndefa: {default_temp}')
                if(data == default_temp):
                    print("dati default trovati")
                    return
                restore = ask_question_choice(f"Sono stati trovati dati precedentemente inseriti per l'utente {LOGGED_USER}, vuoi ripristinarli?")
                if not restore:
                    LOAD_TEMP = False
                    return
                LOAD_TEMP = False

                # Imposta le variabili globali con i valori dal file JSON
                selected_start_datetime = data["selected_start_datetime"]
                start_time_time_elapsed_label.configure(text= selected_start_datetime)
                tempo_setup_num.configure(value= data["tempo_setup_num"])
                pezzi_select_num.configure(value= data["pezzi_select_num"])
                tempo_taglio_num.configure(value= data["tempo_taglio_num"])
                tempo_fresatura_num.configure(value= data["tempo_fresatura_num"])
                tempo_tornitura_num.configure(value= data["tempo_tornitura_num"])
                tempo_elettro_num.configure(value= data["tempo_elettro_num"])
                menu_tendina_disegni.set(str(data["menu_tendina_disegni"]))
                #draw_num_entry.configure(textvariable= str(data["draw_num_entry"])) qui c'è UN BUG
                #note_num_entry.configure(textvariable= str(data["note_num_entry"]))

                LOAD_TEMP = False

            except FileNotFoundError:
                # Se il file non esiste, non fare nulla
                LOAD_TEMP = False
                pass

# Dati precedenti
previous_data = {}

def salva_temp():
    global LOAD_TEMP
    global selected_start_datetime, previous_data
    #print(LOAD_TEMP)
    if LOGGED_USER != '' and not LOAD_TEMP:
        # Dati attuali
        current_data = {
            "selected_start_datetime": selected_start_datetime,
            "tempo_setup_num": tempo_setup_num.get(),
            "pezzi_select_num": pezzi_select_num.get(),
            "tempo_taglio_num": tempo_taglio_num.get(),
            "tempo_fresatura_num": tempo_fresatura_num.get(),
            "tempo_tornitura_num": tempo_tornitura_num.get(),
            "tempo_elettro_num": tempo_elettro_num.get(),
            "menu_tendina_disegni": menu_tendina_disegni.get(),
            "draw_num_entry": draw_num_entry.get(),
            "note_num_entry": note_num_entry.get()
        }

        # Confronta con i dati precedenti
        if current_data != previous_data:
            file_name = f"{LOGGED_USER}_temp.json"  # Nome del file JSON con la variabile user
            with open(file_name, 'w') as f:
                json.dump(current_data, f)
            previous_data = current_data

        # Richiama la funzione salva_temp dopo un certo intervallo di tempo
    root.after(1000, lambda: salva_temp())

# Esegui la funzione salva_temp all'inizio
salva_temp()

# Logica per mostrare i pulsanti solo quando il checkbox è selezionato
def setup_toggle_buttons():
    global setup_start_time, setup_minutes, setup_seconds
    if setup_time_checkbox.get():
        tempo_setup_num.place_forget()
        #frame_setup_time.place(x=0, rely=0.5, anchor='w')
        #if(setup_start_time != None):
        #    setup_button_inizio.configure(text="Riprendi")
        setup_button_inizio.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
        setup_button_stop.place(relx=0.4, rely=RELY_TIMER_BUTTONS)
        setup_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
        setup_time_elapsed_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
        setup_time_elapsed_label.configure(text="{:d}:{:02d}".format(setup_minutes, setup_seconds))
        tempo_setup_label.configure(text="Tempo di setup")
        setup_minutes = tempo_setup_num.get()
        #frame_setup_time.configure(height=_map_frame_y(SETUP_TIME_FRAME_HEIGHT_AUTO))
        #setup_start_time = time.time()
        update_elapsed_time_setup()  # Avvia l'aggiornamento del tempo trascorso
    else:
        setup_button_inizio.place_forget()
        setup_button_stop.place_forget()
        setup_button_reset.place_forget()
        setup_time_elapsed_label.place_forget()
        tempo_setup_num.place(x=_map_item_x(10, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(43, SETUP_TIME_FRAME_HEIGHT_MANUAL))
        #setup_start_time = None
        tempo_setup_label.configure(text="Tempo di setup(min)")
        #setup_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso
        tempo_setup_num.configure(value=setup_minutes)

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
setup_time_checkbox.configure(command=setup_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
setup_toggle_buttons()

from datetime import datetime

def show_datetime_dialog():
    global selected_start_datetime

    def save_datetime():
        global selected_start_datetime
        selected_date = datetime.strptime(f"{day_spinbox.get()}/{month_spinbox.get()}/{year_spinbox.get()}", "%d/%m/%Y")
        selected_hour = int(hour_spinbox.get())
        selected_minute = int(minute_spinbox.get())
        selected_start_datetime = datetime(selected_date.year, selected_date.month, selected_date.day, selected_hour, selected_minute)
        print("Data e ora inserite:", selected_start_datetime)
        start_time_time_elapsed_label.configure(text= selected_start_datetime)
        dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

    current_date = datetime.now()
    current_hour = current_date.hour
    current_minute = current_date.minute

    dialog = ctk.CTkToplevel()
    dialog.title("Inserisci data e ora d'inizio")

    ctk.CTkLabel(master=dialog, text="Data:").grid(row=0, column=0, padx=5, pady=5)
    day_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=1, to=31, height=44, value=current_date.day)
    day_spinbox.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(master=dialog, text="/").grid(row=0, column=2)
    month_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=1, to=12, height=44, value=current_date.month)
    month_spinbox.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(master=dialog, text="/").grid(row=0, column=4)
    year_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=current_date.year, to=current_date.year + 100, height=44, value=current_date.year)
    year_spinbox.grid(row=0, column=5, padx=5, pady=5)

    ctk.CTkLabel(master=dialog, text="Ora:").grid(row=1, column=0, padx=5, pady=5)
    hour_spinbox = CTkSpinbox(master=dialog, button_width=50, from_=0, to=23, width=76, height=44, value=current_hour)
    hour_spinbox.grid(row=1, column=1, padx=5, pady=5)
    
    ctk.CTkLabel(master=dialog, text="Minuti:").grid(row=1, column=2, padx=5, pady=5)
    minute_spinbox = CTkSpinbox(master=dialog, button_width=50, from_=0, to=59, width=76, height=44, value=current_minute)
    minute_spinbox.grid(row=1, column=3, padx=5, pady=5)

    save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_datetime)
    save_button.grid(row=2, column=0, columnspan=6, padx=5, pady=5)

    dialog.lift()
    dialog.focus_set()  
    dialog.grab_set()   
    dialog.wait_window()



def set_start_time(MODE):
    global selected_start_datetime
    if MODE == 'current_date':
        selected_start_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        start_time_time_elapsed_label.configure(text= selected_start_datetime)
        print(selected_start_datetime)
    elif MODE == 'set_date':
        show_datetime_dialog()
        print(selected_start_datetime)

#FRAME START TIME
START_TIME_FRAME_WIDTH = 210
START_TIME_FRAME_HEIGHT = 100

#GENERAZIONE FRAME
frame_start_time = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(START_TIME_FRAME_WIDTH), 
    height=_map_frame_y(START_TIME_FRAME_HEIGHT)
)

#GENERAZIONE LABEL
tempo_start_time_label = ctk.CTkLabel(
    master=frame_start_time, 
    bg_color=['gray86', 'gray17'], 
    text="Data e ora d'inizio"
)
tempo_start_time_label.place(x=_map_item_x(18, START_TIME_FRAME_WIDTH), y=_map_item_y(6, START_TIME_FRAME_HEIGHT))

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
start_time_button_inizia_ora = ctk.CTkButton(
    master=frame_start_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Inizia ora",
    command=lambda: set_start_time('current_date')
)

start_time_button_imposta = ctk.CTkButton(
    master=frame_start_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Imposta",
    command=lambda: set_start_time('set_date')
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
start_time_time_elapsed_label = ctk.CTkLabel(
    master=frame_start_time, 
    bg_color=['gray86', 'gray17'], 
    text= 'Da impostare'
)
start_time_time_elapsed_label.place(relx=0.1, rely=0.3)
start_time_button_inizia_ora.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
start_time_button_imposta.place(relx=0.5, rely=RELY_TIMER_BUTTONS)
#start_time_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
#tempo_start_time_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
#tempo_start_time_label.configure(text="Data e ora")
tempo_setup_label.configure(text="Tempo di setup")

#FRAME TIMES CONTAINER
CONTAINER_TIME_FRAME_WIDTH = 890
CONTAINER_TIME_FRAME_HEIGHT = 110
CONTAINER_TIME_FRAME_HEIGHT_AUTO = 160

frame_container_time = ctk.CTkScrollableFrame(
    master=home_page, 
    width=CONTAINER_TIME_FRAME_WIDTH, 
    height=CONTAINER_TIME_FRAME_HEIGHT,
    orientation='horizontal',
    fg_color= "transparent"
    
    )#ctk.CTkScrollableFrame(label_text="CTkScrollableFrame")

frame_container_time.grid_columnconfigure(0, weight=110)
#frame_container_time.pack()
frame_container_time.place_forget()

#FRAME TAGLIO TIME 
TAGLIO_TIME_FRAME_WIDTH= 210
TAGLIO_TIME_FRAME_HEIGHT_MANUAL = 100
TAGLIO_TIME_FRAME_HEIGHT_AUTO = 150

taglio_paused_time = 0 
taglio_elapsed_time = 0  
taglio_elapsed_seconds = 0
taglio_minutes = 0
taglio_seconds = 0
time_taglio_timer_current_button = None

# Funzione per avviare il taglio
def start_taglio():
    global taglio_start_time, taglio_paused_time, taglio_elapsed_time, time_taglio_timer_current_button
    time_taglio_timer_current_button = 'start'
    taglio_button_stop.configure(state= "enabled")
    taglio_button_inizio.configure(state= "disabled")
    if taglio_start_time is None:
        taglio_start_time = time.time()
    else:
        # Se c'è un tempo di pausa memorizzato, aggiungilo al tempo trascorso
        taglio_paused_time = time.time() - taglio_paused_time  # Calcola il tempo di pausa
        taglio_start_time += taglio_paused_time  # Aggiungi il tempo di pausa al tempo iniziale
    update_elapsed_time_taglio()  # Avvia l'aggiornamento del tempo trascorso

# Funzione per fermare il taglio
def stop_taglio():
    global taglio_start_time, taglio_paused_time, taglio_elapsed_time, time_taglio_timer_current_button
    time_taglio_timer_current_button = 'stop'
    taglio_button_stop.configure(state= "disabled")
    taglio_button_inizio.configure(state= "enabled")
    if taglio_start_time is not None:
        taglio_paused_time = time.time()  # Memorizza il tempo trascorso prima della pausa
        taglio_elapsed_time += taglio_paused_time - taglio_start_time  # Aggiorna il tempo totale trascorso
        #taglio_start_time = None  # Resetta taglio_start_time


def somma(primo_num, sec_num):
    print(primo_num+sec_num)

somma(5,6)
# Funzione per resettare il taglio
def reset_taglio(type_req = None):
    global taglio_start_time, taglio_paused_time, taglio_elapsed_time, time_taglio_timer_current_button, taglio_minutes, taglio_seconds
    if type_req == None:
        if(not ask_question_choice("Sei sicuro di voler resettare il timer di taglio?")):
            return
    time_taglio_timer_current_button = 'reset'
    taglio_button_stop.configure(state="disabled")
    taglio_button_inizio.configure(state= "enabled")
    taglio_start_time = None  # Resetta taglio_start_time
    taglio_paused_time = 0  # Resetta il tempo di pausa
    taglio_elapsed_time = 0  # Resetta il tempo trascorso totale
    taglio_minutes = 0
    taglio_seconds = 0
    taglio_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso


#GENERAZIONE FRAME
frame_taglio_time = ctk.CTkFrame(
    master=frame_container_time,
    width=TAGLIO_TIME_FRAME_WIDTH,#_map_frame_x(TAGLIO_TIME_FRAME_WIDTH),
    height=TAGLIO_TIME_FRAME_HEIGHT_MANUAL#_map_frame_y(TAGLIO_TIME_FRAME_HEIGHT)
    )

#GENERAZIONE LABEL
taglio_time_label = ctk.CTkLabel(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di taglio (min)"
)
taglio_time_label.place(x=_map_item_x(18, TAGLIO_TIME_FRAME_WIDTH), y=_map_item_y(6, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_taglio_num = CTkSpinbox(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=_map_item_x(76, TAGLIO_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, TAGLIO_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20']
)
tempo_taglio_num.place(x=_map_item_x(10, TAGLIO_TIME_FRAME_WIDTH), y=_map_item_y(43, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE CHECKBOX
taglio_time_checkbox = ctk.CTkCheckBox(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_container_time
taglio_time_checkbox.place(relx=0.65, rely=0.1)

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
taglio_button_inizio = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: start_taglio()
)

taglio_button_stop = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: stop_taglio()
)

taglio_button_reset = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: reset_taglio()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
taglio_time_elapsed_label = ctk.CTkLabel(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text="{:d}:{:02d}".format(taglio_minutes, taglio_seconds)
)
taglio_time_elapsed_label.place(relx=0.1, rely=0.6)

taglio_start_time = None

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_taglio():
    global time_taglio_timer_current_button, taglio_elapsed_seconds, taglio_seconds, taglio_minutes, taglio_start_time
    if taglio_start_time is not None and time_taglio_timer_current_button == 'start':
        if tempo_taglio_num.get() != taglio_minutes and not taglio_time_checkbox.get():
            time_diff = int(tempo_taglio_num.get()) - taglio_minutes
            time_diff_seconds = time_diff * 60
            taglio_start_time -= time_diff_seconds

        taglio_elapsed_seconds = int(time.time() - taglio_start_time)
        taglio_minutes = taglio_elapsed_seconds // 60
        taglio_seconds = taglio_elapsed_seconds % 60
        taglio_time_elapsed_label.configure(text="{:d}:{:02d}".format(taglio_minutes, taglio_seconds))
        if(taglio_minutes > tempo_taglio_num.get() and taglio_time_checkbox.get()):
            tempo_taglio_num.configure(value= taglio_minutes)
    frame_container_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_taglio)  # Richiama se stesso ogni secondo

# Logica per mostrare i pulsanti solo quando il checkbox è selezionato
def taglio_toggle_buttons():
    RELY_TIMER_BUTTONS = 0.6
    global taglio_start_time, taglio_minutes, taglio_seconds, PADX
    if taglio_time_checkbox.get():
        tempo_taglio_num.place_forget()
        #frame_taglio_time.grid(row=0, column=0, padx=PADX)
        #if(taglio_start_time != None):
        #    taglio_button_inizio.configure(text="Riprendi")
        taglio_button_inizio.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
        taglio_button_stop.place(relx=0.4, rely=RELY_TIMER_BUTTONS)
        taglio_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
        taglio_time_elapsed_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
        taglio_time_elapsed_label.configure(text="{:d}:{:02d}".format(taglio_minutes, taglio_seconds))
        taglio_time_label.configure(text="Tempo di taglio")
        #frame_container_time.configure(height=_map_frame_y(TAGLIO_TIME_FRAME_HEIGHT_MANUAL))
        #taglio_start_time = time.time()
        update_elapsed_time_taglio()  # Avvia l'aggiornamento del tempo trascorso
    else:
        taglio_button_inizio.place_forget()
        taglio_button_stop.place_forget()
        taglio_button_reset.place_forget()
        taglio_time_elapsed_label.place_forget()
        tempo_taglio_num.place(x=_map_item_x(10, TAGLIO_TIME_FRAME_WIDTH), y=_map_item_y(43, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))
        #taglio_start_time = None
        taglio_time_label.configure(text="Tempo di taglio(min)")
        #taglio_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso
        tempo_taglio_num.configure(value=taglio_minutes)

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
taglio_time_checkbox.configure(command=taglio_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
taglio_toggle_buttons()

#FRAME TORNITURA TIME 
TORNITURA_TIME_FRAME_WIDTH = 210
TORNITURA_TIME_FRAME_HEIGHT_MANUAL = 100
TORNITURA_TIME_FRAME_HEIGHT_AUTO = 150

tornitura_paused_time = 0  # Variabile per memorizzare il tempo trascorso prima della pausa
tornitura_elapsed_time = 0  # Variabile per memorizzare il tempo trascorso total
tornitura_elapsed_seconds = 0
tornitura_minutes = 0
tornitura_seconds = 0
time_tornitura_timer_current_button = None

# Funzione per avviare la tornitura
def start_tornitura():
    global tornitura_start_time, tornitura_paused_time, tornitura_elapsed_time, time_tornitura_timer_current_button
    time_tornitura_timer_current_button = 'start'
    tornitura_button_stop.configure(state= "enabled")
    tornitura_button_inizio.configure(state= "disabled")
    if tornitura_start_time is None:
        tornitura_start_time = time.time()
    else:
        # Se c'è un tempo di pausa memorizzato, aggiungilo al tempo trascorso
        tornitura_paused_time = time.time() - tornitura_paused_time  # Calcola il tempo di pausa
        tornitura_start_time += tornitura_paused_time  # Aggiungi il tempo di pausa al tempo iniziale
    update_elapsed_time_tornitura()  # Avvia l'aggiornamento del tempo trascorso

# Funzione per fermare la tornitura
def stop_tornitura():
    global tornitura_start_time, tornitura_paused_time, tornitura_elapsed_time, time_tornitura_timer_current_button
    time_tornitura_timer_current_button = 'stop'
    tornitura_button_stop.configure(state= "disabled")
    tornitura_button_inizio.configure(state= "enabled")
    if tornitura_start_time is not None:
        tornitura_paused_time = time.time()  # Memorizza il tempo trascorso prima della pausa
        tornitura_elapsed_time += tornitura_paused_time - tornitura_start_time  # Aggiorna il tempo totale trascorso
        #tornitura_start_time = None  # Resetta tornitura_start_time

# Funzione per resettare la tornitura
def reset_tornitura(type_req = None):
    global tornitura_start_time, tornitura_paused_time, tornitura_elapsed_time, time_tornitura_timer_current_button, tornitura_minutes, tornitura_seconds
    if type_req == None:
        if(not ask_question_choice("Sei sicuro di voler resettare il timer di tornitura?")):
            return
    time_tornitura_timer_current_button = 'reset'
    tornitura_button_stop.configure(state="disabled")
    tornitura_button_inizio.configure(state= "enabled")
    tornitura_start_time = None  # Resetta tornitura_start_time
    tornitura_paused_time = 0  # Resetta il tempo di pausa
    tornitura_elapsed_time = 0  # Resetta il tempo trascorso totale
    tornitura_minutes = 0
    tornitura_seconds = 0
    tornitura_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso

#GENERAZIONE FRAME
frame_tornitura_time = ctk.CTkFrame(
    master=frame_container_time,
    width=TORNITURA_TIME_FRAME_WIDTH,
    height=TORNITURA_TIME_FRAME_HEIGHT_MANUAL
)

#GENERAZIONE LABEL
tornitura_time_label = ctk.CTkLabel(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di tornitura (min)"
)
tornitura_time_label.place(x=_map_item_x(18, TORNITURA_TIME_FRAME_WIDTH), y=_map_item_y(6, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_tornitura_num = CTkSpinbox(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=_map_item_x(76, TORNITURA_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, TORNITURA_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20']
)
tempo_tornitura_num.place(x=_map_item_x(10, TORNITURA_TIME_FRAME_WIDTH), y=_map_item_y(43, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE CHECKBOX
tornitura_time_checkbox = ctk.CTkCheckBox(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_tornitura_time
tornitura_time_checkbox.place(relx=0.65, rely=0.1)

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
tornitura_button_inizio = ctk.CTkButton(
    master=frame_tornitura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: start_tornitura()
)

tornitura_button_stop = ctk.CTkButton(
    master=frame_tornitura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: stop_tornitura()
)

tornitura_button_reset = ctk.CTkButton(
    master=frame_tornitura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: reset_tornitura()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
tornitura_time_elapsed_label = ctk.CTkLabel(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'], 
    text="{:d}:{:02d}".format(tornitura_minutes, tornitura_seconds)
)
tornitura_time_elapsed_label.place(relx=0.1, rely=0.6)

tornitura_start_time = None

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_tornitura():
    global time_tornitura_timer_current_button, tornitura_elapsed_seconds, tornitura_seconds, tornitura_minutes, tornitura_start_time
    if tornitura_start_time is not None and time_tornitura_timer_current_button == 'start':
        if tempo_tornitura_num.get() != tornitura_minutes and not tornitura_time_checkbox.get():
            time_diff = int(tempo_tornitura_num.get()) - tornitura_minutes
            time_diff_seconds = time_diff * 60
            tornitura_start_time -= time_diff_seconds

        tornitura_elapsed_seconds = int(time.time() - tornitura_start_time)
        tornitura_minutes = tornitura_elapsed_seconds // 60
        tornitura_seconds = tornitura_elapsed_seconds % 60
        tornitura_time_elapsed_label.configure(text="{:d}:{:02d}".format(tornitura_minutes, tornitura_seconds))
        if(tornitura_minutes > tempo_tornitura_num.get() and tornitura_time_checkbox.get()):
            tempo_tornitura_num.configure(value= tornitura_minutes)
    frame_tornitura_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_tornitura)  # Richiama se stesso ogni secondo

# Logica per mostrare i pulsanti solo quando il checkbox è selezionato
def tornitura_toggle_buttons():
    RELY_TIMER_BUTTONS = 0.6
    global tornitura_start_time, tornitura_minutes, tornitura_seconds
    if tornitura_time_checkbox.get():
        tempo_tornitura_num.place_forget()
        #frame_tornitura_time.place(x=0, rely=0.5, anchor='w')
        tornitura_button_inizio.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
        tornitura_button_stop.place(relx=0.4, rely=RELY_TIMER_BUTTONS)
        tornitura_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
        tornitura_time_elapsed_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
        tornitura_time_elapsed_label.configure(text="{:d}:{:02d}".format(tornitura_minutes, tornitura_seconds))
        tornitura_time_label.configure(text="Tempo di tornitura")
        update_elapsed_time_tornitura()
    else:
        tornitura_button_inizio.place_forget()
        tornitura_button_stop.place_forget()
        tornitura_button_reset.place_forget()
        tornitura_time_elapsed_label.place_forget()
        tempo_tornitura_num.place(x=_map_item_x(10, TORNITURA_TIME_FRAME_WIDTH), y=_map_item_y(43, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))
        tornitura_time_label.configure(text="Tempo di tornitura(min)")
        tempo_tornitura_num.configure(value=tornitura_minutes)

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
tornitura_time_checkbox.configure(command=tornitura_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
tornitura_toggle_buttons()


#FRAME FRESATURA TIME
FRESATURA_TIME_FRAME_WIDTH = 210
FRESATURA_TIME_FRAME_HEIGHT_MANUAL = 100
FRESATURA_TIME_FRAME_HEIGHT_AUTO = 150

fresatura_paused_time = 0  # Variabile per memorizzare il tempo trascorso prima della pausa
fresatura_elapsed_time = 0  # Variabile per memorizzare il tempo trascorso total
fresatura_elapsed_seconds = 0
fresatura_minutes = 0
fresatura_seconds = 0
time_fresatura_timer_current_button = None

# Funzione per avviare la fresatura
def start_fresatura():
    global fresatura_start_time, fresatura_paused_time, fresatura_elapsed_time, time_fresatura_timer_current_button
    time_fresatura_timer_current_button = 'start'
    fresatura_button_stop.configure(state= "enabled")
    fresatura_button_inizio.configure(state= "disabled")
    if fresatura_start_time is None:
        fresatura_start_time = time.time()
    else:
        # Se c'è un tempo di pausa memorizzato, aggiungilo al tempo trascorso
        fresatura_paused_time = time.time() - fresatura_paused_time  # Calcola il tempo di pausa
        fresatura_start_time += fresatura_paused_time  # Aggiungi il tempo di pausa al tempo iniziale
    update_elapsed_time_fresatura()  # Avvia l'aggiornamento del tempo trascorso

# Funzione per fermare la fresatura
def stop_fresatura():
    global fresatura_start_time, fresatura_paused_time, fresatura_elapsed_time, time_fresatura_timer_current_button
    time_fresatura_timer_current_button = 'stop'
    fresatura_button_stop.configure(state= "disabled")
    fresatura_button_inizio.configure(state= "enabled")
    if fresatura_start_time is not None:
        fresatura_paused_time = time.time()  # Memorizza il tempo trascorso prima della pausa
        fresatura_elapsed_time += fresatura_paused_time - fresatura_start_time  # Aggiorna il tempo totale trascorso
        #fresatura_start_time = None  # Resetta fresatura_start_time

# Funzione per resettare la fresatura
def reset_fresatura(type_req = None):
    global fresatura_start_time, fresatura_paused_time, fresatura_elapsed_time, time_fresatura_timer_current_button, fresatura_minutes, fresatura_seconds
    if type_req == None:
        if(not ask_question_choice("Sei sicuro di voler resettare il timer di fresatura?")):
            return
    time_fresatura_timer_current_button = 'reset'
    fresatura_button_stop.configure(state="disabled")
    fresatura_button_inizio.configure(state= "enabled")
    fresatura_start_time = None  # Resetta fresatura_start_time
    fresatura_paused_time = 0  # Resetta il tempo di pausa
    fresatura_elapsed_time = 0  # Resetta il tempo trascorso totale
    fresatura_minutes = 0
    fresatura_seconds = 0
    fresatura_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso

#GENERAZIONE FRAME
frame_fresatura_time = ctk.CTkFrame(
    master=frame_container_time,
    width=FRESATURA_TIME_FRAME_WIDTH,
    height=FRESATURA_TIME_FRAME_HEIGHT_MANUAL
)

#GENERAZIONE LABEL
fresatura_time_label = ctk.CTkLabel(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di fresatura (min)"
)
fresatura_time_label.place(x=_map_item_x(18, FRESATURA_TIME_FRAME_WIDTH), y=_map_item_y(6, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_fresatura_num = CTkSpinbox(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=_map_item_x(76, FRESATURA_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, FRESATURA_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20']
)
tempo_fresatura_num.place(x=_map_item_x(10, FRESATURA_TIME_FRAME_WIDTH), y=_map_item_y(43, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE CHECKBOX
fresatura_time_checkbox = ctk.CTkCheckBox(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_fresatura_time
fresatura_time_checkbox.place(relx=0.65, rely=0.1)

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
fresatura_button_inizio = ctk.CTkButton(
    master=frame_fresatura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: start_fresatura()
)

fresatura_button_stop = ctk.CTkButton(
    master=frame_fresatura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: stop_fresatura()
)

fresatura_button_reset = ctk.CTkButton(
    master=frame_fresatura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: reset_fresatura()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
fresatura_time_elapsed_label = ctk.CTkLabel(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'], 
    text="{:d}:{:02d}".format(fresatura_minutes, fresatura_seconds)
)
fresatura_time_elapsed_label.place(relx=0.1, rely=0.6)

fresatura_start_time = None

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_fresatura():
    global time_fresatura_timer_current_button, fresatura_elapsed_seconds, fresatura_seconds, fresatura_minutes, fresatura_start_time
    if fresatura_start_time is not None and time_fresatura_timer_current_button == 'start':
        if tempo_fresatura_num.get() != fresatura_minutes and not fresatura_time_checkbox.get():
            time_diff = int(tempo_fresatura_num.get()) - fresatura_minutes
            time_diff_seconds = time_diff * 60
            fresatura_start_time -= time_diff_seconds

        fresatura_elapsed_seconds = int(time.time() - fresatura_start_time)
        fresatura_minutes = fresatura_elapsed_seconds // 60
        fresatura_seconds = fresatura_elapsed_seconds % 60
        fresatura_time_elapsed_label.configure(text="{:d}:{:02d}".format(fresatura_minutes, fresatura_seconds))
        if(fresatura_minutes > tempo_fresatura_num.get() and fresatura_time_checkbox.get()):
            tempo_fresatura_num.configure(value= fresatura_minutes)
    frame_fresatura_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_fresatura)  # Richiama se stesso ogni secondo

# Logica per mostrare i pulsanti solo quando il checkbox è selezionato
def fresatura_toggle_buttons():
    RELY_TIMER_BUTTONS = 0.6
    global fresatura_start_time, fresatura_minutes, fresatura_seconds
    if fresatura_time_checkbox.get():
        tempo_fresatura_num.place_forget()
        #frame_fresatura_time.place(x=0, rely=0.5, anchor='w')
        fresatura_button_inizio.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
        fresatura_button_stop.place(relx=0.4, rely=RELY_TIMER_BUTTONS)
        fresatura_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
        fresatura_time_elapsed_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
        fresatura_time_elapsed_label.configure(text="{:d}:{:02d}".format(fresatura_minutes, fresatura_seconds))
        fresatura_time_label.configure(text="Tempo di fresatura")
        update_elapsed_time_fresatura()  # Avvia l'aggiornamento del tempo trascorso
    else:
        fresatura_button_inizio.place_forget()
        fresatura_button_stop.place_forget()
        fresatura_button_reset.place_forget()
        fresatura_time_elapsed_label.place_forget()
        tempo_fresatura_num.place(x=_map_item_x(10, FRESATURA_TIME_FRAME_WIDTH), y=_map_item_y(43, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))
        fresatura_time_label.configure(text="Tempo di fresatura(min)")
        tempo_fresatura_num.configure(value=fresatura_minutes)

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
fresatura_time_checkbox.configure(command=fresatura_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
fresatura_toggle_buttons()


#FRAME ELETTRO TIME
ELETTRO_TIME_FRAME_WIDTH = 210
ELETTRO_TIME_FRAME_HEIGHT_MANUAL = 100
ELETTRO_TIME_FRAME_HEIGHT_AUTO = 150

elettro_paused_time = 0  # Variabile per memorizzare il tempo trascorso prima della pausa
elettro_elapsed_time = 0  # Variabile per memorizzare il tempo trascorso total
elettro_elapsed_seconds = 0
elettro_minutes = 0
elettro_seconds = 0
time_elettro_timer_current_button = None

# Funzione per avviare l'elettroerosione
def start_elettro():
    global elettro_start_time, elettro_paused_time, elettro_elapsed_time, time_elettro_timer_current_button
    time_elettro_timer_current_button = 'start'
    elettro_button_stop.configure(state= "enabled")
    elettro_button_inizio.configure(state= "disabled")
    if elettro_start_time is None:
        elettro_start_time = time.time()
    else:
        # Se c'è un tempo di pausa memorizzato, aggiungilo al tempo trascorso
        elettro_paused_time = time.time() - elettro_paused_time  # Calcola il tempo di pausa
        elettro_start_time += elettro_paused_time  # Aggiungi il tempo di pausa al tempo iniziale
    update_elapsed_time_elettro()  # Avvia l'aggiornamento del tempo trascorso

# Funzione per fermare l'elettroerosione
def stop_elettro():
    global elettro_start_time, elettro_paused_time, elettro_elapsed_time, time_elettro_timer_current_button
    time_elettro_timer_current_button = 'stop'
    elettro_button_stop.configure(state= "disabled")
    elettro_button_inizio.configure(state= "enabled")
    if elettro_start_time is not None:
        elettro_paused_time = time.time()  # Memorizza il tempo trascorso prima della pausa
        elettro_elapsed_time += elettro_paused_time - elettro_start_time  # Aggiorna il tempo totale trascorso
        #elettro_start_time = None  # Resetta elettro_start_time

# Funzione per resettare l'elettroerosione
def reset_elettro(type_req= None):
    global elettro_start_time, elettro_paused_time, elettro_elapsed_time, time_elettro_timer_current_button, elettro_seconds, elettro_minutes
    if type_req == None:
        if(not ask_question_choice("Sei sicuro di voler resettare il timer di elettroerosione?")):
            return
    time_elettro_timer_current_button = 'reset'
    elettro_button_stop.configure(state="disabled")
    elettro_button_inizio.configure(state= "enabled")
    elettro_start_time = None  # Resetta elettro_start_time
    elettro_paused_time = 0  # Resetta il tempo di pausa
    elettro_elapsed_time = 0  # Resetta il tempo trascorso totale
    elettro_minutes = 0
    elettro_seconds = 0
    elettro_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso

#GENERAZIONE FRAME
frame_elettro_time = ctk.CTkFrame(
    master=frame_container_time,
    width=ELETTRO_TIME_FRAME_WIDTH,
    height=ELETTRO_TIME_FRAME_HEIGHT_MANUAL
)

#GENERAZIONE LABEL
elettro_time_label = ctk.CTkLabel(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di elettroerosione (min)"
)
elettro_time_label.place(x=_map_item_x(18, ELETTRO_TIME_FRAME_WIDTH), y=_map_item_y(6, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_elettro_num = CTkSpinbox(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=_map_item_x(76, ELETTRO_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, ELETTRO_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20']
)
tempo_elettro_num.place(x=_map_item_x(10, ELETTRO_TIME_FRAME_WIDTH), y=_map_item_y(43, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE CHECKBOX
elettro_time_checkbox = ctk.CTkCheckBox(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_elettro_time
elettro_time_checkbox.place(relx=0.65, rely=0.1)

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
elettro_button_inizio = ctk.CTkButton(
    master=frame_elettro_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: start_elettro()
)

elettro_button_stop = ctk.CTkButton(
    master=frame_elettro_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: stop_elettro()
)

elettro_button_reset = ctk.CTkButton(
    master=frame_elettro_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: reset_elettro()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
elettro_time_elapsed_label = ctk.CTkLabel(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'], 
    text="{:d}:{:02d}".format(elettro_minutes, elettro_seconds)
)
elettro_time_elapsed_label.place(relx=0.1, rely=0.6)

elettro_start_time = None

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_elettro():
    global time_elettro_timer_current_button, elettro_elapsed_seconds, elettro_seconds, elettro_minutes, elettro_start_time
    if elettro_start_time is not None and time_elettro_timer_current_button == 'start':
        if tempo_elettro_num.get() != elettro_minutes and not elettro_time_checkbox.get():
            time_diff = int(tempo_elettro_num.get()) - elettro_minutes
            time_diff_seconds = time_diff * 60
            elettro_start_time -= time_diff_seconds

        elettro_elapsed_seconds = int(time.time() - elettro_start_time)
        elettro_minutes = elettro_elapsed_seconds // 60
        elettro_seconds = elettro_elapsed_seconds % 60
        elettro_time_elapsed_label.configure(text="{:d}:{:02d}".format(elettro_minutes, elettro_seconds))
        if(elettro_minutes > tempo_elettro_num.get() and elettro_time_checkbox.get()):
            tempo_elettro_num.configure(value= elettro_minutes)
    frame_elettro_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_elettro)  # Richiama se stesso ogni secondo

# Logica per mostrare i pulsanti solo quando il checkbox è selezionato
def elettro_toggle_buttons():
    RELY_TIMER_BUTTONS = 0.6
    global elettro_start_time, elettro_minutes, elettro_seconds
    if elettro_time_checkbox.get():
        tempo_elettro_num.place_forget()
        #frame_elettro_time.place(x=0, rely=0.5, anchor='w')
        elettro_button_inizio.place(relx=0.1, rely=RELY_TIMER_BUTTONS)
        elettro_button_stop.place(relx=0.4, rely=RELY_TIMER_BUTTONS)
        elettro_button_reset.place(relx=0.7, rely=RELY_TIMER_BUTTONS)
        elettro_time_elapsed_label.place(relx=ELAPSED_TIME_LABEL_X, rely=ELAPSED_TIME_LABEL_Y)
        elettro_time_elapsed_label.configure(text="{:d}:{:02d}".format(elettro_minutes, elettro_seconds))
        elettro_time_label.configure(text="Tempo di elettroerosione")
        update_elapsed_time_elettro()  # Avvia l'aggiornamento del tempo trascorso
    else:
        elettro_button_inizio.place_forget()
        elettro_button_stop.place_forget()
        elettro_button_reset.place_forget()
        elettro_time_elapsed_label.place_forget()
        tempo_elettro_num.place(x=_map_item_x(10, ELETTRO_TIME_FRAME_WIDTH), y=_map_item_y(43, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))
        elettro_time_label.configure(text="Tempo di elettroerosione(min)")
        tempo_elettro_num.configure(value=elettro_minutes)

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
elettro_time_checkbox.configure(command=elettro_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
elettro_toggle_buttons()


#PEZZI FRAME
N_PEZZI_FRAME_WIDTH = 210
N_PEZZI_FRAME_HEIGHT = 100
frame_n_pezzi = ctk.CTkFrame(
    master=home_page, 
    width=_map_frame_x(N_PEZZI_FRAME_WIDTH), 
    height=_map_frame_y(N_PEZZI_FRAME_HEIGHT)
    )

pezzi_select_num = CTkSpinbox(
    master=frame_n_pezzi, bg_color=[
        'gray86', 'gray17'], 
        button_width = 50,
        width=_map_item_x(76, N_PEZZI_FRAME_WIDTH), 
        height=_map_item_y(44, N_PEZZI_FRAME_HEIGHT), 
        value=0, 
        fg_color=['gray81', 'gray20'],
        )
pezzi_select_num.place(x=_map_item_x(11, N_PEZZI_FRAME_WIDTH), y=_map_item_y(44, N_PEZZI_FRAME_HEIGHT))

def open_pdf():
    selected_menu_tendina = menu_tendina_disegni.get()
    if(".pdf" in selected_menu_tendina):
        file_name = os.path.join(directory_path, str(menu_tendina_disegni.get()))
    elif(".pdf" not in selected_menu_tendina):
        file_name = os.path.join(directory_path, str(menu_tendina_disegni.get()) + ".pdf")
    corrected_file_path = file_name.replace('/', '\\')
    print(corrected_file_path)
    try:
        subprocess.Popen(['xdg-open', file_name])  # Linux
        print("Linux")
    except OSError:
        try:
            subprocess.Popen(['open', file_name])  # macOS
            print("MacOS")
        except OSError:
            try:
                subprocess.Popen(['start', '', corrected_file_path], shell=True)  # Windows
                print("Windows")
            except OSError:
                print("Impossibile aprire il file PDF con un programma esterno.")

#FRAME DRAW
N_DRAW_FRAME_WIDTH = 200
N_DRAW_FRAME_HEIGHT = 90

frame_n_draw = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(N_DRAW_FRAME_WIDTH), 
    height=_map_frame_y(N_DRAW_FRAME_HEIGHT)
    )

draw_mode_checkbox = ctk.CTkCheckBox(
    master=frame_n_draw, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
    )

# Carica la configurazione dal file .conf
checkbox_auto = load_config("draw_mode_checkbox")
print("checkbox_auto: " + str(checkbox_auto))

# Imposta lo stato di spunta del checkbox in base al valore caricato
if(checkbox_auto):
    draw_mode_checkbox.select()
elif(not checkbox_auto):
    draw_mode_checkbox.deselect()
else:
    print("Conf not found")

draw_mode_checkbox.place(relx = 0.65, rely=0.1)

draw_num_label = ctk.CTkLabel(
    master=frame_n_draw, 
    bg_color=['gray92', 'gray14'], 
    text="Numero disegno")
draw_num_label.place(relx = 0.09, rely=0.11)

draw_num_entry = ctk.CTkEntry(
    master=frame_n_draw, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

menu_tendina_disegni = ctk.CTkOptionMenu(
    master=frame_n_draw, 
    values=[], 
    bg_color=['gray86', 'gray17'],
    width= 140,# + 10,
    height= 28 + 10,
    dropdown_font = ctk.CTkFont(
        'Roboto',
        size=16),
    hover=False
    )

menu_tendina_disegni.configure(values=file_list)
menu_tendina_disegni.set("Sel. num. disegno")

draw_open_pdf_button = ctk.CTkButton(
    master=frame_n_draw, 
    width= 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Apri",
    command= lambda: open_pdf()
    )

if draw_mode_checkbox.get():
    menu_tendina_disegni.place(relx = 0.02, rely=0.4)
    draw_open_pdf_button.place(relx = 0.775, rely=0.4)
else:
    #draw_open_pdf_button.place_forget()
    draw_num_entry.place(relx = 0.09, rely=0.4)

#LAVORAZIONE FRAME
LAVORAZIONE_FRAME_WIDTH = 400
LAVORAZIONE_FRAME_HEIGHT = 40
frame_lavorazione = ctk.CTkFrame(master=home_page, 
                                           width=_map_frame_x(LAVORAZIONE_FRAME_WIDTH), 
                                           height=_map_frame_y(LAVORAZIONE_FRAME_HEIGHT)
                                           )
#frame_lavorazione.place(x=191, y=73)

tornitura_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="Tornitura")
tornitura_checkbox.place(x=_map_item_x(115, LAVORAZIONE_FRAME_WIDTH), y=_map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

fresatura_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="Fresatura")
fresatura_checkbox.place(x=_map_item_x(220, LAVORAZIONE_FRAME_WIDTH), y=_map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

elettro_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray92', 'gray14'], width=72, text="Elettro")
elettro_checkbox.place(x=_map_item_x(320, LAVORAZIONE_FRAME_WIDTH), y=_map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

taglio_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="Taglio")
taglio_checkbox.place(x=_map_item_x(13, LAVORAZIONE_FRAME_WIDTH), y=_map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

def show_popup():
    # Disable/Enable popup
    if switch.get()==1:
        #keyboard.disable = False
        numpad_login.disable = False
    else:
        #keyboard.disable = True
        numpad_login.disable = True

def create_database(username):
    global db_config
    try:
        # Connessione al database principale
        conn_main = psycopg2.connect(**db_config)
        cur_main = conn_main.cursor()

        # Verifica se il database esiste già
        cur_main.execute("SELECT datname FROM pg_catalog.pg_database WHERE datname = %s", (f"{username}_user",))
        if not cur_main.fetchone():
            # Il database non esiste, quindi lo creiamo
            conn_main.set_isolation_level(0)  # Imposta il livello di isolamento su autocommit
            new_db_name = f"{username}_user"
            cur_main.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db_name)))
            print(f"Database '{new_db_name}' creato con successo.")


        # Chiudiamo la connessione al database principale
        conn_main.close()

        return new_db_name
    except Exception as e:
        print(f"Errore durante la creazione del database per '{username}': {e}")
        return None

def perform_registration():

    username = user_singup_entry.get()
    password = passwd_singup_entry.get()
    confirm_password = passwd_repeat_singup_entry.get()
    print(username + ", " + password + ", " + confirm_password)

    if password != confirm_password:
        #show_error_message("Errore, le password non corrispondono.", 24, 110)
        CTkMessagebox(
            master= login_page,
            title="Errore di registrazione", 
            message="Le password non corrispondono!",
            icon="warning"
            )
        return False
    
    try:
        import psycopg2
        from psycopg2 import sql

        # Connessione al database PostgreSQL
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Verifica se il database esiste già
        #db_name = username
        new_db_name = create_database(username)
        print("new_db_name: " + new_db_name)
        # Connessione al database appena creato
        conn.close()
        conn = psycopg2.connect(**{**db_config, 'dbname': new_db_name})
        cur = conn.cursor()

        # Creazione della tabella per memorizzare la password
        cur.execute("""
            CREATE TABLE password (
                id SERIAL PRIMARY KEY,
                password_hash TEXT
            )
        """)

        # Inserimento della password nella tabella
        # Qui puoi usare un metodo di hash per crittografare la password prima di memorizzarla
        # Ad esempio, usando bcrypt o hashlib
        # Ecco un esempio di utilizzo di hashlib per ottenere un hash della password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("INSERT INTO password (password_hash) VALUES (%s)", (password_hash,))

        # Applica le modifiche
        conn.commit()
        switch_page(home_page)
        return True

    except psycopg2.Error as e:
        conn.rollback()
        #messagebox.showerror("Errore di registrazione", f"Errore durante l'inserimento dell'utente nel database: {e}")
        CTkMessagebox(
            master= singup_page,
            title="Errore di registrazione", 
            message=f"Errore durante l'inserimento dell'utente nel database: {e}",
            icon="warning"
            )
        return False

    finally:
        try:
            if conn is not None:
                conn.close()
        except:
            CTkMessagebox(
                master= singup_page,
                title="Errore di registrazione", 
                message="Errore di accesso al database",
                icon="warning"
                )

def check_db_connection(db_config):
    global DB_STATE
    try:
        # Prova a connetterti al database PostgreSQL
        conn = psycopg2.connect(**db_config)
        conn.close()  # Chiudi immediatamente la connessione, non serve tenerla aperta
        DB_STATE = "Connesso"
        update_db_user_state()
        return True  # Restituisci True se la connessione è riuscita
    except psycopg2.Error as e:
        print(f"Errore durante la connessione al database: {e}")
        update_db_user_state()
        DB_STATE = 'Errore di connessione' 
        return False  # Restituisci False se c'è stato un errore di connessione


# Chiamata alla funzione per verificare la connessione al database all'avvio
check_db_connection(db_config)

selected_checkboxes = []  # Lista per tenere traccia dei checkbox selezionati

def update_selected_checkbox(checkbox):
    global selected_checkboxes

    if checkbox in selected_checkboxes:
        selected_checkboxes.remove(checkbox)
    else:
        selected_checkboxes.append(checkbox)

def update_selected_text():
    global selected_checkboxes
    global selected_checkbox_text

    selected_checkbox_text = ', '.join([checkbox.cget('text') for checkbox in selected_checkboxes])

def ask_question_db_conf(host, port, user, passwd):
    # Formattazione dei dati come una tabella
    tabella = (
        f"{'HOST:':<20}{host}\n"
        f"{'PORT:':<20}{port}\n"
        f"{'USER:':<20}{user}\n"
        f"{'PASSWORD:':<20}{passwd}"
    )

    # Creazione del messaggio di messagebox
    msg = CTkMessagebox(
        master= singup_page,
        title="Conferma impostazioni Postgres", 
        message=f"Impostazioni:\n\n{tabella}\nIl test della connessione ha dato esito positivo\nConferma per salvare?",
        width=500,
        icon="question", 
        option_1="Conferma", 
        option_2="Modifica" 
    )

    # Ottieni la risposta dal messagebox
    response = msg.get()
    
    if response=="Conferma":
        return True
    elif response=="Modifica":
        return False

def save_db_conf(host, port, user, passwd, dialog):

    db_config = {
        'host': host,
        'port': port,
        'user': user,
        'password': passwd
    }

    if check_db_connection(db_config):
        if(ask_question_db_conf(host, port, user, passwd)):
            save_config('pg_host', host)
            save_config('pg_port', port)
            save_config('pg_user', user)
            save_config('pg_passwd', passwd)
            dialog.destroy()

def show_update_config_dialog():
    def choose_directory():
        directory_path = filedialog.askdirectory()
        if directory_path:
            directory_update_entry.delete(0, "end")  # Pulisce l'entry widget
            directory_update_entry.insert(0, directory_path)  # Inserisce il percorso selezionato nell'entry widget

    def save_directory():
        chosen_directory = directory_update_entry.get()
        if chosen_directory:
            save_config("update_directory", chosen_directory)
            dialog.destroy()

    dialog = ctk.CTkToplevel()
    dialog.title("Configurazione Directory Aggiornamenti")

    directory_update_label = ctk.CTkLabel(dialog, text="Directory:")
    directory_update_label.grid(row=0, column=0, padx=5, pady=5)

    directory_update_entry = ctk.CTkEntry(dialog, width=250)
    directory_update_entry.grid(row=0, column=1, padx=5, pady=5)

    choose_button = ctk.CTkButton(dialog, text="Scegli Directory", command=choose_directory)
    choose_button.grid(row=0, column=2, padx=5, pady=5)

    save_button = ctk.CTkButton(dialog, text="Salva", command=save_directory)
    save_button.grid(row=2, column=1, padx=5, pady=5)

    dialog.lift()

    dialog.focus_set()  
    dialog.grab_set()   
    dialog.wait_window()

def apply_update_dialog(exe_directory):
    # Verifica che la directory esista
    if os.path.isdir(exe_directory):
        # Trova il percorso del file .exe nella directory
        exe_file = None
        for file_name in os.listdir(exe_directory):
            if file_name.endswith('.exe'):
                exe_file = os.path.join(exe_directory, file_name)
                break
        
        # Se trova un file .exe, copialo nella stessa directory dell'eseguibile Python
        if exe_file:
            python_executable_dir = os.path.dirname(sys.executable)
            try:
                shutil.copy2(exe_file, python_executable_dir)
                print("File .exe copiato con successo.")
            except shutil.SameFileError:
                print("Il file .exe è già presente nella directory dell'eseguibile.")
            except PermissionError:
                print("Non hai i permessi per copiare il file .exe.")
            except Exception as e:
                print(f"Si è verificato un errore durante la copia del file .exe: {e}")
        else:
            print("Nessun file .exe trovato nella directory indicata.")
    else:
        print("La directory indicata non esiste.")

def show_draw_config_dialog():
    def choose_directory():
        directory_path = filedialog.askdirectory()
        if directory_path:
            directory_entry.delete(0, "end")  # Pulisce l'entry widget
            directory_entry.insert(0, directory_path)  # Inserisce il percorso selezionato nell'entry widget

    def save_directory():
        global file_list
        chosen_directory = directory_entry.get()
        if chosen_directory:
            save_config("draw_directory", chosen_directory)
            file_list = get_pdf_files_in_directory(chosen_directory)
            menu_tendina_disegni.configure(values=file_list)
            dialog.destroy()  # Chiude la finestra di dialogo dopo aver salvato il percorso

    def toggle_auto_scan(checkbox):
        if checkbox:
            save_config("draw_auto_scan", True)
        else:
            save_config("draw_auto_scan", False)

    dialog = ctk.CTkToplevel()
    dialog.title("Configurazione Directory Disegni")

    directory_label = ctk.CTkLabel(dialog, text="Directory:")
    directory_label.grid(row=0, column=0, padx=5, pady=5)

    directory_entry = ctk.CTkEntry(dialog, width=250)
    directory_entry.insert(0, load_config("draw_directory") or '')
    directory_entry.grid(row=0, column=1, padx=5, pady=5)

    choose_button = ctk.CTkButton(dialog, text="Scegli Directory", command=choose_directory)
    choose_button.grid(row=0, column=2, padx=5, pady=5)

    save_button = ctk.CTkButton(dialog, text="Salva", command=save_directory)
    save_button.grid(row=2, column=1, padx=5, pady=5)

    dialog.lift()  # Solleva la finestra di dialogo in primo piano

    dialog.focus_set()  # Imposta il focus sulla finestra di dialogo
    dialog.grab_set()   # Blocca l'input alle altre finestre
    dialog.wait_window()  # Attendi che la finestra di dialogo venga chiusa

def show_db_config_dialog():
    dialog = ctk.CTkToplevel()
    dialog.title("Configurazione Server PostgreSQL")
    dialog.geometry("400x300")
    dialog.resizable(False, False)

    host_label = ctk.CTkLabel(dialog, text="Host:")
    host_label.pack()
    host_entry = ctk.CTkEntry(dialog)
    host_entry.pack()

    port_label = ctk.CTkLabel(dialog, text="Porta:")
    port_label.pack()
    port_entry = ctk.CTkEntry(dialog)
    port_entry.pack()

    user_label = ctk.CTkLabel(dialog, text="Utente:")
    user_label.pack()
    user_entry = ctk.CTkEntry(dialog)
    user_entry.pack()

    password_label = ctk.CTkLabel(dialog, text="Password:")
    password_label.pack()
    password_entry = ctk.CTkEntry(dialog, show="*")
    password_entry.pack()

    # Carica le impostazioni dal file di configurazione (se esiste)
    host_entry.insert(0, load_config('pg_host') or '')
    port_entry.insert(0, load_config('pg_port') or '')
    user_entry.insert(0, load_config('pg_user') or '')
    password_entry.insert(0, load_config('pg_passwd') or '')

    save_button = ctk.CTkButton(
        dialog, 
        text="Test impostazioni", 
        command=lambda: save_db_conf(host_entry.get(), port_entry.get(), user_entry.get(), password_entry.get(), dialog)
        )
    save_button.pack()

    dialog.focus_set()  # Imposta il focus sulla finestra di dialogo
    dialog.grab_set()   # Blocca l'input alle altre finestre
    dialog.wait_window()  # Attendi che la finestra di dialogo venga chiusa



def checkbox_clicked(checkbox):
    update_selected_checkbox(checkbox)
    update_selected_text()
    #print("selected_checkbox_text: " + str(type(selected_checkbox_text)))  # Stampa il testo dei checkbox selezionati

# Collegamento della funzione di gestione dei click ai comandi di selezione/deselezione dei checkbox
tornitura_checkbox.configure(command=lambda: checkbox_clicked(tornitura_checkbox))
fresatura_checkbox.configure(command=lambda: checkbox_clicked(fresatura_checkbox))
elettro_checkbox.configure(command=lambda: checkbox_clicked(elettro_checkbox))
taglio_checkbox.configure(command=lambda: checkbox_clicked(taglio_checkbox))

#SING-UP FRAME
SINGUP_FRAME_WIDTH = 190 + 15
SINGUP_FRAME_HEIGHT = 263 + 40

# Creazione del frame di registrazione
frame_singup = ctk.CTkFrame(
    master=singup_page, 
    width=_map_frame_x(SINGUP_FRAME_WIDTH), 
    height=_map_frame_y(SINGUP_FRAME_HEIGHT) 
)

# Label per il titolo "Registrazione"
registration_title_label = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Registrazione",
    font=("Helvetica", 16, "bold")  # Opzionale: cambia il font per enfatizzare il titolo
)
registration_title_label.place(x=_map_item_x(50, SINGUP_FRAME_WIDTH), y=_map_item_y(2, SINGUP_FRAME_HEIGHT))

# Label e Entry per l'username
user_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Username"
)
user_label_singup.place(x=_map_item_x(60, SINGUP_FRAME_WIDTH), y=_map_item_y(30, SINGUP_FRAME_HEIGHT))

user_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
print("user_singup_entry: " + str(user_singup_entry))
user_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(50, SINGUP_FRAME_HEIGHT))

# Label e Entry per la password
passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Password"
)
passwd_label_singup.place(x=_map_item_x(60, SINGUP_FRAME_WIDTH), y=_map_item_y(90, SINGUP_FRAME_HEIGHT))

passwd_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
passwd_singup_entry.configure(show='*')
passwd_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(110, SINGUP_FRAME_HEIGHT))

# Label e Entry per la ripetizione della password
repeat_passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Ripeti password"
)
repeat_passwd_label_singup.place(x=_map_item_x(45, SINGUP_FRAME_WIDTH), y=_map_item_y(150, SINGUP_FRAME_HEIGHT))

passwd_repeat_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
passwd_repeat_singup_entry.configure(show='*')
passwd_repeat_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(170, SINGUP_FRAME_HEIGHT))

# Pulsante di registrazione
singup_button = ctk.CTkButton(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Registrati",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: perform_registration()
)
singup_button.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(210, SINGUP_FRAME_HEIGHT))

# Pulsante per tornare indietro
back_button_singup = ctk.CTkButton(
    master=frame_singup,
    bg_color=['gray92','gray14'],
    text="Indietro",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: switch_page(home_page)
    )
back_button_singup.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(250, SINGUP_FRAME_HEIGHT))

def change_appearance_mode_event(new_appearance_mode: str):
    save_config("theme", new_appearance_mode)
    ctk.set_appearance_mode(new_appearance_mode)

def change_color_event(new_color: str):
    save_config("color", new_color)
    ctk.set_default_color_theme(new_color)



#FRAME SETTINGS
SETTINGS_FRAME_WIDTH = 190 + 10
SETTINGS_FRAME_HEIGHT = 263 + 60

# Creazione del frame SETTINGS come frame scrollabile
frame_settings = ctk.CTkScrollableFrame(
    master=singup_page, 
    width=_map_frame_x(SETTINGS_FRAME_WIDTH), 
    height=_map_frame_y(SETTINGS_FRAME_HEIGHT),
    orientation='vertical'                                  
)
frame_settings.grid_rowconfigure(0)

# Label per il titolo "Impostazioni"
settings_title_label = ctk.CTkLabel(
    master=frame_settings, 
    bg_color=['gray92', 'gray14'], 
    text="Impostazioni",
    font=("Helvetica", 16, "bold")  # Opzionale: cambia il font per enfatizzare il titolo
)
settings_title_label.grid(row=0, column=0)

# Creazione del frame per la num key scale Scale
frame_num_board = ctk.CTkFrame(master=frame_settings)
frame_num_board.grid(row=5, column=0, padx=10, pady=10)  

# Label per la KEYSIZE Scale
num_board_scale_label_singup = ctk.CTkLabel(
    master=frame_num_board, 
    bg_color=['gray92', 'gray14'], 
    text="NUM KEY size"
)
num_board_scale_label_singup.grid(row=0, column=0)

# CTkSpinbox per la selezione della GUI Scale
num_board_select_num = CTkSpinbox(
    master=frame_num_board, 
    bg_color=['gray86', 'gray17'],
    width=_map_item_x(76, SETTINGS_FRAME_WIDTH),
    height=_map_item_y(44, SETTINGS_FRAME_HEIGHT),
    value=KEYWIDTH, 
    fg_color=['gray81', 'gray20']
)
num_board_select_num.grid(row=8, column=0)  

# Colleghi la funzione di aggiornamento alla variazione del valore del CTkSpinbox
num_board_select_num.configure(command=lambda: update_num_board(num_board_select_num.get()))

# Creazione del frame per l'aspetto
frame_appearance = ctk.CTkFrame(master=frame_settings)
frame_appearance.grid(row=7, column=0, padx=10, pady=10)

# Label per l'aspetto
appearance_mode_label = ctk.CTkLabel(frame_appearance, text="Tema:", anchor="w")
appearance_mode_label.grid(row=0, column=0)

# OptionMenu per selezionare l'aspetto
appearance_mode_optionemenu = ctk.CTkOptionMenu(
    frame_appearance, 
    values=["Light", "Dark", "System"],
    command=change_appearance_mode_event
)
default_theme_text = "Seleziona un tema"
appearance_mode_optionemenu.set(default_theme_text)
appearance_mode_optionemenu.grid(row=1, column=0)

# Label per il colore
color_label = ctk.CTkLabel(frame_appearance, text="Colore:", anchor="w")
color_label.grid(row=6, column=0)

# OptionMenu per selezionare il colore
color_optionemenu = ctk.CTkOptionMenu(
    frame_appearance, 
    values=["green", "blue"],
    command= change_color_event
)
default_color_text = "Seleziona un colore"
color_optionemenu.set(default_color_text)
color_optionemenu.grid(row=5, column=0)

# Pulsante per le impostazioni del database
db_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impostazioni DB",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_db_config_dialog()
)
db_settings.grid(row=1, column=0)

# Pulsante per le impostazioni dei disegni
draw_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impostazioni Disegni",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_draw_config_dialog()
)
draw_settings.grid(row=2, column=0)

run_update = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Applica aggiornamento",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_draw_config_dialog()
)
run_update.grid(row=3, column=0)

# Pulsante per le impostazioni dei disegni
update_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impost. Update",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_update_config_dialog()
)
update_settings.grid(row=4, column=0)

#FRAME NOTE
N_NOTE_FRAME_WIDTH = 210
N_NOTE_FRAME_HEIGHT = 100

frame_note = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(N_NOTE_FRAME_WIDTH), 
    height=_map_frame_y(N_NOTE_FRAME_HEIGHT)
    )

note_mode_checkbox = ctk.CTkCheckBox(
    master=frame_note, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
    )

note_num_label = ctk.CTkLabel(
    master=frame_note, 
    bg_color=['gray92', 'gray14'], 
    text="Aggiungi note")
note_num_label.place(relx = 0.09, rely=0.11)

note_num_entry = ctk.CTkEntry(
    master=frame_note, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

note_num_entry.place(relx = 0.09, rely=0.4)

def get_user_databases():
    try:
        # Connessione al database principale
        conn_main = psycopg2.connect(**db_config)
        cur_main = conn_main.cursor()

        # Ottieni i nomi dei database presenti sul server PostgreSQL
        cur_main.execute("SELECT datname FROM pg_catalog.pg_database")
        databases = cur_main.fetchall()

        # Filtra solo i nomi dei database che terminano con "_user"
        user_databases = [db[0].rstrip("_user") for db in databases if db[0].endswith("_user")]
        print(user_databases)

        # Chiudiamo la connessione al database principale
        conn_main.close()

        return user_databases

    except Exception as e:
        print(f"Errore durante il recupero dei database degli utenti: {e}")
        return ["Errore1", "Errore2", "Errore3"]

def perform_login():#username, password):
    global LOGGED_USER
    global LOGGED_USER_DB
    global LOAD_TEMP

    users_list = get_user_databases()

    username = menu_tendina_utenti.get()  # Ottieni il valore immesso nella casella di testo dell'username
    password = passwd_login_entry.get()  # Ottieni il valore immesso nella casella di testo della password
    
    try:
        # Verifica se il nome utente selezionato è presente nel menu a tendina
        if username not in users_list:
            CTkMessagebox(
                master= login_page,
                title="Errore di login", 
                message="Utente non valido. Riprova!",
                icon="warning"
                )
            return
        
        # Aggiungiamo "_user" al nome del database
        db_name = f"{username}_user"
        
        # Connessione al database corrispondente all'utente selezionato
        conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
        cur = conn.cursor()

        # Esempio di verifica della password nel database degli utenti
        # In questo esempio, assumiamo che ci sia una tabella 'password' nel database dell'utente
        # e che contenga le password crittografate degli utenti
        cur.execute("SELECT password_hash FROM password")
        password_hash = cur.fetchone()[0]

        # Verifica se la password inserita corrisponde alla password memorizzata nel database
        # In questo esempio, stiamo confrontando l'hash della password memorizzata con l'hash della password inserita
        import hashlib
        input_password_hash = hashlib.sha256(password.encode()).hexdigest()
        if input_password_hash == password_hash:
            CTkMessagebox(
                master= home_page,
                title="Login", 
                message="Login effettuato con successo!",
                icon="info"
                )
            LOGGED_USER = username
            LOGGED_USER_DB = db_name
            update_db_user_state()
            switch_page(home_page)
            carica_temp()
            LOAD_TEMP = False
            print("LOAD_TEMP: " + str(LOAD_TEMP))
        else:
            CTkMessagebox(
                master= login_page,
                title="Errore di login", 
                message="Credenziali non valide. Riprova!",
                icon="info"
                )

    except psycopg2.Error as e:
        CTkMessagebox(
            master= login_page,
            title="Errore di login", 
            message=f"Errore durante la connessione al database: {e}",
            icon="info"
            )

    finally:
        if conn is not None:
            conn.close()

def accedi():
    username = menu_tendina_utenti.get()  # Ottieni il valore immesso nella casella di testo dell'username
    password = passwd_login_entry.get()  # Ottieni il valore immesso nella casella di testo della password
    # Fai qualcosa con i dati ottenuti, ad esempio, controlla le credenziali, accedi, ecc.
    defaul_user = "Seleziona un utente"
    print("Username:", username)
    print("Password:", password)
    if(username == defaul_user or password == ""):
        error_type = ''
        error_user = "devi selezionare l'username"
        error_pass = "devi inserire la password"
        error_user_pass = error_user + " e " + error_pass + "!"
        if(username == defaul_user and password != ""):
            error_type = error_user
        if(password == "" and username != defaul_user):
            error_type = error_pass
        if(password == "" and username == defaul_user):
            error_type = error_user_pass
        CTkMessagebox(
            master= login_page,
            title="Errore",
            message="Errore " + error_type,
            icon="warning"
            )
        return
    
    perform_login()

def order_to_db(TABLE_NAME):
    global LOGGED_USER 
    global LOGGED_USER_DB
    global selected_checkbox_text
    global selected_start_datetime

    if draw_mode_checkbox.get():
        numero_disegno = str(menu_tendina_disegni.get())
    else:
        numero_disegno = str(draw_num_entry.get())
    
    draw_exists = check_draw_exist_connection(db_config, numero_disegno)

    tipo_lavorazione = ''
    orario_fine = time.strftime('%Y-%m-%d %H:%M:%S')
    #orario_fine_dt = datetime.strptime(orario_fine, '%Y-%m-%d %H:%M:%S')
    tempo_setup = int(tempo_setup_num.get())
    tempo_taglio = int(tempo_taglio_num.get())
    tempo_tornitura = int(tempo_tornitura_num.get())
    tempo_fresatura = int(tempo_fresatura_num.get())
    tempo_elettroerosione = int(tempo_elettro_num.get())
    tempo_ciclo_totale = tempo_taglio + tempo_tornitura + tempo_fresatura + tempo_elettroerosione
    numero_pezzi = int(pezzi_select_num.get())
    orario_inizio = selected_start_datetime
    note_lavorazione = note_num_entry.get()
    if draw_mode_checkbox.get():
        numero_disegno = str(menu_tendina_disegni.get())
    else:
        numero_disegno = str(draw_num_entry.get())

    checkbox_data = selected_checkbox_text

    errore_riempimento = False

    if checkbox_data != "":
        tipo_lavorazione = checkbox_data#["text"]
        print("Checkbox selezionato:", tipo_lavorazione)
    else:
        print("Nessun checkbox selezionato.")
        # or tempo_taglio == 0 or tempo_tornitura == 0 or tempo_fresatura == 0 or tempo_elettroerosione == 0 
    
    print("selected_start_datetime: " + str(selected_start_datetime))

    # Verifica se tutti i campi sono stati compilati e se il numero di pezzi è diverso da zero
    if not all([orario_inizio, orario_fine, tipo_lavorazione, tempo_setup]) or numero_pezzi == 0 or numero_disegno == '' or selected_start_datetime == None:
        errore_riempimento = True
    
    if 'Taglio' in selected_checkbox_text and tempo_taglio == 0:
        errore_riempimento = True
        
    if 'Tornitura' in selected_checkbox_text and tempo_tornitura == 0:
        errore_riempimento = True

    if 'Fresatura' in selected_checkbox_text and tempo_fresatura == 0:
        errore_riempimento = True

    if 'Elettroerosione' in selected_checkbox_text and tempo_elettroerosione == 0:
        errore_riempimento = True

    if(errore_riempimento):
        CTkMessagebox(title="Errore", 
                  message="Riempi tutti i campi prima di continuare!",
                  icon="warning"
                  )
        return

    tempo_ciclo_totale = tempo_taglio + tempo_tornitura + tempo_fresatura + tempo_elettroerosione + tempo_setup

    #orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, tempo_ciclo, numero_pezzi
    user_choose = ask_question_confirm_order(orario_fine, tempo_setup, tempo_taglio, tempo_tornitura, 
                               tempo_fresatura, tempo_elettroerosione, orario_inizio, 
                               numero_pezzi, numero_disegno, note_lavorazione)
    if(not user_choose):
        CTkMessagebox(title="Errore", 
                  message="Devi accedere per confermare l'ordine!",
                  icon="warning"
                  )
        return
    
    conn = None

    try:
        if(LOGGED_USER != '' and LOGGED_USER_DB != ''):
            db_name = LOGGED_USER_DB

            conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
            cur = conn.cursor()

            print("TABLE_NAME: " + str(TABLE_NAME))

            query = """
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    orario_inizio TIMESTAMP,
                    orario_fine TIMESTAMP,
                    numero_disegno TEXT,
                    tempo_taglio INTEGER,
                    tempo_tornitura INTEGER,
                    tempo_fresatura INTEGER,
                    tempo_elettroerosione INTEGER,
                    tempo_ciclo_totale INTEGER,
                    tempo_setup INTEGER,
                    numero_pezzi INTEGER,
                    note_lavorazione TEXT
                )
            """.format(TABLE_NAME)

            cur.execute(query)
            
            query = """
                INSERT INTO {} (
                    orario_inizio, 
                    orario_fine, 
                    numero_disegno, 
                    tempo_taglio, 
                    tempo_tornitura, 
                    tempo_fresatura, 
                    tempo_elettroerosione, 
                    tempo_setup, 
                    numero_pezzi, 
                    note_lavorazione)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """.format(TABLE_NAME)

            cur.execute(query, (orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, numero_pezzi, note_lavorazione))
            conn.commit()
            CTkMessagebox(title="Chiusura ordine", 
                  message="Ordine chiuso con successo!",
                  icon="info"
                  )
                  
        else:
            CTkMessagebox(title="Errore", 
                  message=f"Devi effettuare il login per poter concludere l'ordine!",
                  icon="info"
                  )
            return

    except psycopg2.Error as e:
        conn.rollback()
        CTkMessagebox(title="Errore", 
                  message=f"Errore durante la chiusura dell'ordine: {e}",
                  icon="info"
                  )

    finally:
        if conn is not None:
            conn.close()

def riprendi_ordine():
    print('riprendi ordine')

def azzera_ordine():
    global selected_start_datetime
    ask_question_choice("Sei sicuro di voler azzerare l'ordine?")
    tempo_setup_num.configure(value= 0)
    pezzi_select_num.configure(value= 0)
    tempo_taglio_num.configure(value= 0)
    tempo_fresatura_num.configure(value= 0)
    tempo_tornitura_num.configure(value= 0)
    tempo_elettro_num.configure(value= 0)
    menu_tendina_disegni.set("Sel. num. disegno")
    draw_num_entry.delete('0', 'end')
    start_time_time_elapsed_label.configure(text= 'Da impostare')
    note_num_entry.delete('0', 'end')
    selected_start_datetime = None
    reset_elettro('force')
    reset_fresatura('force')
    reset_setup('force')
    reset_tornitura('force')
    reset_taglio('force')
    

def get_last_orders(num_ordini):
    global LOGGED_USER_DB
    
    try:
        # Connessione al database
        db_name = LOGGED_USER_DB

        conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
        cur = conn.cursor()

        # Query per ottenere gli ultimi ordini
        query = f"""
            SELECT * FROM ordini
            ORDER BY id DESC
            LIMIT %s
        """
        cur.execute(query, (num_ordini,))
        ultimi_ordini = cur.fetchall()

        # Chiudi la connessione al database
        cur.close()
        conn.close()

        return ultimi_ordini

    except psycopg2.Error as e:
        print("Errore durante l'interrogazione del database:", e)
        return None

def modifica_ordine():
    global recent_orders, selected_order, TABLE_ORDERS_ROW
    ORDER_MOD_BUTTON_WIDTH = 100

    def forget_selected_order_frame():
            global selected_order, selected_column, selected_row
            selected_order = None
            #selected_row = None
            #selected_column = None
            
            table_selected_order.destroy()
            button_elimina_ordine_selezionato.grid_forget()
            button_modifica_ordine_selezionato.grid_forget()
            frame_gestione_selezione_ordine_effettuato.grid_forget()
            frame_buttons_selezione_ordine_effettuato.grid_forget()

    def back_to_home():

        frame_gestione_modifica_ordine_selezionato.place_forget()

        button_modifica_ordine_selezionato.grid_forget()
        button_elimina_ordine_selezionato.grid_forget()
        frame_gestione_selezione_ordine_effettuato.place_forget()

        button_conferma_modifica.grid_forget()
        button_indietro_modifica.grid_forget()
        frame_gestione_lista_ordini_effettuati.place_forget()
        table_orders_list.destroy()
        switch_page(home_page)

    def print_selected(selected):
        print("selected: " + str(selected))

    def gestione_selezione():
        
        def draw_selected_order():
            global selected_order
            '''
            label_seleted_table = ctk.CTkLabel(
                master=frame_gestione_selezione_ordine_effettuato, 
                bg_color=['gray86', 'gray17'], 
                text="Seleziona l'elemento da modificare"
            )
            label_seleted_table.grid(row=0, padx=5, pady=10)
            '''
            intestazioni = ["ID", "Orario inizio", "Orario fine", "Numero disegno", "Tempo taglio", "Tempo tornitura", 
                            "Tempo fresatura", "Tempo elettroerosione", "Tempo ciclo", "Tempo setup", "Numero pezzi", "Note lavorazione"]
            
            for col, intestazione in enumerate(intestazioni):
                table_selected_order.insert(0, col, intestazione, bg_color="lightgrey")

            # Popolamento della tabella con l'ordine selezionato
            ordine = selected_order
            for col, valore in enumerate(ordine, start=0):
                if isinstance(valore, datetime):
                    valore = valore.strftime("%Y-%m-%d %H:%M:%S")
                table_selected_order.insert(1, col, valore)

            table_selected_order.grid(row=1, padx=5, pady=10)

        draw_selected_order()
        if frame_gestione_selezione_ordine_effettuato.winfo_exists():
            
            button_modifica_ordine_selezionato.grid_forget()
            frame_gestione_selezione_ordine_effettuato.grid_forget()

        button_elimina_ordine_selezionato.grid( row=0, column=1, padx=10, pady=10)
        frame_buttons_selezione_ordine_effettuato.grid(row=2, padx=10, pady=10)

        frame_gestione_selezione_ordine_effettuato.place(relx=0.5, rely=0.8, anchor='s')

    def show_row_select(cell):
        global selected_row, prev_selected_row, selected_column, prev_selected_column, selected_order

        if cell["row"] == 0:
            return  # Non modificare l'intestazione

        if selected_row is not None:
            # Deseleziona la riga precedentemente selezionata
            table_orders_list.deselect_row(selected_row)

        if selected_column is not None:
            # Deseleziona la colonna precedentemente selezionata
            table_selected_order.deselect_column(selected_column)
            selected_column = None

        # Seleziona la nuova riga
        selected = table_orders_list.get()[cell["row"]]
        selected_order = selected
        selected_row = cell["row"]
        table_orders_list.edit_row(selected_row, fg_color=table_orders_list.hover_color)

        gestione_selezione()

        # Esegui altre azioni, se necessario, sulla riga selezionata
        print_selected(selected)

    def show_column_select(cell):
        global selected_column, column_name, column_value

        if cell["column"] == 0:
            return  # Non modificare l'intestazione

        if selected_column is not None:
            # Deseleziona la colonna precedentemente selezionata
            table_selected_order.deselect_column(selected_column)

        # Seleziona la nuova colonna
        selected_column = cell["column"]
        column_name = table_selected_order.get()[0][selected_column]
        column_value = table_selected_order.get()[1][selected_column]
        table_selected_order.edit_column(selected_column, fg_color=table_selected_order.hover_color)

        button_modifica_ordine_selezionato.grid(row=0, column=0, padx=10, pady=10)

        # Esegui altre azioni, se necessario, sulla colonna selezionata
        print(f'colonna: {column_name}, valore: {column_value}')

    def update_db_value(id):
        global selected_column, column_value, db_index_names
        db_column_name = db_index_names[selected_column]
        try:
            db_name = LOGGED_USER_DB

            conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
            cur = conn.cursor()

            # Genera la query di aggiornamento dinamicamente
            query = f"""
                UPDATE {'ordini'} 
                SET {db_column_name} = %s
                WHERE id = %s
            """

            # Eseguire la query di aggiornamento con il nuovo valore e l'ID del record da aggiornare
            cur.execute(query, (column_value, id))
            conn.commit()

            CTkMessagebox(
                title="Aggiornamento ordine",
                message="Ordine aggiornato con successo!",
                icon="info"
            )
            
            #forget_selected_order_frame()


        except psycopg2.Error as e:
            print(e)
            conn.rollback()
            CTkMessagebox(
                title="Errore",
                message=f"Errore durante l'aggiornamento dell'ordine: {e}",
                icon="info"
            )

    def int_modify_dialog(column_name):
        global DATA_ORDER_CHANGE, column_value
        
        def save_int():
            global column_value, DATA_ORDER_CHANGE
            column_value = int_spinbox.get()
            print(f"Modifica '{column_name}': {column_value}")
            DATA_ORDER_CHANGE = True
            dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

        dialog = ctk.CTkToplevel()
        dialog.title(f"Modifica {column_name}")

        ctk.CTkLabel(master=dialog, text=f"{column_name}:").grid(row=0, column=0, padx=5, pady=5)
        int_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, height=44)  # Personalizza i valori di 'from_' e 'to' secondo le tue esigenze
        int_spinbox.grid(row=0, column=1, padx=5, pady=5)
        int_spinbox.set(column_value)

        save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_int)
        save_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        DATA_ORDER_CHANGE = False
        
        dialog.lift()
        dialog.focus_set()  
        dialog.grab_set()   
        dialog.wait_window()

    def string_modify_dialog(column_name):
        global DATA_ORDER_CHANGE, column_value
        def save_string():
            global column_value, DATA_ORDER_CHANGE
            column_value = entry_string.get()
            print(f"Modifica '{column_name}': {column_value}")
            DATA_ORDER_CHANGE = True
            dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

        dialog = ctk.CTkToplevel()
        dialog.title(f"Modifica {column_name}")

        ctk.CTkLabel(master=dialog, text=f"{column_name}:").grid(row=0, column=0, padx=5, pady=5)
        entry_string = ctk.CTkEntry(master=dialog, width=50, height=50)
        entry_string.grid(row=0, column=1, padx=5, pady=5)
        if(column_value == None):
            column_value = ''
            entry_string.insert(0, column_value)
        else:
            entry_string.insert(0, column_value)

        save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_string)
        save_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        DATA_ORDER_CHANGE = False
        
        dialog.lift()
        dialog.focus_set()  
        dialog.grab_set()   
        dialog.wait_window()

    def datetime_modify_dialog(datetime_to_mod):
        global DATA_ORDER_CHANGE

        def save_datetime():
            global new_date, column_value, DATA_ORDER_CHANGE
            selected_date = datetime.strptime(f"{day_spinbox.get()}/{month_spinbox.get()}/{year_spinbox.get()}", "%d/%m/%Y")
            selected_hour = int(hour_spinbox.get())
            selected_minute = int(minute_spinbox.get())
            column_value = datetime(selected_date.year, selected_date.month, selected_date.day, selected_hour, selected_minute)
            print("Data e ora inserite:", column_value)
            #start_time_time_elapsed_label.configure(text= selected_start_datetime)
            DATA_ORDER_CHANGE = True
            dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

        current_date = datetime.now()
        current_hour = datetime_to_mod.hour
        current_minute = datetime_to_mod.minute

        dialog = ctk.CTkToplevel()
        dialog.title("Inserisci data e ora d'inizio")

        ctk.CTkLabel(master=dialog, text="Data:").grid(row=0, column=0, padx=5, pady=5)
        day_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=1, to=31, height=44, value=datetime_to_mod.day)
        day_spinbox.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(master=dialog, text="/").grid(row=0, column=2)
        month_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=1, to=12, height=44, value=datetime_to_mod.month)
        month_spinbox.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(master=dialog, text="/").grid(row=0, column=4)
        year_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, from_=datetime_to_mod.year, to=datetime_to_mod.year + 100, height=44, value=current_date.year)
        year_spinbox.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(master=dialog, text="Ora:").grid(row=1, column=0, padx=5, pady=5)
        hour_spinbox = CTkSpinbox(master=dialog, button_width=50, from_=0, to=23, width=76, height=44, value=current_hour)
        hour_spinbox.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(master=dialog, text="Minuti:").grid(row=1, column=2, padx=5, pady=5)
        minute_spinbox = CTkSpinbox(master=dialog, button_width=50, from_=0, to=59, width=76, height=44, value=current_minute)
        minute_spinbox.grid(row=1, column=3, padx=5, pady=5)

        save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_datetime)
        save_button.grid(row=2, column=0, columnspan=6, padx=5, pady=5)

        DATA_ORDER_CHANGE = False

        dialog.lift()
        dialog.focus_set()  
        dialog.grab_set()   
        dialog.wait_window()

    def modifica_valore_colonna():
        global selected_column, column_name, column_value, new_date, selected_order
        print(f"modifica:\n{selected_column}\n{column_name}\n{column_value}")

        if isinstance(column_value, str):
            # Verifica se la stringa può essere convertita in un oggetto datetime
            try:
                column_value_datetime = datetime.strptime(column_value, "%Y-%m-%d %H:%M:%S")
                datetime_modify_dialog(column_value_datetime)
            except ValueError:
                string_modify_dialog(column_name)
        elif isinstance(column_value, int):
            int_modify_dialog(column_name)
        elif(isinstance, None):
            string_modify_dialog(column_name)
        else:
            print("Tipo di dato non supportato.")
        
        selected_order[selected_column] = column_value
        print(selected_order[selected_column])
        table_selected_order.insert(1, selected_column, column_value)
        table_orders_list.insert(selected_row, selected_column, column_value)
        print(selected_order)
        if DATA_ORDER_CHANGE:
            print(f'DATA_ORDER_CHANGE: {DATA_ORDER_CHANGE}')
            update_db_value(selected_order[0])
        else:
            print(f'DATA_ORDER_CHANGE: {DATA_ORDER_CHANGE}')
        #table_selected_order.edit()




    def conferma_modifica():
        print("conferma")

    def elimina_ordine():
        global selected_order, selected_row

        CHOICE = ask_question_choice(f"Sei sicuro di voler eliminare l'ordine con ID:{selected_order[0]}")

        if CHOICE:
            try:
                db_name = LOGGED_USER_DB

                conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
                cur = conn.cursor()

                query = """
                    DELETE FROM {} 
                    WHERE id = %s
                """.format('ordini')

                cur.execute(query, (selected_order[0],))
                conn.commit()

                CTkMessagebox(title="Eliminazione ordine", 
                            message="Ordine eliminato con successo!",
                            icon="info"
                            )
                    
                table_orders_list.delete_row(selected_row)
                draw_table_orders()
                button_modifica_ordine_selezionato.grid_forget()
                button_elimina_ordine_selezionato.grid_forget()
                frame_gestione_selezione_ordine_effettuato.place_forget()

            except (Exception, psycopg2.Error) as error:
                print("Errore durante l'eliminazione dell'ordine:", error)

            finally:
                if conn:
                    cur.close()
                    conn.close()


    #recent_orders = get_last_orders(TABLE_ORDERS_ROW)
    
    switch_page(modify_order_page)

    table_orders_list = CTkTable(master=modify_order_page, width= 70, height= 38, row=TABLE_ORDERS_ROW + 1, command=show_row_select, column=12)
    table_selected_order = CTkTable(master=frame_gestione_selezione_ordine_effettuato, width= 70, height= 38,  command=show_column_select, row=2, column=12)

    def draw_table_orders():
        global recent_orders

        recent_orders = get_last_orders(TABLE_ORDERS_ROW)

        intestazioni = ["ID", "Orario inizio", "Orario fine", "Numero disegno", "Tempo taglio", "Tempo tornitura", 
                        "Tempo fresatura", "Tempo elettroerosione", "Tempo ciclo", "Tempo setup", "Numero pezzi", "Note lavorazione"]
        
        for col, intestazione in enumerate(intestazioni):
            table_orders_list.insert(0, col, intestazione, bg_color="lightgrey")

        # Popolamento della tabella con gli ordini
        for row, ordine in enumerate(recent_orders, start=1):
            for col, valore in enumerate(ordine, start=0):
                if isinstance(valore, datetime):
                    valore = valore.strftime("%Y-%m-%d %H:%M:%S")
                #print(f"col: {col}, valore: {valore}")
                table_orders_list.insert(row, col, valore)

        table_orders_list.pack(expand=True, padx=20, pady=20, anchor='n')
    
    draw_table_orders()

    frame_gestione_modifica_ordine_selezionato = ctk.CTkFrame(
        master=modify_order_page,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )

    # Creazione del frame
    frame_gestione_lista_ordini_effettuati = ctk.CTkFrame(
        master=modify_order_page,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )
    
    button_conferma_modifica = ctk.CTkButton(
        master=frame_gestione_lista_ordini_effettuati, 
        bg_color=['gray92', 'gray14'], 
        text="Conferma ordine",
        width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
        height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT)#,
        #command=lambda: conferma_ordine()
    )

    button_indietro_modifica = ctk.CTkButton(
        master=frame_gestione_lista_ordini_effettuati, 
        bg_color=['gray92', 'gray14'], 
        text="Indietro",
        width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
        height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
        command=lambda: back_to_home()
    )

    button_conferma_modifica.configure(state= 'Disabled')

    # Posizionamento del frame
    frame_gestione_lista_ordini_effettuati.place(relx=0.5, rely=0.9, anchor='s')
    #button_conferma_modifica.grid(row=0, column=0, padx=10, pady=10)
    button_indietro_modifica.grid(row=0, column=3, padx=10, pady=10)

    frame_buttons_selezione_ordine_effettuato = ctk.CTkFrame(
        master=frame_gestione_selezione_ordine_effettuato,
        width=ORDER_BUTTONS_FRAME_WIDTH,
        height=ORDER_BUTTONS_FRAME_WIDTH
    )

    button_modifica_ordine_selezionato = ctk.CTkButton(
        master=frame_buttons_selezione_ordine_effettuato, 
        bg_color=['gray92', 'gray14'], 
        text="Modifica ordine",
        width=_map_item_x(140 + 10, ORDER_BUTTONS_FRAME_WIDTH),
        height=_map_item_y(28 + 10, ORDER_BUTTONS_FRAME_HEIGHT),
        command=lambda: modifica_valore_colonna()
    )

    button_elimina_ordine_selezionato = ctk.CTkButton(
        master=frame_buttons_selezione_ordine_effettuato, 
        bg_color=['gray92', 'gray14'], 
        text="Elimina ordine",
        width=_map_item_x(140 + 10, ORDER_BUTTONS_FRAME_WIDTH),
        height=_map_item_y(28 + 10, ORDER_BUTTONS_FRAME_HEIGHT),
        command=lambda: elimina_ordine()
    )


def salva_ordine():
    order_to_db('ordini_in_sospeso')

def conferma_ordine():
    order_to_db('ordini')
    
def ask_question_confirm_order(orario_fine_dt, tempo_setup, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, orario_inizio, numero_pezzi, numero_disegno, note_lavorazione):
    # Formattazione dei dati come una tabella
    tabella = (
        f"{'INIZIO:':<20}{orario_inizio}\n"
        f"{'FINE:':<20}{orario_fine_dt}\n"
        f"{'N DISEGNO:':<20}{numero_disegno}\n"
        f"{'SETUP:':<20}{tempo_setup} m\n"
        f"{'TAGLIO:':<20}{tempo_taglio} m\n"
        f"{'TORNITURA:':<20}{tempo_tornitura} m\n"
        f"{'FRESATURA:':<20}{tempo_fresatura} m\n"
        f"{'ELETTROEROSIONE:':<20}{tempo_elettroerosione} m\n"
        f"{'N PEZZI:':<20}{numero_pezzi} prodotti\n"
        f"{'NOTE.:':<20}{note_lavorazione[:10]}...\n"
    )

    # Creazione del messaggio di messagebox
    msg = CTkMessagebox(
        master= home_page,
        title="Conferma ordine", 
        message=f"Dettagli dell'ordine:\n\n{tabella}\n\nSei sicuro di voler confermare?",
        width=500,
        icon="question", 
        option_1="Conferma", 
        option_2="Modifica" 
    )

    # Ottieni la risposta dal messagebox
    response = msg.get()

    if response=="Conferma":
        return True
    elif response=="Modifica":
        return False

#LOGIN FRAME
LOGIN_FRAME_WIDTH = 190 + 10
LOGIN_FRAME_HEIGHT = 263 + 10

frame_login = ctk.CTkFrame(
    master=login_page, 
    width=_map_frame_x(LOGIN_FRAME_WIDTH),
    height=_map_frame_y(LOGIN_FRAME_HEIGHT)
    )

switch = ctk.CTkSwitch(login_page, text="On-Screen Keyboard", command=show_popup)

user_menu_label = ctk.CTkLabel(
    master=frame_login, 
    bg_color=['gray92', 'gray14'], 
    text="Seleziona utente"
    )
user_menu_label.place(x=_map_item_x(50, LOGIN_FRAME_WIDTH), y=_map_item_y(3, LOGIN_FRAME_HEIGHT))

passwd_login_entry = ctk.CTkEntry(
    master=frame_login, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )
passwd_login_entry.configure(show='*')
passwd_login_entry.place(x=_map_item_x(25, LOGIN_FRAME_WIDTH), y=_map_item_y(110, LOGIN_FRAME_HEIGHT))

passwd_label = ctk.CTkLabel(
    master=frame_login, 
    bg_color=['gray92', 'gray14'], 
    text="Password")
passwd_label.place(x=_map_item_x(65, LOGIN_FRAME_WIDTH), y=_map_item_y(75, LOGIN_FRAME_HEIGHT))

login_button = ctk.CTkButton(
    master=frame_login, 
    bg_color=['gray92', 'gray14'], 
    width=_map_item_x(140 + 10, LOGIN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
    text="Accedi")
login_button.place(x=_map_item_x(25, LOGIN_FRAME_WIDTH), y=_map_item_y(168, LOGIN_FRAME_HEIGHT))

# Collega la funzione al pulsante "Accedi"
login_button.configure(command=accedi)

back_login_button = ctk.CTkButton(
    master=frame_login,
    bg_color=['gray92','gray14'],
    command=lambda: switch_page(home_page),
    width=_map_item_x(140 + 10, LOGIN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
    text="Indietro")
back_login_button.place(x=_map_item_x(25, LOGIN_FRAME_WIDTH), y=_map_item_y(210, LOGIN_FRAME_HEIGHT))

#FRAME GESTIONE ORDINE
ORDER_MAN_FRAME_WIDTH = 400 
ORDER_MAN_FRAME_HEIGHT = 200

#FRAME GESTIONE ORDINE
ORDER_BUTTONS_FRAME_WIDTH = 160
ORDER_BUTTONS_FRAME_HEIGHT = 40

# Creazione del frame
frame_gestione_ordine = ctk.CTkFrame(
    master=home_page,
    width=ORDER_MAN_FRAME_WIDTH,
    height=ORDER_MAN_FRAME_HEIGHT
)

# Creazione del pulsante all'interno del frame
button_conferma_ordine = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Conferma ordine",
    width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: conferma_ordine()
)

# Posizionamento del frame
button_conferma_ordine.grid(row=0, column=0, padx=10, pady=10)

button_salva_ordine = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Salva ordine",
    width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: salva_ordine()
)

# Posizionamento del frame
#button_salva_ordine.grid(row=0, column=1, padx=10, pady=10)

button_carica_ordine = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Ordini effettuati",
    width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: modifica_ordine()
)

# Posizionamento del frame
button_carica_ordine.grid(row=0, column=2, padx=10, pady=10)

button_reset_ordine = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Azzera ordine",
    width=_map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: azzera_ordine()
)

# Posizionamento del frame
button_reset_ordine.grid(row=0, column=3, padx=10, pady=10)



pezzi_label = ctk.CTkLabel(master=frame_n_pezzi, bg_color=['gray86', 'gray17'], text="N. Pezzi")
pezzi_label.place(x=_map_item_x(55, N_PEZZI_FRAME_WIDTH), y=_map_item_y(8, N_PEZZI_FRAME_HEIGHT))

lista_utenti = get_user_databases() #["Utente1", "Utente2", "Utente3"]

menu_tendina_utenti = ctk.CTkOptionMenu(
    master=frame_login, 
    values=[], 
    bg_color=['gray86', 'gray17'],
    width=_map_item_x(140 + 10, LOGIN_FRAME_WIDTH), 
    height=_map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
    dropdown_font = ctk.CTkFont(
        'Roboto',
        size=16),
    hover=False)
menu_tendina_utenti.place(x=_map_item_x(25, LOGIN_FRAME_WIDTH), y=_map_item_y(37, LOGIN_FRAME_HEIGHT))

frame_gestione_selezione_ordine_effettuato = ctk.CTkFrame(
        master=modify_order_page,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )

#menu_tendina_utenti.
menu_tendina_utenti.configure(values=lista_utenti)

# Imposta il testo predefinito
default_text = "Seleziona un utente"  # Puoi cambiare questo testo se necessario
menu_tendina_utenti.set(default_text)

root.resizable(True, True)  # La finestra sarà ridimensionabile sia in larghezza che in altezza

def on_window_resize(event):
    global root_height
    global root_width
    global numpad_x
    global numpad_y
    # Aggiorna i valori dei widget in base alle dimensioni attuali della finestra
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    if frame_container_time.winfo_exists():
        width_container_time_frame = 222.5 * len(selected_checkbox_text.split(", "))
        if(width_container_time_frame < root_width - 150):
            #print(f"width_container_time_frame: {width_container_time_frame}, root_width: {root_width}")
            frame_container_time.place_forget()
            frame_container_time.configure(width = 222.5 * len(selected_checkbox_text.split(", ")))
        else:
            frame_container_time.place_forget()
            frame_container_time.configure(width = root_width - 250)
        frame_container_time.place(relx=0.50, rely=0.19, anchor='n')
    else:
        frame_container_time.place_forget()

    if frame_singup.winfo_exists():
        frame_singup.place(relx=0.40, rely=0.1, anchor='n')
    if frame_settings.winfo_exists():
        frame_settings.place(relx=0.60, rely=0.1, anchor='n')
    if frame_login.winfo_exists():
        frame_login.place(relx=0.50, rely=0.1, anchor='n')
        # Ottieni le coordinate del frame login rispetto alla finestra principale
        frame_login_x = frame_login.winfo_rootx()
        frame_login_y = frame_login.winfo_rooty()

        # Ottieni le dimensioni del frame login
        frame_login_width = frame_login.winfo_width()
        frame_login_height = frame_login.winfo_height()

        # Calcola le coordinate per posizionare il numpad accanto al frame login
        numpad_x = frame_login_x + frame_login_width + 10  # Aggiungi 10 pixel di padding
        numpad_y = frame_login_y

    if frame_n_pezzi.winfo_exists():
        frame_n_pezzi.place(relx=0.999, rely=0.5, anchor='e')

    if frame_lavorazione.winfo_exists():
        frame_lavorazione.place(relx=0.50, rely=0.1, anchor='n')

    if frame_setup_time.winfo_exists():
        frame_setup_time.place(x=0, rely=0.5, anchor='w')

    if frame_start_time.winfo_exists():
        frame_start_time.place(x=0, rely=0.3, anchor='w')

    if frame_log_setting.winfo_exists():
        frame_log_setting.place(relx=0.999, rely=0.003,anchor='ne')

    if frame_connection_title.winfo_exists():
        frame_connection_title.place(relx=0.999, rely=0.99, anchor='se')

    if frame_n_draw.winfo_exists():
        frame_n_draw.place(relx=0.50, rely=0.4, anchor='n')

    if frame_gestione_ordine.winfo_exists():
        frame_gestione_ordine.place(relx=0.5, rely=0.9, anchor='s')
        

    if frame_note.winfo_exists():
        frame_note.place(relx=0.999, rely=0.3, anchor='e')

def on_checkbox_change(checkbox_name):
    # Larghezza minima desiderata tra i frame
    global PADX
    if(selected_checkbox_text):
        width_container_time_frame = 222.5 * len(selected_checkbox_text.split(", "))
        if(width_container_time_frame < root_width):
            #print(f"width_container_time_frame: {width_container_time_frame}, root_width: {root_width}")
            frame_container_time.place_forget()
            frame_container_time.configure(width = 222.5 * len(selected_checkbox_text.split(", ")))
        else:
            frame_container_time.place_forget()
            frame_container_time.configure(width = root_width - 250)
        frame_container_time.place(relx=0.50, rely=0.19, anchor='n')
    else:
        frame_container_time.place_forget()

    if checkbox_name == "taglio":
        if taglio_checkbox.get():
            frame_taglio_time.grid(row=0, column=0, padx=PADX)
        else:
            frame_taglio_time.grid_remove()
    elif checkbox_name == "tornitura":
        if tornitura_checkbox.get():
            frame_tornitura_time.grid(row=0, column=1, padx=PADX)
        else:
            frame_tornitura_time.grid_remove()
    elif checkbox_name == "fresatura":
        if fresatura_checkbox.get():
            frame_fresatura_time.grid(row=0, column=2, padx=PADX)
        else:
            frame_fresatura_time.grid_remove()
    elif checkbox_name == "elettro":
        if elettro_checkbox.get():
            frame_elettro_time.grid(row=0, column=3, padx=10)
        else:
            frame_elettro_time.grid_remove()

    elif checkbox_name == "draw_mode":
        draw_check = draw_mode_checkbox.get()
        if draw_check:
            draw_num_entry.place_forget()
            menu_tendina_disegni.place(relx = 0.02, rely=0.4)
            draw_open_pdf_button.place(relx = 0.775, rely=0.4)
            save_config("draw_mode_checkbox", draw_check)
        else:
            draw_num_entry.place(relx = 0.09, rely=0.4)
            menu_tendina_disegni.place_forget()
            draw_open_pdf_button.place_forget()
            save_config("draw_mode_checkbox", draw_check)

numpad_login = CTkPopupKeyboard.PopupNumpad(
    attach= passwd_login_entry,
    keycolor= 'dodgerblue2',
    keywidth= KEYWIDTH,
    keyheight= KEYHEIGHT
    )

numpad_singup_password = CTkPopupKeyboard.PopupNumpad(
    attach= passwd_singup_entry,
    keycolor= 'dodgerblue2',
    keywidth= KEYWIDTH,
    keyheight= KEYHEIGHT
    )

numpad_singup_password = CTkPopupKeyboard.PopupNumpad(
    attach= passwd_repeat_singup_entry,
    keycolor= 'dodgerblue2',
    keywidth= KEYWIDTH,
    keyheight= KEYHEIGHT
    )

switch = ctk.CTkSwitch(login_page, text="On-Screen Numboard", command=show_popup)
switch.pack(pady=10)
switch.toggle()

# Associa la funzione on_checkbox_change a ciascun checkbox
tornitura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("tornitura"))
fresatura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("fresatura"))
elettro_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("elettro"))
taglio_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("taglio"))

draw_mode_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("draw_mode"))

def schedule_check():
    # Esegui il controllo e poi pianifica il prossimo controllo
    check_db_connection(db_config)
    root.after(5000, schedule_check)  # 5000 millisecondi = 5 secondi

schedule_check()

root.bind("<Configure>", on_window_resize)

root.mainloop()