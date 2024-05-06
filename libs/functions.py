import sys, subprocess, os, json, customtkinter, psycopg2

ORIGINAL_WIDTH =  800
ORIGINAL_HEIGHT = 500

root_width = ORIGINAL_WIDTH
root_height = ORIGINAL_HEIGHT

LOGGED_USER = ''
LOGGED_USER_DB = ''
DB_STATE = 'Non connesso'

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

def load_config():
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
            if "gui_scale" in config_data:
                return config_data["gui_scale"]
    except FileNotFoundError:
        # Se il file di configurazione non esiste, ritorna None
        pass
    return 0

GUI_SCALE = load_config()
print(GUI_SCALE)

connection_state_text = "Utente: " + LOGGED_USER + "DB: " + DB_STATE

#FRAME CONNESSIONE
FRAME_CONN_WIDTH = 152
FRAME_CONN_HEIGHT = 30

frame_connection_title = customtkinter.CTkFrame(
    master=home_page, 
    width=_map_frame_x(FRAME_CONN_WIDTH),
    height=_map_frame_y(FRAME_CONN_HEIGHT)
    )

label_connessione = customtkinter.CTkLabel(
    master=frame_connection_title,
    font=customtkinter.CTkFont(
        'Roboto',
        size=15),
    bg_color=['gray86','gray17'],
    height=10,
    text= connection_state_text,
    justify="left")

label_connessione.place(x=fc._map_item_x(10, FRAME_CONN_WIDTH), rely=0.2)

def update_db_user_state():
    if(LOGGED_USER == ''):
        LOGGED_USER_AUX = 'Ness.utente'
    else:
        LOGGED_USER_AUX = LOGGED_USER
    connection_state_text = "Accesso: " + LOGGED_USER_AUX + " DB: " + str(DB_STATE)  + "    "
    label_connessione.configure(text=connection_state_text)

    # Calcola la larghezza del testo del messaggio di stato della connessione
    text_width = customtkinter.CTkFont('Roboto', size=15).measure(connection_state_text)

    # Aggiorna la larghezza del frame e del label in base alla larghezza del testo
    frame_connection_title.configure(width=_map_frame_x(text_width + 10))  # Aggiungi un po' di spazio extra
    label_connessione.configure(width=_map_frame_x(text_width + 10))

    # Ora posiziona il label al centro del frame
    label_connessione.place(x=_map_item_x(10, FRAME_CONN_WIDTH), rely=0.5, anchor="w")  # Ancoraggio a sinistra


def check_db_connection():
    global db_config
    global DB_STATE

    try:
        # Prova a connetterti al database PostgreSQL
        conn = psycopg2.connect(**db_config)
        DB_STATE = 'OK'  # Se la connessione è riuscita, imposta DB_STATE su 'OK'
    except psycopg2.Error as e:
        print(f"Errore durante la connessione al database: {e}")
        DB_STATE = 'Errore di connessione'  # Se c'è stato un errore di connessione, imposta DB_STATE su 'Errore di connessione'
    finally:
        # Aggiorna lo stato della connessione nel programma
        update_db_user_state()

        # Chiudi la connessione se è stata aperta
        if 'conn' in locals():
            conn.close()

def restart_program():
    python = sys.executable
    subprocess.call([python, sys.argv[0]])