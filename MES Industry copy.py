import customtkinter as ctk
import tkinter as tk
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
import ctypes
from libs import CTkPopupKeyboard
import tkinter as tk

ORIGINAL_WIDTH =  800
ORIGINAL_HEIGHT = 500

LOGGED_USER = ''
LOGGED_USER_DB = ''
DB_STATE = 'Non connesso'

selected_checkbox = None
selected_checkbox_text = ''

root_width = ORIGINAL_WIDTH
root_height = ORIGINAL_HEIGHT

def load_config(conf_item):
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
            #if "gui_scale" in config_data:
            #    return config_data["gui_scale"]
            if conf_item in config_data:
                return config_data[conf_item]
            else:
                print("Conf not found!")
                return 0
    except FileNotFoundError:
        # Se il file di configurazione non esiste, ritorna None
        pass
    return 0

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
    'password': load_config('pg_passwd')  #'SphDbProduzione'
}

def update_gui_scale(new_value):
    global GUI_SCALE
    GUI_SCALE = new_value
    save_config("gui_scale", GUI_SCALE)

def update_color(new_value):
    global COLOR
    COLOR = new_value
    save_config("color", COLOR)
    ctk.set_default_color_theme(load_config("color"))

THEME = load_config("theme")
GUI_SCALE = load_config("gui_scale")
COLOR = load_config("color")


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
        print("value_frame_x: " + str(value) + "---> " + str(value_adapted))
        return value_adapted
    else:
        return value

def _map_frame_y(value):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, value, 0, (value + GUI_SCALE)))
        print("value_frame_y: " + str(value) + "---> " + str(value_adapted) + "")
        return value_adapted
    else:
        return value
    
def _map_item_x(value, frame_dim_x):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, frame_dim_x, 0, (frame_dim_x + GUI_SCALE)))
        print("value_item_x: " + str(value) + "---> " + str(value_adapted))
        return value_adapted
    else:
        return value

def _map_item_y(value, frame_dim_y):
    global GUI_SCALE
    if(GUI_SCALE != 0):
        value_adapted = int(_map(value, 0, frame_dim_y, 0, (frame_dim_y + GUI_SCALE)))
        print("value_item_y: " + str(value) + "---> " + str(value_adapted) + "")
        return value_adapted
    else:
        return value


def switch_page(page):
    pages = [home_page, singup_page, login_page]
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
singup_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
login_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
confirm_order_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)

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
        Image.open('libs\gear_icon.png'),
        size=(20,20)),
        command=lambda: switch_page(singup_page))
setting_button.place(x=_map_item_x(64, LOG_SET_FRAME_WIDTH), y=_map_item_y(4, LOG_SET_FRAME_HEIGHT))

#FRAME SETUP TIME 
SETUP_TIME_FRAME_WIDTH = 210
SETUP_TIME_FRAME_HEIGHT = 100

#GENERAZIONE FRAME
frame_setup_time = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(SETUP_TIME_FRAME_WIDTH), 
    height=_map_frame_y(SETUP_TIME_FRAME_HEIGHT)
    )

#GENERAZIONE LABEL
tempo_setup_label = ctk.CTkLabel(
    master=frame_setup_time, bg_color=[
        'gray86', 'gray17'], text="Tempo di setup (min)")
tempo_setup_label.place(x=_map_item_x(18, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(6, SETUP_TIME_FRAME_HEIGHT))

#GENERAZIONE SELEZIONA NUMERO
tempo_setup_num = CTkSpinbox(
    master=frame_setup_time, 
    bg_color=['gray86', 'gray17'],
    button_width = 50,
    width=_map_item_x(76, SETUP_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, SETUP_TIME_FRAME_HEIGHT), 
    value=0, 
    fg_color=['gray81', 'gray20']
    )
tempo_setup_num.place(x=_map_item_x(10, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(43, SETUP_TIME_FRAME_HEIGHT))

# FRAME TIMES CONTAINER
CONTAINER_TIME_FRAME_WIDTH = 890
CONTAINER_TIME_FRAME_HEIGHT = 110

frame_container_time = ctk.CTkFrame(
    master=home_page, 
    width=CONTAINER_TIME_FRAME_WIDTH, 
    height=CONTAINER_TIME_FRAME_HEIGHT,
    
    )

#FRAME TAGLIO TIME
TAGLIO_TIME_FRAME_WIDTH = 210
TAGLIO_TIME_FRAME_HEIGHT = 100

frame_taglio_time = ctk.CTkFrame(
    master=frame_container_time,
    width=TAGLIO_TIME_FRAME_WIDTH,#_map_frame_x(TAGLIO_TIME_FRAME_WIDTH),
    height=TAGLIO_TIME_FRAME_HEIGHT#_map_frame_y(TAGLIO_TIME_FRAME_HEIGHT)
    )

frame_taglio_label = ctk.CTkLabel(
    master=frame_taglio_time, bg_color=[
        'gray86', 'gray17'], text="Tempo di taglio (min)")
frame_taglio_label.place(x=_map_item_x(18, TAGLIO_TIME_FRAME_WIDTH), y=_map_item_y(6, TAGLIO_TIME_FRAME_HEIGHT))

tempo_taglio_num = CTkSpinbox(
    master=frame_taglio_time, 
    bg_color=['gray86', 'gray17'],
    button_width = 50,
    width=_map_item_x(76, TAGLIO_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, TAGLIO_TIME_FRAME_HEIGHT), 
    value=0, 
    fg_color=['gray81', 'gray20']
    )
tempo_taglio_num.place(x=_map_item_x(10, TAGLIO_TIME_FRAME_WIDTH), y=_map_item_y(43, TAGLIO_TIME_FRAME_HEIGHT))

#FRAME TORNITURA TIME
TORNITURA_TIME_FRAME_WIDTH = 210
TORNITURA_TIME_FRAME_HEIGHT = 100

frame_tornitura_time = ctk.CTkFrame(
    master=frame_container_time,
    width=TORNITURA_TIME_FRAME_WIDTH, #_map_frame_x(TORNITURA_TIME_FRAME_WIDTH), 
    height=TORNITURA_TIME_FRAME_HEIGHT #_map_frame_y(TORNITURA_TIME_FRAME_HEIGHT)
    )

frame_tornitura_label = ctk.CTkLabel(
    master=frame_tornitura_time, bg_color=[
        'gray86', 'gray17'], text="Tempo di tornitura (min)")
frame_tornitura_label.place(x=_map_item_x(18, TORNITURA_TIME_FRAME_WIDTH), y=_map_item_y(6, TORNITURA_TIME_FRAME_HEIGHT))

tempo_tornitura_num = CTkSpinbox(
    master=frame_tornitura_time, 
    bg_color=['gray86', 'gray17'],
    button_width = 50,
    width=_map_item_x(76, TORNITURA_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, TORNITURA_TIME_FRAME_HEIGHT), 
    value=0, 
    fg_color=['gray81', 'gray20']
    )
tempo_tornitura_num.place(x=_map_item_x(10, TORNITURA_TIME_FRAME_WIDTH), y=_map_item_y(43, TORNITURA_TIME_FRAME_HEIGHT))

#FRAME FRESATURA TIME
FRESATURA_TIME_FRAME_WIDTH = 210
FRESATURA_TIME_FRAME_HEIGHT = 100

frame_fresatura_time = ctk.CTkFrame(
    master=frame_container_time,
    width=FRESATURA_TIME_FRAME_WIDTH, #_map_frame_x(FRESATURA_TIME_FRAME_WIDTH), 
    height=FRESATURA_TIME_FRAME_HEIGHT #_map_frame_y(FRESATURA_TIME_FRAME_HEIGHT)
    )

frame_fresatura_label = ctk.CTkLabel(
    master=frame_fresatura_time, bg_color=[
        'gray86', 'gray17'], text="Tempo di fresatura (min)")
frame_fresatura_label.place(x=_map_item_x(18, FRESATURA_TIME_FRAME_WIDTH), y=_map_item_y(6, FRESATURA_TIME_FRAME_HEIGHT))

tempo_fresatura_num = CTkSpinbox(
    master=frame_fresatura_time, 
    bg_color=['gray86', 'gray17'],
    button_width = 50,
    width=_map_item_x(76, FRESATURA_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, FRESATURA_TIME_FRAME_HEIGHT), 
    value=0, 
    fg_color=['gray81', 'gray20']
    )
tempo_fresatura_num.place(x=_map_item_x(10, FRESATURA_TIME_FRAME_WIDTH), y=_map_item_y(43, FRESATURA_TIME_FRAME_HEIGHT))

#FRAME ELETTRO TIME
ELETTRO_TIME_FRAME_WIDTH = 210
ELETTRO_TIME_FRAME_HEIGHT = 100

frame_elettro_time = ctk.CTkFrame(
    master=frame_container_time,
    width=ELETTRO_TIME_FRAME_WIDTH, #_map_frame_x(ELETTRO_TIME_FRAME_WIDTH), 
    height=ELETTRO_TIME_FRAME_HEIGHT #_map_frame_y(ELETTRO_TIME_FRAME_HEIGHT)
    )

frame_elettro_label = ctk.CTkLabel(
    master=frame_elettro_time, bg_color=[
        'gray86', 'gray17'], text="Tempo di elettro (min)")
frame_elettro_label.place(x=_map_item_x(18, ELETTRO_TIME_FRAME_WIDTH), y=_map_item_y(6, ELETTRO_TIME_FRAME_HEIGHT))

tempo_elettro_num = CTkSpinbox(
    master=frame_elettro_time, 
    bg_color=['gray86', 'gray17'],
    button_width = 50,
    width=_map_item_x(76, ELETTRO_TIME_FRAME_WIDTH), 
    height=_map_item_y(44, ELETTRO_TIME_FRAME_HEIGHT), 
    value=0, 
    fg_color=['gray81', 'gray20']
    )
tempo_elettro_num.place(x=_map_item_x(10, ELETTRO_TIME_FRAME_WIDTH), y=_map_item_y(43, ELETTRO_TIME_FRAME_HEIGHT))

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

#SETUP TIME FRAME
N_DRAW_FRAME_WIDTH = 180
N_DRAW_FRAME_HEIGHT = 90

frame_n_draw = ctk.CTkFrame(
    master=home_page,
    width=_map_frame_x(N_DRAW_FRAME_WIDTH), 
    height=_map_frame_y(N_DRAW_FRAME_HEIGHT)
    )

draw_num_label = ctk.CTkLabel(
    master=frame_n_draw, 
    bg_color=['gray92', 'gray14'], 
    text="Numero disegno")
draw_num_label.place(relx = 0.09, rely=0.1)#x=_map_item_x(65, N_DRAW_FRAME_WIDTH), y=_map_item_y(75, N_DRAW_FRAME_HEIGHT))

draw_num_entry = ctk.CTkEntry(
    master=frame_n_draw, 
    width= 140 + 10,
    height= 28 + 10,
    bg_color=['gray92', 'gray14']
    )

draw_num_entry.place(relx = 0.09, rely=0.4)#(x=_map_item_x(25, N_DRAW_FRAME_WIDTH), y=_map_item_y(110, N_DRAW_FRAME_HEIGHT))

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
    #username = menu_tendina_utenti.get()
    #password = passwd_login_entry.get()

    username = user_singup_entry.get()
    password = passwd_singup_entry.get()
    confirm_password = passwd_repeat_singup_entry.get()
    print(username + ", " + password + ", " + confirm_password)

    if password != confirm_password:
        #show_error_message("Errore, le password non corrispondono.", 24, 110)
        CTkMessagebox(title="Errore di registrazione", 
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
        CTkMessagebox(title="Errore di registrazione", 
                message=f"Errore durante l'inserimento dell'utente nel database: {e}",
                icon="warning"
                )
        return False

    finally:
        try:
            if conn is not None:
                conn.close()
        except:
            CTkMessagebox(title="Errore di registrazione", 
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

frame_singup = ctk.CTkFrame(
    master=singup_page, 
    width=_map_frame_x(SINGUP_FRAME_WIDTH), 
    height=_map_frame_y(SINGUP_FRAME_HEIGHT) 
    )

user_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Username")
user_label_singup.place(x=_map_item_x(60, SINGUP_FRAME_WIDTH), y=_map_item_y(2, SINGUP_FRAME_HEIGHT))

user_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
    )
print("user_singup_entry: " + str(user_singup_entry))
user_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(30, SINGUP_FRAME_HEIGHT))

passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Password",
    width= _map_item_x(0, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28, SINGUP_FRAME_HEIGHT)
    )
passwd_label_singup.place(x=_map_item_x(60, SINGUP_FRAME_WIDTH), y=_map_item_y(70, SINGUP_FRAME_HEIGHT))

passwd_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
    )
passwd_singup_entry.configure(show='*')
passwd_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(90, SINGUP_FRAME_HEIGHT))

repeat_passwd_label_singup = ctk.CTkLabel(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Ripeti password",
    width= _map_item_x(0, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28, SINGUP_FRAME_HEIGHT)
    )
repeat_passwd_label_singup.place(x=_map_item_x(45, SINGUP_FRAME_WIDTH), y=_map_item_y(130, SINGUP_FRAME_HEIGHT))

passwd_repeat_singup_entry = ctk.CTkEntry(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'],
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
    )
passwd_repeat_singup_entry.configure(show='*')
passwd_repeat_singup_entry.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(150, SINGUP_FRAME_HEIGHT))

singup_button = ctk.CTkButton(
    master=frame_singup, 
    bg_color=['gray92', 'gray14'], 
    text="Registrati",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: perform_registration()
    )
singup_button.place(x=_map_item_x(24, SINGUP_FRAME_WIDTH), y=_map_item_y(200, SINGUP_FRAME_HEIGHT))

back_button_singup = ctk.CTkButton(
    master=frame_singup,
    bg_color=['gray92','gray14'],
    text="Indietro",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: switch_page(home_page))
back_button_singup.place(x=_map_item_x(24, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(240, SETUP_TIME_FRAME_HEIGHT))

def change_appearance_mode_event(new_appearance_mode: str):
    save_config("theme", new_appearance_mode)
    ctk.set_appearance_mode(new_appearance_mode)

def change_color_event(new_color: str):
    save_config("color", new_color)
    ctk.set_default_color_theme(new_color)



#FRAME SETTINGS
SETTINGS_FRAME_WIDTH = 190 + 10
SETTINGS_FRAME_HEIGHT = 263 + 40

frame_settings = ctk.CTkFrame(
    master=singup_page, 
    width=_map_frame_x(SETTINGS_FRAME_WIDTH), 
    height=_map_frame_y(SETTINGS_FRAME_HEIGHT)                                      
    )

settings_label_singup = ctk.CTkLabel(
    master=frame_settings, 
    bg_color=['gray92', 'gray14'], 
    text="Impostazioni")
settings_label_singup.place(x=_map_item_x(60, SETTINGS_FRAME_WIDTH), y=_map_item_y(1, SETTINGS_FRAME_HEIGHT))

gui_scale_label_singup = ctk.CTkLabel(
    master=frame_settings, 
    bg_color=['gray92', 'gray14'], 
    text="GUI Scale")
gui_scale_label_singup.place(x=_map_item_x(60, SETTINGS_FRAME_WIDTH), y=_map_item_y(25, SETTINGS_FRAME_HEIGHT))

gui_scale_select_num = CTkSpinbox(
    master=frame_settings, bg_color=[
        'gray86', 'gray17'],
        width= _map_item_x(76, SETTINGS_FRAME_WIDTH),
        height= _map_item_y(44, SETTINGS_FRAME_HEIGHT),
        value=GUI_SCALE, 
        fg_color=['gray81', 'gray20'])

# Colleghi la funzione di aggiornamento alla variazione del valore del CTkSpinbox
gui_scale_select_num.configure(command=lambda: update_gui_scale(gui_scale_select_num.get()))

gui_scale_select_num.place(x=_map_item_x(24, SETTINGS_FRAME_WIDTH), y=_map_item_y(45, SETTINGS_FRAME_HEIGHT))

appearance_mode_label = ctk.CTkLabel(frame_settings, text="Tema:", anchor="w")
#appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
appearance_mode_label.place(x=_map_item_x(60, SETTINGS_FRAME_WIDTH), y=_map_item_y(100, SETTINGS_FRAME_HEIGHT))

appearance_mode_optionemenu = ctk.CTkOptionMenu(
    frame_settings, 
    values=["Light", "Dark", "System"],
    command=change_appearance_mode_event)
#appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
default_theme_text = "Seleziona un tema"
appearance_mode_optionemenu.set(default_theme_text)

appearance_mode_optionemenu.place(x=_map_item_x(24, SETTINGS_FRAME_WIDTH), y=_map_item_y(125, SETTINGS_FRAME_HEIGHT))

color_label = ctk.CTkLabel(frame_settings, text="Colore:", anchor="w")
#appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
color_label.place(x=_map_item_x(60, SETTINGS_FRAME_WIDTH), y=_map_item_y(165, SETTINGS_FRAME_HEIGHT))

# Ottieni la lista dei nomi dei colori supportati da tkinter
color_names = ["green", "blue"]

color_optionemenu = ctk.CTkOptionMenu(
    frame_settings, 
    values=color_names,
    command= change_color_event
    )

default_color_text = "Seleziona un colore"
color_optionemenu.set(default_color_text)

#color_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
color_optionemenu.place(x=_map_item_x(24, SETTINGS_FRAME_WIDTH), y=_map_item_y(190, SETTINGS_FRAME_HEIGHT))

db_settings = ctk.CTkButton(
    master=frame_settings,
    bg_color=['gray92','gray14'],
    text="Impostazioni DB",
    width= _map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
    height= _map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
    command=lambda: show_db_config_dialog()
    )

db_settings.place(x=_map_item_x(24, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(230, SETUP_TIME_FRAME_HEIGHT))

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

    users_list = get_user_databases()

    username = menu_tendina_utenti.get()  # Ottieni il valore immesso nella casella di testo dell'username
    password = passwd_login_entry.get()  # Ottieni il valore immesso nella casella di testo della password
    
    try:
        # Verifica se il nome utente selezionato è presente nel menu a tendina
        if username not in users_list:
            CTkMessagebox(title="Errore di login", 
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
            CTkMessagebox(title="Login", 
                  message="Login effettuato con successo!",
                  icon="info"
                  )
            LOGGED_USER = username
            LOGGED_USER_DB = db_name
            update_db_user_state()
            switch_page(home_page)
        else:
            CTkMessagebox(title="Errore di login", 
                  message="Credenziali non valide. Riprova!",
                  icon="info"
                  )

    except psycopg2.Error as e:
        CTkMessagebox(title="Errore di login", 
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
        CTkMessagebox(title="Errore",
                    message="Errore " + error_type,
                    icon="warning"
                    )
        return
    
    perform_login()


def conferma_ordine():
    global LOGGED_USER 
    global LOGGED_USER_DB
    global selected_checkbox_text

    tipo_lavorazione = ''
    orario_fine = time.strftime('%Y-%m-%d %H:%M:%S')
    #tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione,
    # Calcola l'orario di inizio
    orario_fine_dt = datetime.strptime(orario_fine, '%Y-%m-%d %H:%M:%S')
    tempo_setup = int(tempo_setup_num.get())
    tempo_taglio = int(tempo_taglio_num.get())
    tempo_tornitura = int(tempo_tornitura_num.get())
    tempo_fresatura = int(tempo_fresatura_num.get())
    tempo_elettroerosione = int(tempo_elettro_num.get())
    tempo_ciclo_totale = tempo_taglio + tempo_tornitura + tempo_fresatura + tempo_elettroerosione
    numero_pezzi = int(pezzi_select_num.get())
    orario_inizio_dt = orario_fine_dt - timedelta(minutes=tempo_setup + tempo_ciclo_totale)
    orario_inizio = orario_inizio_dt.strftime('%Y-%m-%d %H:%M:%S')
    numero_disegno = str(draw_num_entry.get())
    
    checkbox_data = selected_checkbox_text

    errore_riempimento = False

    if checkbox_data != "":
        tipo_lavorazione = checkbox_data#["text"]
        print("Checkbox selezionato:", tipo_lavorazione)
    else:
        print("Nessun checkbox selezionato.")
        # or tempo_taglio == 0 or tempo_tornitura == 0 or tempo_fresatura == 0 or tempo_elettroerosione == 0 

    # Verifica se tutti i campi sono stati compilati e se il numero di pezzi è diverso da zero
    if not all([orario_inizio, orario_fine, tipo_lavorazione, tempo_setup]) or numero_pezzi == 0 or numero_disegno == '':
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

    tempo_ciclo_totale = tempo_taglio + tempo_tornitura + tempo_fresatura + tempo_elettroerosione

    #orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, tempo_ciclo, numero_pezzi
    user_choose = ask_question(orario_fine_dt, tempo_setup, tempo_taglio, tempo_tornitura, 
                               tempo_fresatura, tempo_elettroerosione, tempo_ciclo_totale, 
                               orario_inizio_dt, orario_inizio, numero_pezzi, numero_disegno)
    if(not user_choose):
        return
    
    conn = None

    try:
        if(LOGGED_USER != '' and LOGGED_USER_DB != ''):
            db_name = LOGGED_USER_DB

            conn = psycopg2.connect(**{**db_config, 'dbname': db_name})
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS ordini (
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
                    numero_pezzi INTEGER
                )
            """)

            cur.execute("""
                INSERT INTO ordini (orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, tempo_ciclo_totale, numero_pezzi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (orario_inizio, orario_fine, numero_disegno, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_setup, tempo_ciclo_totale, numero_pezzi))

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
    
def ask_question(orario_fine_dt, tempo_setup, tempo_taglio, tempo_tornitura, tempo_fresatura, tempo_elettroerosione, tempo_ciclo_totale, orario_inizio_dt, orario_inizio, numero_pezzi, numero_disegno):
    # Formattazione dei dati come una tabella
    tabella = (
        f"{'INIZIO:':<20}{orario_inizio_dt}\n"
        f"{'FINE:':<20}{orario_fine_dt}\n"
        f"{'N DISEGNO:':<20}{numero_disegno}\n"
        f"{'SETUP:':<20}{tempo_setup} m\n"
        f"{'TAGLIO:':<20}{tempo_taglio} m\n"
        f"{'TORNITURA:':<20}{tempo_tornitura} m\n"
        f"{'FRESATURA:':<20}{tempo_fresatura} m\n"
        f"{'ELETTROEROSIONE:':<20}{tempo_elettroerosione} m\n"
        f"{'CICLO TOT.:':<20}{tempo_ciclo_totale} m\n"
        f"{'N PEZZI:':<20}{numero_pezzi} prodotti\n"
    )

    # Creazione del messaggio di messagebox
    msg = CTkMessagebox(
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
    #width= 140,
    #height= 28,
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

button_conferma_ordine = ctk.CTkButton(
    master=home_page, 
    bg_color=['gray92', 'gray14'], 
    text="Conferma ordine",
    width=_map_item_x(140 + 10, LOGIN_FRAME_WIDTH),
    height=_map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
    command=lambda: conferma_ordine())
button_conferma_ordine.place(relx=0.5, rely=1.0, anchor='s')

pezzi_label = ctk.CTkLabel(master=frame_n_pezzi, bg_color=['gray86', 'gray17'], text="N. Pezzi")
pezzi_label.place(x=_map_item_x(55, SETUP_TIME_FRAME_WIDTH), y=_map_item_y(8, SETUP_TIME_FRAME_HEIGHT))

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

#menu_tendina_utenti.
menu_tendina_utenti.configure(values=lista_utenti)

# Imposta il testo predefinito
default_text = "Seleziona un utente"  # Puoi cambiare questo testo se necessario
menu_tendina_utenti.set(default_text)

root.resizable(True, True)  # La finestra sarà ridimensionabile sia in larghezza che in altezza


def on_window_resize(event):
    global root_height
    global root_width
    # Aggiorna i valori dei widget in base alle dimensioni attuali della finestra
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    if frame_singup.winfo_exists():
        frame_singup.place(relx=0.40, rely=0.1, anchor='n')
    if frame_settings.winfo_exists():
        frame_settings.place(relx=0.60, rely=0.1, anchor='n')
    if frame_login.winfo_exists():
        frame_login.place(relx=0.50, rely=0.1, anchor='n')
    if frame_n_pezzi.winfo_exists():
        frame_n_pezzi.place(relx=0.999, rely=0.5, anchor='e')
    if frame_lavorazione.winfo_exists():
        frame_lavorazione.place(relx=0.50, rely=0.1, anchor='n')

    if frame_setup_time.winfo_exists():
        frame_setup_time.place(x=0, rely=0.5, anchor='w')

    if frame_log_setting.winfo_exists():
        frame_log_setting.place(relx=0.999, rely=0.003,anchor='ne')
    if frame_connection_title.winfo_exists():
        frame_connection_title.place(relx=0.999, rely=0.99, anchor='se')
    if frame_n_draw.winfo_exists():
        frame_n_draw.place(relx=0.50, rely=0.4, anchor='n')

    button_conferma_ordine.place(relx=0.5, rely=0.9, anchor='s')

def on_checkbox_change(checkbox_name):
    # Larghezza minima desiderata tra i frame
    min_spacing = 10  # Modifica questa variabile secondo le tue esigenze
    
    # Posizione X del frame precedente
    prev_frame_x = 0

    RELY_FRAME_TIME = 0.02
    
    if(selected_checkbox_text):
        frame_container_time.place(relx=0.50, rely=0.19, anchor='n')
    else:
        frame_container_time.place_forget()
        

    if checkbox_name == "taglio":
        if taglio_checkbox.get():
            frame_taglio_time.place(x=_map_item_x(10, CONTAINER_TIME_FRAME_HEIGHT), y=_map_item_y(5, CONTAINER_TIME_FRAME_WIDTH))
        else:
            frame_taglio_time.place_forget()
    elif checkbox_name == "tornitura":
        if tornitura_checkbox.get():
            frame_tornitura_time.place(x=230, y=_map_item_y(5, CONTAINER_TIME_FRAME_WIDTH))
        else:
            frame_tornitura_time.place_forget()
    elif checkbox_name == "fresatura":
        if fresatura_checkbox.get():
            frame_fresatura_time.place(x=230 + 220, y=_map_item_y(5, CONTAINER_TIME_FRAME_WIDTH))
        else:
            frame_fresatura_time.place_forget()
    elif checkbox_name == "elettro":
        if elettro_checkbox.get():
            frame_elettro_time.place(x=230 + 220 + 220, y=_map_item_y(5, CONTAINER_TIME_FRAME_WIDTH))
        else:
            frame_elettro_time.place_forget()


# Associa la funzione on_checkbox_change a ciascun checkbox
tornitura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("tornitura"))
fresatura_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("fresatura"))
elettro_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("elettro"))
taglio_checkbox.bind("<Button-1>", lambda event: on_checkbox_change("taglio"))

root.bind("<Configure>", on_window_resize)

root.mainloop()