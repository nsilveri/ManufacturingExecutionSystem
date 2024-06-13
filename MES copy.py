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
from libs import CTkPopupKeyboard, machineData, check_box_manager
from libs.db_manager import DbManager
from libs.modOrders import modifica_ordine
from libs.loginMan import switch_page_for_login
from libs.mapFunctions import Mapper
from libs.definitions import *
from libs.support_functions import *
import tkinter as tk
import shutil
from threading import Timer
#from libs.variables import var.LOGGED_USER, var.LOGGED_USER
import libs.variables as var
from libs.pages import home_frames
from libs import numPads, queries

ORIGINAL_WIDTH =  800
ORIGINAL_HEIGHT = 500
root_width = ORIGINAL_WIDTH
root_height = ORIGINAL_HEIGHT

DB_STATE = 'Non connesso'

DRAW_NUM = ''

PADX = 5
ELAPSED_TIME_LABEL_X = 0.1
ELAPSED_TIME_LABEL_Y = 0.3
RELY_TIMER_BUTTONS = 0.59

PADX_FRAME_GESTIONE_ORDINI = 15
PADY_FRAME_GESTIONE_ORDINI = 15

DATA_ORDER_CHANGE = False

UPDATE_TIMER_DELAY = 1000

LOAD_TEMP = True
MENU_MODIFICA_DATI = False

# Creazione del gestore dati delle macchine
machine_data = machineData.MachineManager()


mapper = Mapper(ORIGINAL_WIDTH, ORIGINAL_HEIGHT, root_width, root_height)

selected_row = None
selected_column = None
prev_selected_row = None
prev_selected_column= None
column_name = None
column_value = None
new_date = None
value_for_db = None

MACHINE_SELECT_STATE = False

checkBoxMan = check_box_manager.CheckboxStateHandler(machine_data)

 # Impostazione dei dati booleani
checkbox_states = {
    "taglio": False,
    "tornitura": False,
    "fresatura": False,
    "elettro": False
}

# Inizializza MACCHINARIO con il primo elemento della lista
MACCHINARIO = machines[0]



ctk.set_appearance_mode(load_config("theme"))
ctk.set_default_color_theme(load_config("color"))

db_config = {
    'host':     load_config('pg_host'),      #'SPH-SERVER-PRODUZIONE'
    'port':     load_config('pg_port'),      #'5432',
    'user':     load_config('pg_user'),      #'postgres',
    'password': load_config('pg_passwd')     #'SphDbProduzione'
}

DBMan = DbManager(db_config, var.LOGGED_USER)

def update_gui_scale(new_value):
    var.set_gui_scale(new_value)
    ctk.set_widget_scaling(var.GUI_SCALE/100)  # widget dimensions and text size
    save_config("gui_scale", var.GUI_SCALE)

def update_num_board(new_value):
    global NUM_BOARD_SIZE

    NUM_BOARD_SIZE = new_value
    save_config("keywidth", NUM_BOARD_SIZE)
    save_config("keyheight", NUM_BOARD_SIZE)
    var.set_key_size(NUM_BOARD_SIZE, NUM_BOARD_SIZE)

def update_color(new_value):
    global COLOR
    COLOR = new_value
    save_config("color", COLOR)
    ctk.set_default_color_theme(load_config("color"))

THEME = load_config("theme", "blue")
#GUI_SCALE = load_config("gui_scale", 1)
var.set_gui_scale(load_config("gui_scale", 100))
COLOR = load_config("color", "blue")
var.set_key_size(load_config("keywidth", 75), load_config("keyheight", 75))

ctk.set_widget_scaling(var.GUI_SCALE/100)  # widget dimensions and text size
ctk.set_window_scaling(1)  # window geometry dimensions

def restart_program():
    python = sys.executable
    subprocess.call([python, sys.argv[0]])

def switch_page(page):
    pages = [home_page, singup_page, login_page, modify_order_page]
    for i in pages:
        i.pack_forget()
    page.pack(expand=True, fill='both')

    fixed_widgets = []
    for widget in fixed_widgets:
        widget.lift()
        widget.place(x=widget.winfo_x(), y=widget.winfo_y())

root = ctk.CTk()
root.title("MES Industry")
root.geometry((f"{ORIGINAL_WIDTH}x{ORIGINAL_HEIGHT}"))
root.resizable(False, False)

home_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
home_page.pack(expand=True, fill='both')

#home_frames.MyHomePage(root)

singup_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
login_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
modify_order_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)

for machine in machines:
    machine_data.add_empty_machine(machine)

def get_pdf_files_in_directory(directory_path):
    try:
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
    except:
        print("Errore durante la lettura dei file PDF nella directory.")
        CTkMessagebox(
            master=home_page,
            title="Errore",
            message="Errore durante la lettura dei file PDF nella directory.",
            icon="error",
            option_1="OK"
        )
        return []        

directory_path = load_config("draw_directory")
pdf_file_list = get_pdf_files_in_directory(directory_path)

#FRAME TITLE
FRAME_TITLE_WIDTH = 152
FRAME_TITLE_HEIGHT = 40

frame_app_title = ctk.CTkFrame(
    master=home_page, 
    width=mapper._map_item_x(162, FRAME_TITLE_WIDTH), 
    height=mapper._map_item_y(40, FRAME_TITLE_HEIGHT)
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
    width=mapper._map_frame_x(FRAME_CONN_WIDTH),
    height=mapper._map_frame_y(FRAME_CONN_HEIGHT)
    )

connection_state_text = "Utente: " + var.LOGGED_USER + "DB: " + DB_STATE

label_logged_user = ctk.CTkLabel(
    master=frame_connection_title,
    font=ctk.CTkFont(
        'Roboto',
        size=15),
    bg_color=['gray86','gray17'],
    height=10,
    text= f"Utente: {var.LOGGED_USER}")

label_db_conn_state = ctk.CTkLabel(
    master=frame_connection_title,
    font=ctk.CTkFont(
        'Roboto',
        size=15),
    bg_color=['gray86','gray17'],
    height=10,
    text= f"DB: {DB_STATE}")

label_logged_user.grid(row= 0, column= 0, padx= 5, pady= 5)
label_db_conn_state.grid(row= 0, column= 1, padx= 5, pady= 5)

def update_db_user_state():
    if(var.LOGGED_USER == ''):
        LOGGED_USER_AUX = 'Ness.utente'
    else:
        LOGGED_USER_AUX = var.LOGGED_USER
    label_logged_user.configure(text=f"Utente: {LOGGED_USER_AUX}")
    label_db_conn_state.configure(text=f"DB: {DB_STATE}")

#switch_login_page()

#FRAME LOGIN SETTINGS
LOG_SET_FRAME_WIDTH = 106# + 20
LOG_SET_FRAME_HEIGHT = 40# + 20
frame_log_setting = ctk.CTkFrame(
    master=home_page, 
    width=mapper._map_frame_x(LOG_SET_FRAME_WIDTH), 
    height=mapper._map_frame_y(LOG_SET_FRAME_HEIGHT)
    )

def set_logged_user():

    switch_page_for_login(switch_page, home_page, login_page, users_list, mapper, get_user_databases, DBMan, carica_temp, var.KEYWIDTH, var.KEYHEIGHT)#, var.LOGGED_USER, var.LOGGED_USER)
    print(f"MAIN: Utente loggato: {var.LOGGED_USER}")
    if var.LOGGED_USER != '':
        update_db_user_state()

login_button = ctk.CTkButton(
    master=frame_log_setting,
    bg_color=[
        'gray86',
        'gray17'],
    width=mapper._map_item_x(50 + 5, LOG_SET_FRAME_WIDTH),
    height=mapper._map_item_y(30 + 5, LOG_SET_FRAME_HEIGHT),
    text="Login",
    command=lambda: set_logged_user()
    )

setting_button = ctk.CTkButton(
    master=frame_log_setting,
    bg_color=[
        'gray86',
        'gray17'],
    compound="left",
    width=mapper._map_item_x(36 + 5, LOG_SET_FRAME_WIDTH),
    height=mapper._map_item_y(30 + 5, LOG_SET_FRAME_HEIGHT),
    text="",
    image=ctk.CTkImage(
        Image.open(r'libs\gear_icon.png'),
        size=(20,20)),
        command=lambda: switch_page(singup_page))

login_button.grid(row=0, column= 0, padx= 5, pady= 5)
setting_button.grid(row=0, column= 1, padx= 5, pady= 5)

#FRAME SETUP TIME 
SETUP_TIME_FRAME_WIDTH = 210
SETUP_TIME_FRAME_HEIGHT_MANUAL = 100
SETUP_TIME_FRAME_HEIGHT_AUTO = 150

#GENERAZIONE FRAME
frame_setup_time = ctk.CTkFrame(
    master=home_page,
    width=mapper._map_frame_x(SETUP_TIME_FRAME_WIDTH), 
    height=mapper._map_frame_y(SETUP_TIME_FRAME_HEIGHT_MANUAL)
)

#GENERAZIONE LABEL
tempo_setup_label = ctk.CTkLabel(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di setup (min)"
)
tempo_setup_label.place(x=mapper._map_item_x(18, SETUP_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, SETUP_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_setup_num = CTkSpinbox(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=mapper._map_item_x(76, SETUP_TIME_FRAME_WIDTH), 
    height=mapper._map_item_y(44, SETUP_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20'],
    command= lambda: machine_data.machines[MACCHINARIO].timers.set_start("setup", int(tempo_setup_num.get()))
)
tempo_setup_num.place(x=mapper._map_item_x(10, SETUP_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, SETUP_TIME_FRAME_HEIGHT_MANUAL))

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
    command=lambda: machine_data.machines[MACCHINARIO].timers.start_timer("setup")
)

setup_button_stop = ctk.CTkButton(
    master=frame_setup_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: machine_data.machines[MACCHINARIO].timers.stop_timer("setup") #stop_setup()
)

setup_button_reset = ctk.CTkButton(
    master=frame_setup_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: machine_data.machines[MACCHINARIO].timers.reset_timer("setup") #reset_setup()
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
setup_time_elapsed_label = ctk.CTkLabel(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'], 
    text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("setup") #timer_manager.get_elapsed_time(MACCHINARIO, 'setup') machine_data["PUMA"].add_timer("setup")
)
setup_time_elapsed_label.place(relx=0.1, rely=0.6)

setup_start_time = None

for machine in machines:
    print(machine)
    machine_data.machines[machine].timers.add_timer("setup")
    machine_data.machines[machine].timers.add_timer("taglio")
    machine_data.machines[machine].timers.add_timer("tornitura")
    machine_data.machines[machine].timers.add_timer("fresatura")
    machine_data.machines[machine].timers.add_timer("elettro")

    machine_data.machines[machine].dates.add_date("inizio")
    machine_data.machines[machine].dates.add_date("fine")

    machine_data.machines[machine].prod_data.add_prod_data("pezzi")
    machine_data.machines[machine].prod_data.set_prod_data("pezzi", 0)

    machine_data.machines[machine].prod_data.add_prod_data("checkbox_state")
    checkBoxMan.set_checkbox_states(checkbox_states, machine)

    machine_data.machines[machine].prod_data.add_prod_data("numero_disegno_tendina")
    machine_data.machines[machine].prod_data.set_prod_data("numero_disegno_tendina", "Sel. num. disegno")

    machine_data.machines[machine].prod_data.add_prod_data("numero_disegno_entry")
    machine_data.machines[machine].prod_data.set_prod_data("numero_disegno_entry", "")

    machine_data.machines[machine].prod_data.add_prod_data("note_lavorazione")
    machine_data.machines[machine].prod_data.set_prod_data("note_lavorazione", "")

    machine_data.machines[machine].prod_data.add_prod_data("commessa_lavorazione")
    machine_data.machines[machine].prod_data.set_prod_data("commessa_lavorazione", "")


machine_data.machines[MACCHINARIO].timers.set_attach_buttons("setup", [setup_button_inizio, setup_button_stop, setup_button_reset])



# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_setup():
    setup_elapsed_time = machine_data.machines[MACCHINARIO].timers.get_elapsed_time("setup")
    setup_time_elapsed_label.configure(text=setup_elapsed_time)

    # Se il tempo trascorso non corrisponde al tempo impostato e la casella di controllo è selezionata, aggiorna il valore
    if int(setup_elapsed_time.split(":")[0]) != int(tempo_setup_num.get()) and setup_time_checkbox.get():
        tempo_setup_num.configure(value=int(setup_elapsed_time.split(":")[0]))
    elif int(setup_elapsed_time.split(":")[0]) != int(tempo_setup_num.get()) and not setup_time_checkbox.get():
        machine_data.machines[MACCHINARIO].timers.set_start("setup", int(tempo_setup_num.get()))

    # Richiama la funzione ogni secondo per aggiornare il tempo trascorso
    frame_setup_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_setup)


def carica_temp():
    global LOAD_TEMP
    global tempo_setup_num, pezzi_select_num, tempo_taglio_num, tempo_fresatura_num, tempo_tornitura_num, tempo_elettro_num, menu_tendina_disegni, draw_num_entry, note_num_entry
    default_temp = {"selected_start_datetime": None, "tempo_setup_num": 0, "pezzi_select_num": 0, "tempo_taglio_num": 0, "tempo_fresatura_num": 0, "tempo_tornitura_num": 0, "tempo_elettro_num": 0, "menu_tendina_disegni": "Sel. num. disegno", "draw_num_entry": "", "note_num_entry": ""}
    if LOAD_TEMP:
        if var.LOGGED_USER != '':
            file_name = f"{var.LOGGED_USER}_temp.json"
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
                    print(data == default_temp)
                    print(f'data: {data} \ndefa: {default_temp}')
                if(data == default_temp):
                    print("dati default trovati")
                    return
                restore = ask_question_choice(f"Sono stati trovati dati precedentemente inseriti per l'utente {var.LOGGED_USER}, vuoi ripristinarli?", home_page)
                if not restore:
                    LOAD_TEMP = False
                    return
                LOAD_TEMP = False

                # Imposta le variabili globali con i valori dal file JSON
                machine_data.machines[MACCHINARIO].dates.set_date("inizio", data["selected_start_datetime"])
                start_time_time_elapsed_label.configure(text= machine_data.machines[MACCHINARIO].dates.get_date("inizio"))
                tempo_setup_num.configure(value= data["tempo_setup_num"])
                pezzi_select_num.configure(value= data["pezzi_select_num"])
                tempo_taglio_num.configure(value= data["tempo_taglio_num"])
                tempo_fresatura_num.configure(value= data["tempo_fresatura_num"])
                tempo_tornitura_num.configure(value= data["tempo_tornitura_num"])
                tempo_elettro_num.configure(value= data["tempo_elettro_num"])
                menu_tendina_disegni.set(str(data["menu_tendina_disegni"]))

                LOAD_TEMP = False

            except FileNotFoundError:
                # Se il file non esiste, non fare nulla
                LOAD_TEMP = False
                pass

# Dati precedenti
previous_data = {}

def salva_temp():
    global LOAD_TEMP
    global previous_data

    current_data_default = {
                "selected_start_datetime": 'null',
                "tempo_setup_num": 0,
                "pezzi_select_num": 0,
                "tempo_taglio_num": 0,
                "tempo_fresatura_num": 0,
                "tempo_tornitura_num": 0,
                "tempo_elettro_num": 0,
                "menu_tendina_disegni": "Sel. num. disegno",
                "draw_num_entry": "",
                "note_num_entry": ""
            }
    
    #print(LOAD_TEMP)
    if var.LOGGED_USER != '' and not LOAD_TEMP:
        # Dati attuali
        try:
            current_data = {
                "selected_start_datetime": machine_data.machines[MACCHINARIO].dates.get_date("inizio"),
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

            #print(f"current_data: {current_data}")

            # Confronta con i dati precedenti
            if current_data != previous_data:
                file_name = f"{var.LOGGED_USER}_temp.json"  # Nome del file JSON con la variabile user
                with open(file_name, 'w') as f:
                    json.dump(current_data, f)
                previous_data = current_data
        except Exception as e:
            print(f"Errore durante il salvataggio dei dati temporanei: {e}")

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
        setup_time_elapsed_label.configure(text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("setup")) #timer_manager.get_elapsed_time(MACCHINARIO, 'setup')) #"{:d}:{:02d}".format(setup_minutes, setup_seconds))
        tempo_setup_label.configure(text="Tempo di setup")
        setup_minutes = tempo_setup_num.get()
        #frame_setup_time.configure(height=mapper._map_frame_y(SETUP_TIME_FRAME_HEIGHT_AUTO))
        #setup_start_time = time.time()
        update_elapsed_time_setup()  # Avvia l'aggiornamento del tempo trascorso
    else:
        setup_button_inizio.place_forget()
        setup_button_stop.place_forget()
        setup_button_reset.place_forget()
        setup_time_elapsed_label.place_forget()
        tempo_setup_num.place(x=mapper._map_item_x(10, SETUP_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, SETUP_TIME_FRAME_HEIGHT_MANUAL))
        #setup_start_time = None
        tempo_setup_label.configure(text="Tempo di setup(min)")
        #setup_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso
        tempo_setup_num.configure(value=machine_data.machines[MACCHINARIO].timers.get_elapsed_time("setup").split(":")[0])

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
        datetime_set = datetime(selected_date.year, selected_date.month, selected_date.day, selected_hour, selected_minute)
        machine_data.machines[MACCHINARIO].dates.set_date("inizio", datetime_set)
        print("Data e ora inserite:", machine_data.machines[MACCHINARIO].dates.get_date("inizio"))
        start_time_time_elapsed_label.configure(text= machine_data.machines[MACCHINARIO].dates.get_date("inizio"))
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
    if MODE == 'current_date':
        #selected_start_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        machine_data.machines[MACCHINARIO].dates.set_date("inizio", time.strftime('%Y-%m-%d %H:%M:%S'))
        start_time_time_elapsed_label.configure(text= machine_data.machines[MACCHINARIO].dates.get_date("inizio"))
        print(f"Data e ora d'inizio del {MACCHINARIO}: {machine_data.machines[MACCHINARIO].dates.get_date("inizio")}")
    elif MODE == 'set_date':
        show_datetime_dialog()
        print(machine_data.machines[MACCHINARIO].dates.get_date("inizio"))

#FRAME START TIME
START_TIME_FRAME_WIDTH = 210
START_TIME_FRAME_HEIGHT = 100

#GENERAZIONE FRAME
frame_start_time = ctk.CTkFrame(
    master=home_page,
    width=mapper._map_frame_x(START_TIME_FRAME_WIDTH), 
    height=mapper._map_frame_y(START_TIME_FRAME_HEIGHT)
)

#GENERAZIONE LABEL
tempo_start_time_label = ctk.CTkLabel(
    master=frame_start_time, 
    bg_color=['gray86', 'gray17'], 
    text="Data e ora d'inizio"
)


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

tempo_start_time_label.grid(        row= 0, column= 0, padx= 5, pady= 0, columnspan= 2)#place(x=mapper._map_item_x(18, START_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, START_TIME_FRAME_HEIGHT))
start_time_time_elapsed_label.grid( row= 2, column= 0, padx= 5, pady= 0, columnspan= 2)#place(relx=0.1, rely=0.3)
start_time_button_inizia_ora.grid(  row= 3, column= 0, padx= 5, pady= 5)#place(relx=0.1, rely=RELY_TIMER_BUTTONS)
start_time_button_imposta.grid(     row= 3, column= 1, padx= 5, pady= 5)#place(relx=0.5, rely=RELY_TIMER_BUTTONS)

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

#GENERAZIONE FRAME
frame_taglio_time = ctk.CTkFrame(
    master=frame_container_time,
    width=TAGLIO_TIME_FRAME_WIDTH,#mapper._map_frame_x(TAGLIO_TIME_FRAME_WIDTH),
    height=TAGLIO_TIME_FRAME_HEIGHT_MANUAL#mapper._map_frame_y(TAGLIO_TIME_FRAME_HEIGHT)
    )

#GENERAZIONE LABEL
taglio_time_label = ctk.CTkLabel(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text="Tempo di taglio (min)"
)

#GENERAZIONE SELEZIONA NUMERO
tempo_taglio_num = CTkSpinbox(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=mapper._map_item_x(76, TAGLIO_TIME_FRAME_WIDTH), 
    height=mapper._map_item_y(44, TAGLIO_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20'],
    command= lambda: machine_data.machines[MACCHINARIO].timers.set_start("taglio", int(tempo_taglio_num.get()))
)

#GENERAZIONE CHECKBOX
taglio_time_checkbox = ctk.CTkCheckBox(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
)

# Posizionare il checkbox all'interno del frame_container_time
taglio_time_label.place(x=mapper._map_item_x(18, TAGLIO_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))
taglio_time_checkbox.place(relx=0.65, rely=0.1)
tempo_taglio_num.place(x=mapper._map_item_x(10, TAGLIO_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))

#grid(   row= 0, column= 0,                padx=5, pady= 5 )#
#grid(row= 0, column= 1,                padx=5, pady= 5 )#place(
#grid(    row= 2, columnspan= 2, padx=5, pady= 5 )#

#GENERAZIONE PULSANTI "INIZIO", "STOP" E "RESET"
taglio_button_inizio = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Avvia",
    command=lambda: machine_data.machines[MACCHINARIO].timers.start_timer("taglio") #timer_manager.start_timer(MACCHINARIO, "taglio")
)

taglio_button_stop = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: machine_data.machines[MACCHINARIO].timers.stop_timer("taglio") #timer_manager.stop_timer(MACCHINARIO, "taglio") 
)

taglio_button_reset = ctk.CTkButton(
    master=frame_taglio_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: machine_data.machines[MACCHINARIO].timers.reset_timer("taglio") #timer_manager.reset_timer(MACCHINARIO, "taglio"
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
taglio_time_elapsed_label = ctk.CTkLabel(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'], 
    text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("taglio")#"{:d}:{:02d}".format(taglio_minutes, taglio_seconds)
)
taglio_time_elapsed_label.place(relx=0.1, rely=0.6)

taglio_start_time = None

#timer_manager.add_timer(MACCHINARIO,"taglio")
machine_data.machines[MACCHINARIO].timers.set_attach_buttons("taglio", [taglio_button_inizio, taglio_button_stop, taglio_button_reset])
#timer_manager.set_attach_buttons(MACCHINARIO,"taglio", [taglio_button_inizio, taglio_button_stop, taglio_button_reset])

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_taglio():
    taglio_elapsed_time = machine_data.machines[MACCHINARIO].timers.get_elapsed_time("taglio")#timer_manager.get_elapsed_time(MACCHINARIO, 'taglio')
    #print(f"taglio_elapsed_time: {taglio_elapsed_time}")
    taglio_time_elapsed_label.configure(text=taglio_elapsed_time)

    # Se il tempo trascorso non corrisponde al tempo impostato e la casella di controllo è selezionata, aggiorna il valore
    if int(taglio_elapsed_time.split(":")[0]) != int(tempo_taglio_num.get()) and taglio_time_checkbox.get():
        tempo_taglio_num.configure(value=int(taglio_elapsed_time.split(":")[0]))
    elif int(taglio_elapsed_time.split(":")[0]) != int(tempo_taglio_num.get()) and not taglio_time_checkbox.get():
        machine_data.machines[MACCHINARIO].timers.set_start("taglio", int(tempo_taglio_num.get()))

    # Richiama la funzione ogni secondo per aggiornare il tempo trascorso
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
        #frame_container_time.configure(height=mapper._map_frame_y(TAGLIO_TIME_FRAME_HEIGHT_MANUAL))
        #taglio_start_time = time.time()
        update_elapsed_time_taglio()  # Avvia l'aggiornamento del tempo trascorso
    else:
        taglio_button_inizio.place_forget()
        taglio_button_stop.place_forget()
        taglio_button_reset.place_forget()
        taglio_time_elapsed_label.place_forget()
        tempo_taglio_num.place(x=mapper._map_item_x(10, TAGLIO_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, TAGLIO_TIME_FRAME_HEIGHT_MANUAL))
        #taglio_start_time = None
        taglio_time_label.configure(text="Tempo di taglio(min)")
        #taglio_time_elapsed_label.configure(text="0:00")  # Resetta il tempo trascorso
        tempo_taglio_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("taglio").split(":")[0])
        #timer_manager.get_elapsed_time(MACCHINARIO, 'taglio').split(":")[0])

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
tornitura_time_label.place(x=mapper._map_item_x(18, TORNITURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_tornitura_num = CTkSpinbox(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=mapper._map_item_x(76, TORNITURA_TIME_FRAME_WIDTH), 
    height=mapper._map_item_y(44, TORNITURA_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20'],
    command=lambda: machine_data.machines[MACCHINARIO].timers.set_start("tornitura", int(tempo_tornitura_num.get()))
)
tempo_tornitura_num.place(x=mapper._map_item_x(10, TORNITURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))

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
    command=lambda: machine_data.machines[MACCHINARIO].timers.start_timer("tornitura") #timer_manager.start_timer(MACCHINARIO, "tornitura"
)

tornitura_button_stop = ctk.CTkButton(
    master=frame_tornitura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: machine_data.machines[MACCHINARIO].timers.stop_timer("tornitura") #timer_manager.stop_timer(MACCHINARIO, "tornitura")
)

tornitura_button_reset = ctk.CTkButton(
    master=frame_tornitura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: machine_data.machines[MACCHINARIO].timers.reset_timer("tornitura") #timer_manager.reset_timer(MACCHINARIO, "tornitura")
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
tornitura_time_elapsed_label = ctk.CTkLabel(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'], 
    text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("tornitura") 
    #timer_manager.get_elapsed_time(MACCHINARIO, 'tornitura') #"{:d}:{:02d}".format(tornitura_minutes, tornitura_seconds)
)
tornitura_time_elapsed_label.place(relx=0.1, rely=0.6)

tornitura_start_time = None

#timer_manager.set_attach_buttons(MACCHINARIO, "tornitura", [tornitura_button_inizio, tornitura_button_stop, tornitura_button_reset])
machine_data.machines[MACCHINARIO].timers.set_attach_buttons("tornitura", [tornitura_button_inizio, tornitura_button_stop, tornitura_button_reset])
#timer_manager.set_start(MACCHINARIO, "tornitura", 5)

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_tornitura():
    tornitura_elapsed_time = machine_data.machines[MACCHINARIO].timers.get_elapsed_time("tornitura") 
    #timer_manager.get_elapsed_time(MACCHINARIO, "tornitura")
    #print(f"tornitura_elapsed_time: {tornitura_elapsed_time}")
    tornitura_time_elapsed_label.configure(text=tornitura_elapsed_time)

    # Se il tempo trascorso non corrisponde al tempo impostato e la casella di controllo è selezionata, aggiorna il valore
    if int(tornitura_elapsed_time.split(":")[0]) != int(tempo_tornitura_num.get()) and tornitura_time_checkbox.get():
        tempo_tornitura_num.configure(value=int(tornitura_elapsed_time.split(":")[0]))
    elif int(tornitura_elapsed_time.split(":")[0]) != int(tempo_tornitura_num.get()) and not tornitura_time_checkbox.get():
        [MACCHINARIO].timers.set_start("tornitura", int(tempo_tornitura_num.get()))
    
    # Richiama la funzione ogni secondo per aggiornare il tempo trascorso
    frame_container_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_tornitura)

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
        tempo_tornitura_num.place(x=mapper._map_item_x(10, TORNITURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, TORNITURA_TIME_FRAME_HEIGHT_MANUAL))
        tornitura_time_label.configure(text="Tempo di tornitura(min)")
        tempo_tornitura_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("tornitura").split(":")[0])
        #timer_manager.get_elapsed_time(MACCHINARIO, 'tornitura').split(":")[0])

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
fresatura_time_label.place(x=mapper._map_item_x(18, FRESATURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_fresatura_num = CTkSpinbox(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=mapper._map_item_x(76, FRESATURA_TIME_FRAME_WIDTH), 
    height=mapper._map_item_y(44, FRESATURA_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20'],
   command=lambda: machine_data.machines[MACCHINARIO].timers.set_start("fresatura", int(tempo_fresatura_num.get()))
)
tempo_fresatura_num.place(x=mapper._map_item_x(10, FRESATURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))

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
    command=lambda: machine_data.machines[MACCHINARIO].timers.start_timer("fresatura") #timer_manager.start_timer(MACCHINARIO, "fresatura"
)

fresatura_button_stop = ctk.CTkButton(
    master=frame_fresatura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: machine_data.machines[MACCHINARIO].timers.stop_timer("fresatura") #timer_manager.stop_timer(MACCHINARIO, "fresatura")
)

fresatura_button_reset = ctk.CTkButton(
    master=frame_fresatura_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: machine_data.machines[MACCHINARIO].timers.reset_timer("fresatura") #timer_manager.reset_timer(MACCHINARIO, "fresatura")
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
fresatura_time_elapsed_label = ctk.CTkLabel(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'], 
    text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("fresatura")
    #timer_manager.get_elapsed_time(MACCHINARIO, 'fresatura') #"{:d}:{:02d}".format(fresatura_minutes, fresatura_seconds)
)
fresatura_time_elapsed_label.place(relx=0.1, rely=0.6)

fresatura_start_time = None

#timer_manager.add_timer(MACCHINARIO, "fresatura")
machine_data.machines[MACCHINARIO].timers.set_attach_buttons("fresatura", [fresatura_button_inizio, fresatura_button_stop, fresatura_button_reset])
#timer_manager.set_attach_buttons(MACCHINARIO, "fresatura", [fresatura_button_inizio, fresatura_button_stop, fresatura_button_reset])

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_fresatura():
    fresatura_elapsed_time = machine_data.machines[MACCHINARIO].timers.get_elapsed_time("fresatura")
    #timer_manager.get_elapsed_time(MACCHINARIO, "fresatura")
    #print(f"fresatura_elapsed_time: {fresatura_elapsed_time}")
    fresatura_time_elapsed_label.configure(text=fresatura_elapsed_time)

    # Se il tempo trascorso non corrisponde al tempo impostato e la casella di controllo è selezionata, aggiorna il valore
    if int(fresatura_elapsed_time.split(":")[0]) != int(tempo_fresatura_num.get()) and fresatura_time_checkbox.get():
        tempo_fresatura_num.configure(value=int(fresatura_elapsed_time.split(":")[0]))
    elif int(fresatura_elapsed_time.split(":")[0]) != int(tempo_fresatura_num.get()) and not fresatura_time_checkbox.get():
        [MACCHINARIO].timers.set_start("fresatura", int(tempo_fresatura_num.get()))

    # Richiama la funzione ogni secondo per aggiornare il tempo trascorso
    frame_container_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_fresatura)


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
        tempo_fresatura_num.place(x=mapper._map_item_x(10, FRESATURA_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, FRESATURA_TIME_FRAME_HEIGHT_MANUAL))
        fresatura_time_label.configure(text="Tempo di fresatura(min)")
        tempo_fresatura_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("fresatura").split(":")[0])
        #timer_manager.get_elapsed_time(MACCHINARIO, 'fresatura').split(":")[0])

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
elettro_time_label.place(x=mapper._map_item_x(18, ELETTRO_TIME_FRAME_WIDTH), y=mapper._map_item_y(6, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))

#GENERAZIONE SELEZIONA NUMERO
tempo_elettro_num = CTkSpinbox(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'],
    button_width=50,
    width=mapper._map_item_x(76, ELETTRO_TIME_FRAME_WIDTH), 
    height=mapper._map_item_y(44, ELETTRO_TIME_FRAME_HEIGHT_MANUAL), 
    value=0, 
    fg_color=['gray81', 'gray20'],
    command=lambda: machine_data.machines[MACCHINARIO].timers.set_start("elettro", int(tempo_elettro_num.get()))
)
tempo_elettro_num.place(x=mapper._map_item_x(10, ELETTRO_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))

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
    command=lambda: machine_data.machines[MACCHINARIO].timers.start_timer("elettro") #timer_manager.start_timer(MACCHINARIO, "elettro"
)

elettro_button_stop = ctk.CTkButton(
    master=frame_elettro_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Stop",
    command=lambda: machine_data.machines[MACCHINARIO].timers.stop_timer("elettro") #timer_manager.stop_timer(MACCHINARIO, "elettro"
)

elettro_button_reset = ctk.CTkButton(
    master=frame_elettro_time, 
    width=10,
    height=28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Reset",
    command=lambda: machine_data.machines[MACCHINARIO].timers.reset_timer("elettro") #timer_manager.reset_timer(MACCHINARIO, "elettro"
)

#GENERAZIONE LABEL PER IL TEMPO TRASCORSO
elettro_time_elapsed_label = ctk.CTkLabel(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'], 
    text= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("elettro")
)
elettro_time_elapsed_label.place(relx=0.1, rely=0.6)

elettro_start_time = None

machine_data.machines[MACCHINARIO].timers.set_attach_buttons("elettro", [elettro_button_inizio, elettro_button_stop, elettro_button_reset])

# Funzione per aggiornare il tempo trascorso
def update_elapsed_time_elettro():
    elettro_elapsed_time = machine_data.machines[MACCHINARIO].timers.get_elapsed_time("elettro")
    elettro_time_elapsed_label.configure(text=elettro_elapsed_time)

    # Se il tempo trascorso non corrisponde al tempo impostato e la casella di controllo è selezionata, aggiorna il valore
    if int(elettro_elapsed_time.split(":")[0]) != int(tempo_elettro_num.get()) and elettro_time_checkbox.get():
        tempo_elettro_num.configure(value=int(elettro_elapsed_time.split(":")[0]))
    elif int(elettro_elapsed_time.split(":")[0]) != int(tempo_elettro_num.get()) and not elettro_time_checkbox.get():
        [MACCHINARIO].timers.set_start("elettro", int(tempo_elettro_num.get()))

    # Richiama la funzione ogni secondo per aggiornare il tempo trascorso
    frame_container_time.after(UPDATE_TIMER_DELAY, update_elapsed_time_elettro)  # Richiama se stesso ogni secondo

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
        tempo_elettro_num.place(x=mapper._map_item_x(10, ELETTRO_TIME_FRAME_WIDTH), y=mapper._map_item_y(43, ELETTRO_TIME_FRAME_HEIGHT_MANUAL))
        elettro_time_label.configure(text="Tempo di elettroerosione(min)")
        tempo_elettro_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("elettro").split(":")[0])
        #timer_manager.get_elapsed_time(MACCHINARIO, "elettro").split(":")[0])

# Aggiungi una callback per aggiornare i pulsanti quando lo stato del checkbox cambia
elettro_time_checkbox.configure(command=elettro_toggle_buttons)

# Chiamata iniziale per impostare lo stato iniziale dei pulsanti
elettro_toggle_buttons()


#PEZZI FRAME
N_PEZZI_FRAME_WIDTH = 210
N_PEZZI_FRAME_HEIGHT = 100
frame_n_pezzi = ctk.CTkFrame(
    master=home_page, 
    width=mapper._map_frame_x(N_PEZZI_FRAME_WIDTH), 
    height=mapper._map_frame_y(N_PEZZI_FRAME_HEIGHT)
    )

pezzi_select_num = CTkSpinbox(
    master=frame_n_pezzi, bg_color=[
        'gray86', 'gray17'], 
        button_width = 50,
        width=mapper._map_item_x(76, N_PEZZI_FRAME_WIDTH),
        height=mapper._map_item_y(44, N_PEZZI_FRAME_HEIGHT),
        value=0, 
        fg_color=['gray81', 'gray20'],
        command= lambda: machine_data.machines[MACCHINARIO].prod_data.set_prod_data("pezzi", int(pezzi_select_num.get()))
        )
pezzi_select_num.place(x=mapper._map_item_x(11, N_PEZZI_FRAME_WIDTH), y=mapper._map_item_y(44, N_PEZZI_FRAME_HEIGHT))

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

frame_draw_commessa = ctk.CTkFrame(
    master=home_page,
    width=mapper._map_frame_x(N_DRAW_FRAME_WIDTH), 
    height=mapper._map_frame_y(N_DRAW_FRAME_HEIGHT)
    )

frame_n_draw = ctk.CTkFrame(master=frame_draw_commessa)
frame_n_draw_label_auto_button = ctk.CTkFrame(master=frame_n_draw)
frame_tendina_pdf = ctk.CTkFrame(master=frame_n_draw)
frame_commessa = ctk.CTkFrame(master=frame_draw_commessa)

frame_draw_commessa.rowconfigure(0, weight= 2)
frame_draw_commessa.columnconfigure(0, weight= 2)

draw_mode_checkbox = ctk.CTkCheckBox(
    master=frame_n_draw_label_auto_button, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
    )

# Carica la configurazione dal file .conf
checkbox_auto = load_config("draw_mode_checkbox")
print("checkbox_auto: " + str(checkbox_auto))

# Imposta lo stato di spunta del checkbox in base al valore caricato
if(checkbox_auto):
    draw_mode_checkbox.select()
    pdf_file_list = get_pdf_files_in_directory(directory_path)
elif(not checkbox_auto):
    draw_mode_checkbox.deselect()
else:
    print("Conf not found")

draw_num_label = ctk.CTkLabel(
    master=frame_n_draw_label_auto_button, 
    bg_color=['gray92', 'gray14'], 
    text="Numero disegno"
    )

draw_num_entry = ctk.CTkEntry(
    master=frame_tendina_pdf, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

commessa_num_label = ctk.CTkLabel(
    master=frame_commessa,
    bg_color=['gray92', 'gray14'], 
    text="Commessa"
    )

commessa_num_entry = ctk.CTkEntry(
    master=frame_commessa, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

frame_n_draw.grid(                  row= 0, column= 0, padx= 5, pady=5)
draw_num_label.grid(                row= 0, column= 0, padx= 5)#, pady=5)
draw_mode_checkbox.grid(            row= 0, column= 1, padx= 0)#, pady=5)
frame_n_draw_label_auto_button.grid(row= 0, column= 0, padx= 5, pady=5)
frame_commessa.grid(                row= 2, column= 0, padx= 5, pady=5)
commessa_num_label.grid(            row= 0, column= 0, padx= 5)#, pady=5)
commessa_num_entry.grid(            row= 1, column= 0, padx= 5)#, pady=5)

def on_select_draw():
    print(f'Numero disegno selezionato: {menu_tendina_disegni.get()}')
    machine_data.machines[MACCHINARIO].prod_data.set_prod_data("numero_disegno_tendina", menu_tendina_disegni.get())
    print(f'Numero disegno selezionato: {machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_tendina")}')
    machine_data.machines[MACCHINARIO].prod_data.print_prod_data("numero_disegno_tendina")

menu_tendina_disegni = ctk.CTkOptionMenu(
    master=frame_tendina_pdf, 
    values=[], 
    bg_color=['gray86', 'gray17'],
    width= 140,# + 10,
    height= 28 + 10,
    dropdown_font = ctk.CTkFont(
        'Roboto',
        size=16),
    hover=False,
    command= lambda value: on_select_draw()
    )

menu_tendina_disegni.configure(values=pdf_file_list)
menu_tendina_disegni.set("Sel. num. disegno")

draw_open_pdf_button = ctk.CTkButton(
    master=frame_tendina_pdf, 
    width= 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14'],
    text="Apri",
    command= lambda: open_pdf()
    )

def draw_number_frame_visual_mode(operation):
    if operation == 'auto':
        draw_num_entry.grid_forget()
        menu_tendina_disegni.grid(row=1, column=0, padx= 5, pady= 5)
        draw_open_pdf_button.grid(row=1, column=1, padx= 0, pady= 5)
        frame_tendina_pdf.grid(row=1, column=0, padx= 5, pady= 5)

    elif operation == 'manual':
        frame_tendina_pdf.grid(row=1, column=0, padx= 5, pady= 5)
        menu_tendina_disegni.grid_forget()
        draw_open_pdf_button.grid_forget()
        draw_num_entry.grid(row=1, column=0, padx= 5, pady= 5)

if draw_mode_checkbox.get():
    draw_number_frame_visual_mode('auto')
else:
    draw_number_frame_visual_mode('manual')

#LAVORAZIONE FRAME
LAVORAZIONE_FRAME_WIDTH = 400
LAVORAZIONE_FRAME_HEIGHT = 40
frame_lavorazione = ctk.CTkFrame(master=home_page, 
                                           width=mapper._map_frame_x(LAVORAZIONE_FRAME_WIDTH), 
                                           height=mapper._map_frame_y(LAVORAZIONE_FRAME_HEIGHT)
                                           )
#frame_lavorazione.place(x=191, y=73)

tornitura_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="tornitura")
tornitura_checkbox.place(x=mapper._map_item_x(115, LAVORAZIONE_FRAME_WIDTH), y=mapper._map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

fresatura_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="fresatura")
fresatura_checkbox.place(x=mapper._map_item_x(220, LAVORAZIONE_FRAME_WIDTH), y=mapper._map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

elettro_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray92', 'gray14'], width=72, text="elettro")
elettro_checkbox.place(x=mapper._map_item_x(320, LAVORAZIONE_FRAME_WIDTH), y=mapper._map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

taglio_checkbox = ctk.CTkCheckBox(master=frame_lavorazione, bg_color=['gray86', 'gray17'], text="taglio")
taglio_checkbox.place(x=mapper._map_item_x(13, LAVORAZIONE_FRAME_WIDTH), y=mapper._map_item_y(8, LAVORAZIONE_FRAME_HEIGHT))

def create_database(username):
    try:
        # Connessione al database principale
        DBMan.connect()

        # Verifica se il database esiste già
        existing_databases = DBMan.fetch_data("SELECT datname FROM pg_catalog.pg_database WHERE datname = %s", (f"{username}_user",))
        if not existing_databases:
            # Il database non esiste, quindi lo creiamo
            new_db_name = f"{username}_user"
            DBMan.execute_query(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db_name)), commit=True)
            print(f"Database '{new_db_name}' creato con successo.")
        else:
            new_db_name = existing_databases[0][0]

        # Disconnettiamo dal database principale
        DBMan.disconnect()

        return new_db_name
    except Exception as e:
        print(f"Errore durante la creazione del database per '{username}': {e}")
        return None

def perform_registration():

    username = user_singup_entry.get()
    password = passwd_singup_entry.get()
    confirm_password = passwd_repeat_singup_entry.get()
    #print(username + ", " + password + ", " + confirm_password)

    if password != confirm_password:
        CTkMessagebox(
            master= login_page,
            title="Errore di registrazione", 
            message="Le password non corrispondono!",
            icon="warning"
            )
        return False
    
    try:
        # Connessione al database PostgreSQL
        DBMan.connect(var.LOGGED_USER)  # Connessione al database principale

        # Verifica se il database esiste già
        new_db_name = create_database(username)
        print("new_db_name: " + new_db_name)
        
        # Connessione al nuovo database creato
        DBMan.disconnect()  # Disconnetti dal database principale
        DBMan.connect(new_db_name)  # Connessione al nuovo database creato

        # Creazione della tabella per memorizzare la password
        DBMan.execute_query("""
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
        DBMan.execute_query("INSERT INTO password (password_hash) VALUES (%s)", (password_hash,))

        # Applica le modifiche
        DBMan.disconnect()  # Disconnetti dal nuovo database creato

        switch_page(home_page)
        return True

    except Exception as e:
        #messagebox.showerror("Errore di registrazione", f"Errore durante l'inserimento dell'utente nel database: {e}")
        CTkMessagebox(
            master= singup_page,
            title="Errore di registrazione", 
            message=f"Errore durante l'inserimento dell'utente nel database: {e}",
            icon="warning"
            )
        return False

            
progressbar = ctk.CTkProgressBar(master=home_page)
#progressbar.pack(padx=20, pady=10)

def check_db_connection():
    global DB_STATE
    start_time = time.time()
    while time.time() - start_time < 10:
        if DBMan.test_connection():
            DB_STATE = "Connesso"
            update_db_user_state()
            #print("Connessione riuscita")
            return True  # Restituisci True se la connessione è riuscita
        else:
            DB_STATE = 'Errore di connessione'
            #print("Errore di connessione")
            update_db_user_state()
            return False  # Restituisci False se c'è stato un errore di connessione

# Chiamata alla funzione per verificare la connessione al database all'avvio
check_db_connection()

def update_selected_checkbox(checkbox):
    selected_checkboxes = machine_data.machines[MACCHINARIO].prod_data.get_selected_checkboxes()
    selected_checkboxes.split(',')

    if checkbox in selected_checkboxes:
        selected_checkboxes.remove(checkbox)
    else:
        selected_checkboxes.append(checkbox)

    machine_data.machines[MACCHINARIO].prod_data.set_selected_checkboxes(selected_checkboxes)

def update_selected_text():
    selected_checkboxes = machine_data.machines[MACCHINARIO].prod_data.get_selected_checkboxes()
    selected_checkboxes.split(',')
    
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
        global pdf_file_list
        chosen_directory = directory_entry.get()
        if chosen_directory:
            save_config("draw_directory", chosen_directory)
            pdf_file_list = get_pdf_files_in_directory(chosen_directory)
            menu_tendina_disegni.configure(values=pdf_file_list)
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

#SING-UP FRAME
SINGUP_FRAME_WIDTH = 190 + 15
SINGUP_FRAME_HEIGHT = 263 + 40

# Creazione del frame di registrazione
frame_singup = ctk.CTkFrame(
    master=singup_page, 
    width=mapper._map_frame_x(SINGUP_FRAME_WIDTH), 
    height=mapper._map_frame_y(SINGUP_FRAME_HEIGHT) 
)

# Label per il titolo "Registrazione"
registration_title_label = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Registrazione",
    font=("Helvetica", 16, "bold")
)
registration_title_label.place(x=mapper._map_item_x(50, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(2, SINGUP_FRAME_HEIGHT))

# Label e Entry per l'username
user_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Username"
)
user_label_singup.place(x=mapper._map_item_x(60, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(30, SINGUP_FRAME_HEIGHT))

user_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
print("user_singup_entry: " + str(user_singup_entry))
user_singup_entry.place(x=mapper._map_item_x(24, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(50, SINGUP_FRAME_HEIGHT))

# Label e Entry per la password
passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Password"
)
passwd_label_singup.place(x=mapper._map_item_x(60, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(90, SINGUP_FRAME_HEIGHT))

passwd_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
passwd_singup_entry.configure(show='*')
passwd_singup_entry.place(x=mapper._map_item_x(24, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(110, SINGUP_FRAME_HEIGHT))

# Label e Entry per la ripetizione della password
repeat_passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Ripeti password"
)
repeat_passwd_label_singup.place(x=mapper._map_item_x(45, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(150, SINGUP_FRAME_HEIGHT))

passwd_repeat_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
)
passwd_repeat_singup_entry.configure(show='*')
passwd_repeat_singup_entry.place(x=mapper._map_item_x(24, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(170, SINGUP_FRAME_HEIGHT))

# Pulsante di registrazione
singup_button = ctk.CTkButton(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Registrati",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: perform_registration()
)
singup_button.place(x=mapper._map_item_x(24, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(210, SINGUP_FRAME_HEIGHT))

# Pulsante per tornare indietro
back_button_singup = ctk.CTkButton(
    master=frame_singup,
    bg_color=['gray92','gray14'],
    text="Indietro",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: switch_page(home_page)
    )
back_button_singup.place(x=mapper._map_item_x(24, SINGUP_FRAME_WIDTH), y=mapper._map_item_y(250, SINGUP_FRAME_HEIGHT))

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
    width=mapper._map_frame_x(SETTINGS_FRAME_WIDTH), 
    height=mapper._map_frame_y(SETTINGS_FRAME_HEIGHT),
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
    width=mapper._map_item_x(76, SETTINGS_FRAME_WIDTH),
    height=mapper._map_item_y(44, SETTINGS_FRAME_HEIGHT),
    value=var.KEYWIDTH, 
    fg_color=['gray81', 'gray20']
)
num_board_select_num.grid(row=8, column=0)  

# Colleghi la funzione di aggiornamento alla variazione del valore del CTkSpinbox
num_board_select_num.configure(command=lambda: update_num_board(num_board_select_num.get()))

# Creazione del frame per la gui Scale
frame_gui_scale = ctk.CTkFrame(master=frame_settings) 

# Label per la GUISCALE Scale
gui_scale_scale_label_singup = ctk.CTkLabel(
    master=frame_gui_scale, 
    bg_color=['gray92', 'gray14'], 
    text="GUI scale size"
)

# CTkSpinbox per la selezione della GUI Scale
gui_scale_select_num = CTkSpinbox(
    master=frame_gui_scale, 
    bg_color=['gray86', 'gray17'],
    width=mapper._map_item_x(76, SETTINGS_FRAME_WIDTH),
    height=mapper._map_item_y(44, SETTINGS_FRAME_HEIGHT),
    value=var.GUI_SCALE, 
    fg_color=['gray81', 'gray20']
)

frame_gui_scale.grid(               row=6, column=0, padx=10, pady=10)
gui_scale_scale_label_singup.grid(  row=0, column=0)
gui_scale_select_num.grid(          row=1, column=0)

gui_scale_select_num.configure(command=lambda: update_gui_scale(gui_scale_select_num.get()))

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
color_label.grid(row=8, column=0)

# OptionMenu per selezionare il colore
color_optionemenu = ctk.CTkOptionMenu(
    frame_appearance, 
    values=["green", "blue"],
    command= change_color_event
)
default_color_text = "Seleziona un colore"
color_optionemenu.set(default_color_text)
color_optionemenu.grid(row=9, column=0)

# Pulsante per le impostazioni del database
db_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impostazioni DB",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_db_config_dialog()
)
db_settings.grid(row=1, column=0)

# Pulsante per le impostazioni dei disegni
draw_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impostazioni Disegni",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_draw_config_dialog()
)
draw_settings.grid(row=2, column=0)

run_update = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Applica aggiornamento",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_draw_config_dialog()
)
run_update.grid(row=3, column=0)

# Pulsante per le impostazioni dei disegni
update_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impost. Update",
    width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_update_config_dialog()
)
update_settings.grid(row=4, column=0)

#FRAME NOTE
N_NOTE_FRAME_WIDTH = 210
N_NOTE_FRAME_HEIGHT = 100

frame_note = ctk.CTkFrame(
    master=home_page,
    width=mapper._map_frame_x(N_NOTE_FRAME_WIDTH), 
    height=mapper._map_frame_y(N_NOTE_FRAME_HEIGHT)
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

note_num_entry = ctk.CTkEntry(
    master=frame_note, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

note_num_label.grid(row= 0, column= 0, padx= 10, pady= 10)#place(relx = 0.09, rely=0.11)
note_num_entry.grid(row= 1, columnspan= 2, padx= 10, pady= 10)#place(relx = 0.09, rely=0.4)

#FRAME COMMESSA
N_NOTE_FRAME_WIDTH = 210
N_NOTE_FRAME_HEIGHT = 100

frame_commessa = ctk.CTkFrame(
    master=home_page,
    width=mapper._map_frame_x(N_NOTE_FRAME_WIDTH), 
    height=mapper._map_frame_y(N_NOTE_FRAME_HEIGHT)
    )

commessa_mode_checkbox = ctk.CTkCheckBox(
    master=frame_commessa, 
    bg_color=['gray86', 'gray17'], 
    text="Auto"
    )

def get_user_databases(db_config):
    try:
        start_time = time.time()  # Memorizza il tempo di inizio del tentativo di connessione

        while time.time() - start_time < 10:  # Continua fino a quando non sono passati 10 secondi
            # Ottieni i nomi dei database presenti sul server PostgreSQL
            databases = DBMan.fetch_data("SELECT datname FROM pg_catalog.pg_database", autoconnect=var.LOGGED_USER)
            #print(f"Lista database: {databases}")

            # Filtra solo i nomi dei database che terminano con "_user"
            user_databases = [db[0].rstrip("_user") for db in databases if db[0].endswith("_user")]
            print(f"Lista database utenti: {user_databases}")

            return user_databases

    except Exception as e:
        CTkMessagebox(
                master= login_page,
                title="Errore", 
                message="Errore recupero lista utenti",
                icon="warning"
                )
        print(f"Errore durante il recupero dei database degli utenti: {e}")
        return ["Errore1", "Errore2", "Errore3"]


def order_to_db(TABLE_NAME):

    if draw_mode_checkbox.get():
        numero_disegno = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_tendina")
    else:
        numero_disegno = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_entry")
    
    tipo_lavorazione = ''
    machine_data.machines[MACCHINARIO].dates.set_date("fine", time.strftime('%Y-%m-%d %H:%M:%S'))
    orario_fine = machine_data.machines[MACCHINARIO].dates.get_date("fine")
    tempo_setup = int(tempo_setup_num.get())
    tempo_taglio = int(tempo_taglio_num.get())
    tempo_tornitura = int(tempo_tornitura_num.get())
    tempo_fresatura = int(tempo_fresatura_num.get())
    tempo_elettroerosione = int(tempo_elettro_num.get())
    numero_pezzi = int(pezzi_select_num.get())
    orario_inizio = machine_data.machines[MACCHINARIO].dates.get_date("inizio") 
    print(f'\norario_inizio: {orario_inizio}')
    note_lavorazione = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("note_lavorazione")
    print(f'\nnote_lavorazione: {note_lavorazione}')
    #note_num_entry.get()
    commessa_lavorazione = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("commessa_lavorazione")
    print(f'\ncommessa_lavorazione: {commessa_lavorazione}')
    #commessa_num_entry.get()

    if draw_mode_checkbox.get():
        numero_disegno = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_tendina")
        #str(menu_tendina_disegni.get())
    else:
        numero_disegno = machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_entry")
        #str(draw_num_entry.get())

    errore_riempimento = False

    start_date = machine_data.machines[MACCHINARIO].dates.get_date("inizio")
    print(f'\nstart_date: {start_date}')
    print(f'orario_inizio: {orario_inizio}')
    print(f'orario_fine: {orario_fine}')

    # Verifica se tutti i campi sono stati compilati e se il numero di pezzi è diverso da zero
    if not all([orario_inizio, orario_fine, tempo_setup]) or numero_pezzi == 0 or numero_disegno == '' or commessa_lavorazione == '':
        print("errore 1")
        errore_riempimento = True
    
    if checkBoxMan.get_checkbox_state('taglio', MACCHINARIO) == True and tempo_taglio == 0:
        print("errore 2")
        errore_riempimento = True
        
    if checkBoxMan.get_checkbox_state('tornitura', MACCHINARIO) == True and tempo_tornitura == 0:
        print("errore 3")
        errore_riempimento = True

    if checkBoxMan.get_checkbox_state('fresatura', MACCHINARIO) == True and tempo_fresatura == 0:
        print("errore 4")
        errore_riempimento = True

    if checkBoxMan.get_checkbox_state('elettro', MACCHINARIO) == True and tempo_elettroerosione == 0:
        print("errore 5")
        errore_riempimento = True

    if(errore_riempimento):
        CTkMessagebox(title="Errore", 
                  message="Riempi tutti i campi prima di continuare!",
                  icon="warning"
                  )
        return

    #orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, tempo_ciclo, numero_pezzi
    user_choose = ask_question_confirm_order(orario_fine, tempo_setup, tempo_taglio, tempo_tornitura, 
                               tempo_fresatura, tempo_elettroerosione, orario_inizio, 
                               numero_pezzi, numero_disegno, commessa_lavorazione, note_lavorazione)
    
    if(not user_choose):
        CTkMessagebox(title="Errore", 
                  message="Devi accedere per confermare l'ordine!",
                  icon="warning"
                  )
        return

    if(var.LOGGED_USER != '' and var.LOGGED_USER != ''):
        db_name = var.LOGGED_USER_DB

        DBMan.connect(db_name)
        
        # Esegui la query per creare la tabella
        create_table_query = queries.CREATE_TABLE_QUERY.format(TABLE_NAME)
        result_create_table = DBMan.execute_query(create_table_query, commit=True)

        # Esegui la query per inserire dati nella tabella
        insert_query = queries.INSERT_QUERY.format(TABLE_NAME)
        result_order = DBMan.execute_query(insert_query, (orario_inizio, orario_fine, numero_disegno, commessa_lavorazione, 
                                           tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, 
                                           tempo_setup, numero_pezzi, note_lavorazione, MACCHINARIO), commit=True)    
        
        DBMan.disconnect()
        
        if result_order and result_create_table:
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

def riprendi_ordine():
    print('riprendi ordine')

def azzera_ordine():
    if not ask_question_choice("Sei sicuro di voler azzerare l'ordine?", home_page):
        return 
    machine_data.machines[MACCHINARIO].timers.reset_all_timers()
    tempo_setup_num.configure(value= 0)
    pezzi_select_num.configure(value= 0)
    tempo_taglio_num.configure(value= 0)
    tempo_fresatura_num.configure(value= 0)
    tempo_tornitura_num.configure(value= 0)
    tempo_elettro_num.configure(value= 0)
    menu_tendina_disegni.set("Sel. num. disegno")
    draw_num_entry.delete('0', 'end')
    commessa_num_entry.delete('0', 'end')
    start_time_time_elapsed_label.configure(text= 'Da impostare')
    note_num_entry.delete('0', 'end')
    machine_data.machines[MACCHINARIO].dates.set_date("inizio", None)
    
#GESTIONE ORDINE ESTERNALIZZATO

def salva_ordine():
    order_to_db('ordini_in_sospeso')

def conferma_ordine():
    order_to_db('ordini')
    
def ask_question_confirm_order(orario_fine_dt, tempo_setup, tempo_taglio, 
                               tempo_tornitura, tempo_fresatura, tempo_elettroerosione, 
                               orario_inizio, numero_pezzi, numero_disegno, commessa_lavorazione, note_lavorazione):
    # Formattazione dei dati come una tabella
    tabella = (
    f"{'INIZIO:':<20}{orario_inizio}\n"
    f"{'FINE:':<20}{orario_fine_dt}\n"
    f"{'N DISEGNO:':<20}{numero_disegno}\n"
    f"{'N COMMESSA:':<20}{commessa_lavorazione}\n"
    f"{'SETUP:':<20}{tempo_setup} m\n"
    )

    if tempo_taglio != 0:
        tabella += f"{'TAGLIO:':<20}{tempo_taglio} m\n"

    if tempo_tornitura != 0:
        tabella += f"{'TORNITURA:':<20}{tempo_tornitura} m\n"

    if tempo_fresatura != 0:
        tabella += f"{'FRESATURA:':<20}{tempo_fresatura} m\n"

    if tempo_elettroerosione != 0:
        tabella += f"{'ELETTROEROSIONE:':<20}{tempo_elettroerosione} m\n"

    tabella += (
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



#FRAME SELEZIONA MACCHINA
ORDER_MAN_FRAME_WIDTH = 400 
ORDER_MAN_FRAME_HEIGHT = 200

# Creazione del frame
frame_seleziona_macchina = ctk.CTkFrame(master=home_page)

def on_checkbox_change(checkbox_name):
    global PADX
    # Larghezza minima desiderata tra i frame
    print(f"checkbox_name: {checkbox_name}")

    if checkbox_name == "taglio":
        if taglio_checkbox.get():
            checkBoxMan.set_checkbox_state('taglio', True, MACCHINARIO)
            frame_taglio_time.grid(row=0, column=0, padx=PADX)
        else:
            checkBoxMan.set_checkbox_state('taglio', False, MACCHINARIO)
            frame_taglio_time.grid_remove()
    elif checkbox_name == "tornitura":
        if tornitura_checkbox.get():
            checkBoxMan.set_checkbox_state('tornitura', True, MACCHINARIO)
            frame_tornitura_time.grid(row=0, column=1, padx=PADX)
        else:
            checkBoxMan.set_checkbox_state('tornitura', False, MACCHINARIO)
            frame_tornitura_time.grid_remove()
    elif checkbox_name == "fresatura":
        if fresatura_checkbox.get():
            checkBoxMan.set_checkbox_state('fresatura', True, MACCHINARIO)
            frame_fresatura_time.grid(row=0, column=2, padx=PADX)
        else:
            checkBoxMan.set_checkbox_state('fresatura', False, MACCHINARIO)
            frame_fresatura_time.grid_remove()
    elif checkbox_name == "elettro":
        if elettro_checkbox.get():
            checkBoxMan.set_checkbox_state('elettro', True, MACCHINARIO)
            frame_elettro_time.grid(row=0, column=3, padx=10)
        else:
            checkBoxMan.set_checkbox_state('elettro', False, MACCHINARIO)
            frame_elettro_time.grid_remove()

    elif checkbox_name == "draw_mode":
        draw_check = draw_mode_checkbox.get()
        
        if draw_check:
            draw_number_frame_visual_mode('auto')
        else:
            draw_number_frame_visual_mode('manual')

    check_number = checkBoxMan.count_true(MACCHINARIO)
    print(f'check_number: {check_number}')

    if(check_number > 0):
        print(f'1')
        width_container_time_frame = 222.5 * check_number
        print(f'width_container_time_frame: {width_container_time_frame}')
        if(width_container_time_frame < root_width):
            print(f'2')
            frame_container_time.place_forget()
            frame_container_time.configure(width = 222.5 * check_number)
        else:
            print(f'3')
            frame_container_time.place_forget()
            frame_container_time.configure(width = root_width - 250)
        frame_container_time.place(relx=0.50, rely=0.19, anchor='n')
    else:
        print(f'4')
        frame_container_time.place_forget()

def update_widgets_data():
    start_time = machine_data.machines[MACCHINARIO].dates.get_date("inizio")
    print(f"start_time: {start_time}")
    if(start_time == None):
        start_time_time_elapsed_label.configure(text= "Da impostare")
    else:
        start_time_time_elapsed_label.configure(text= machine_data.machines[MACCHINARIO].dates.get_date("inizio"))#.strftime("%Y-%m-%d %H:%M:%S"))
    #tempo setup
    tempo_setup_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("setup").split(":")[0])
    #tempo taglio
    tempo_taglio_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("taglio").split(":")[0])
    #tempo tornitura
    tempo_tornitura_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("tornitura").split(":")[0])
    #tempo fresatura
    tempo_fresatura_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("fresatura").split(":")[0])
    #tempo elettroerosione
    tempo_elettro_num.configure(value= machine_data.machines[MACCHINARIO].timers.get_elapsed_time("elettro").split(":")[0])

    #disegno
    print(f'draw_mode_checkbox.get(): {draw_mode_checkbox.get()}')
    if draw_mode_checkbox.get():
        print(f': {machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_tendina")}')
        menu_tendina_disegni.set(machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_tendina"))
    else:
        draw_num_entry.delete('0', 'end')
        draw_num_entry.insert('0', machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_entry"))
    
    #commessa
    commessa_num_entry.delete('0', 'end')
    commessa_num_entry.insert('0', machine_data.machines[MACCHINARIO].prod_data.get_prod_data("commessa_lavorazione"))
    
    #note
    note_num_entry.delete('0', 'end')
    note_num_entry.insert('0', machine_data.machines[MACCHINARIO].prod_data.get_prod_data("note_lavorazione"))
    
    #pezzi
    value= machine_data.machines[MACCHINARIO].prod_data.get_prod_data("pezzi")
    pezzi_select_num.configure(value= value)
    
    #checkboxes
    checkboxes = checkBoxMan.get_checkbox_states(MACCHINARIO)
    #checkboxes = checkboxes.split(', ')
    print(f'checkboxes: {checkboxes}')

    if  checkBoxMan.get_checkbox_state('taglio', MACCHINARIO):  #'taglio' in checkboxes:
        print('taglio in checkboxes')
        taglio_checkbox.select()
    else:
        print('taglio not in checkboxes')
        taglio_checkbox.deselect()
        
    if checkBoxMan.get_checkbox_state('tornitura', MACCHINARIO):  #'tornitura' in checkboxes:
        print('tornitura in checkboxes')
        tornitura_checkbox.select()
    else:
        print('tornitura not in checkboxes')
        tornitura_checkbox.deselect()

    if checkBoxMan.get_checkbox_state('fresatura', MACCHINARIO):  #'fresatura' in checkboxes:
        print('fresatura in checkboxes')
        fresatura_checkbox.select()
    else:
        print('fresatura not in checkboxes')
        fresatura_checkbox.deselect()

    if checkBoxMan.get_checkbox_state('elettro', MACCHINARIO):  #'elettro' in checkboxes:
        print('elettroerosione in checkboxes')
        elettro_checkbox.select()
    else:
        print('elettroerosione not in checkboxes')
        elettro_checkbox.deselect()
    
    on_checkbox_change('taglio')
    on_checkbox_change('tornitura')
    on_checkbox_change('fresatura')
    on_checkbox_change('elettro')

def change_machine(machine, button):
    global MACCHINARIO
    MACCHINARIO = machine
    print(f"Macchina selezionata: {machine}")

    # Disabilita il pulsante corrente e abilita gli altri
    for button in buttons:
        if button.cget('text') == machine:
            button.configure(state="disabled")
        else:
            button.configure(state="normal")
    update_widgets_data()
# Calcola il numero di colonne basato sul numero di macchine
num_buttons = len(machines)
num_rows = 1
num_columns = (num_buttons + num_rows - 1) // num_rows

buttons = []

for i, machine in enumerate(machines):
    row =  i // num_columns
    column = i % num_columns
    button = ctk.CTkButton(master=frame_seleziona_macchina, text=machine, width= 20, command=lambda m=machine: change_machine(m, button))
    button.grid(row=row, column=column, padx=5, pady=5)
    button.configure(command=lambda m=machine, b=button: change_machine(m, b))  # Passa il pulsante alla funzione
    buttons.append(button)  # Aggiungi il pulsante alla lista dei pulsanti

#print(f'buttons: {buttons}')

change_machine(machines[0], buttons[0])  # Imposta la prima macchina come selezionata di default

#FRAME GESTIONE ORDINE
ORDER_MAN_FRAME_WIDTH = 400 
ORDER_MAN_FRAME_HEIGHT = 200

#PULSANTI GESTIONE ORDINE
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
    width=mapper._map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=mapper._map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: conferma_ordine()
)

# Posizionamento del frame
button_conferma_ordine.grid(row=0, column=0, padx=PADX_FRAME_GESTIONE_ORDINI, pady=PADY_FRAME_GESTIONE_ORDINI)

button_storico_ordini = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Storico ordini",
    width=mapper._map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=mapper._map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: modifica_ordine(switch_page, home_page, modify_order_page, ctk, mapper, DBMan)
)

# Posizionamento del frame
button_storico_ordini.grid(row=0, column=2, padx=PADX_FRAME_GESTIONE_ORDINI, pady=PADY_FRAME_GESTIONE_ORDINI)

button_reset_ordine = ctk.CTkButton(
    master=frame_gestione_ordine, 
    bg_color=['gray92', 'gray14'], 
    text="Azzera ordine",
    width=mapper._map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
    height=mapper._map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
    command=lambda: azzera_ordine()
)

# Posizionamento del frame
button_reset_ordine.grid(row=0, column=3, padx=PADX_FRAME_GESTIONE_ORDINI, pady=PADY_FRAME_GESTIONE_ORDINI)

pezzi_label = ctk.CTkLabel(master=frame_n_pezzi, bg_color=['gray86', 'gray17'], text="N. Pezzi")
pezzi_label.place(x=mapper._map_item_x(55, N_PEZZI_FRAME_WIDTH), y=mapper._map_item_y(8, N_PEZZI_FRAME_HEIGHT))

users_list = get_user_databases(db_config) #["Utente1", "Utente2", "Utente3"]

root.resizable(True, True)  # La finestra sarà ridimensionabile sia in larghezza che in altezza

def on_window_resize(event):
    global root_height
    global root_width

    selected_checkbox_number = checkBoxMan.count_true(MACCHINARIO)
    # Aggiorna i valori dei widget in base alle dimensioni attuali della finestra
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    if frame_container_time.winfo_exists():
        width_container_time_frame = 222.5 * selected_checkbox_number
        if(width_container_time_frame < root_width - 150 or width_container_time_frame > 800):
            frame_container_time.place_forget()
            frame_container_time.configure(width = 222.5 * selected_checkbox_number)
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

    if frame_draw_commessa.winfo_exists():
        frame_draw_commessa.place(relx=0.50, rely=0.4, anchor='n')

    if frame_gestione_ordine.winfo_exists():
        frame_gestione_ordine.place(relx=0.5, rely=0.9, anchor='s')

    if frame_seleziona_macchina.winfo_exists():
        frame_seleziona_macchina.place(x=0, rely=0.99, anchor='sw')

    if frame_note.winfo_exists():
        frame_note.place(relx=0.999, rely=0.3, anchor='e')

#NUMPADS
entry_list = [passwd_singup_entry, passwd_repeat_singup_entry, tempo_setup_num.entry, 
              tempo_taglio_num.entry, tempo_fresatura_num.entry, tempo_tornitura_num.entry, 
              tempo_elettro_num.entry, pezzi_select_num.entry]

numpads = numPads.generate_numpads(entry_list, keyheight= var.KEYHEIGHT, keywidth= var.KEYWIDTH)

def on_draw_entry_change(event):
    machine_data.machines[MACCHINARIO].prod_data.set_prod_data("numero_disegno_entry", draw_num_entry.get())
    print(f'machine_data.machines[{MACCHINARIO}].prod_data.get_set_prod_data("numero_disegno_entry"): {machine_data.machines[MACCHINARIO].prod_data.get_prod_data("numero_disegno_entry")}')

def on_commessa_entry_change(event):
    machine_data.machines[MACCHINARIO].prod_data.set_prod_data("commessa_lavorazione", commessa_num_entry.get())
    print(f'machine_data.machines[{MACCHINARIO}].prod_data.get_set_prod_data("commessa_lavorazione"): {machine_data.machines[MACCHINARIO].prod_data.get_prod_data("commessa_lavorazione")}')

def on_note_entry_change(event):
    machine_data.machines[MACCHINARIO].prod_data.set_prod_data("note_lavorazione", note_num_entry.get())
    print(f'machine_data.machines[{MACCHINARIO}].prod_data.get_set_prod_data("note_lavorazione"): {machine_data.machines[MACCHINARIO].prod_data.get_prod_data("note_lavorazione")}')

# Associa la funzione on_checkbox_change a ciascun checkbox
tornitura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("tornitura"))
fresatura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("fresatura"))
elettro_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("elettro"))
taglio_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("taglio"))

draw_mode_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("draw_mode"))
draw_num_entry.bind("<KeyRelease>", on_draw_entry_change)
commessa_num_entry.bind("<KeyRelease>", on_commessa_entry_change)
note_num_entry.bind("<KeyRelease>", on_note_entry_change)

def schedule_check():
    time_check = 30000
    # Esegui il controllo e poi pianifica il prossimo controllo
    state = check_db_connection()
    if state and var.LOGGED_USER != '':
        time_check = 30000
    else:
        time_check = 1000
    root.after(time_check, schedule_check)  # 5000 millisecondi = 5 secondi

schedule_check()

root.bind("<Configure>", on_window_resize)

root.mainloop()