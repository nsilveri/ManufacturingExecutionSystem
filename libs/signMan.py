import customtkinter as ctk
from libs.mapFunctions import Mapper as mapper
from libs.pages import Pages
from libs import variables as var
from CTkMessagebox import CTkMessagebox
from psycopg2 import sql
from libs import numPads
from libs.loadSaveConf import *
from ctkdlib.custom_widgets import *
import os
import shutil
from tkinter import filedialog

passwd_singup_entry = None
passwd_repeat_singup_entry = None

def switch_page_for_signup(switch_page, signup_page, home_page, DBMan, get_pdf_files_in_directory, menu_tendina_disegni, check_db_connection, mapper):

    SINGUP_FRAME_WIDTH = 190 + 20
    SINGUP_FRAME_HEIGHT = 263 + 20

    #FRAME SETTINGS
    SETTINGS_FRAME_WIDTH = 190 + 20
    SETTINGS_FRAME_HEIGHT = 263 + 20

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
            master= signup_page,
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

    
    def change_appearance_mode_event(new_appearance_mode: str):
        save_config("theme", new_appearance_mode)
        ctk.set_appearance_mode(new_appearance_mode)

    def change_color_event(new_color: str):
        save_config("color", new_color)
        ctk.set_default_color_theme(new_color)

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

        if password != confirm_password:
            CTkMessagebox(
                master= signup_page,
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
            CTkMessagebox(
                master= signup_page,
                title="Errore di registrazione", 
                message=f"Errore durante l'inserimento dell'utente nel database: {e}",
                icon="warning"
                )
            return False
        
    switch_page(signup_page)

    frame_singup_settings = ctk.CTkFrame(master=signup_page)
    frame_singup_settings.place(relx=0.50, rely=0.1, anchor='n')

    #SING-UP FRAME
    # Creazione del frame di registrazione
    frame_singup = ctk.CTkFrame(master= frame_singup_settings)

    # Label per il titolo "Registrazione"
    registration_title_label = ctk.CTkLabel(
        master=frame_singup, 
        bg_color=['gray92', 'gray14'], 
        text="Registrazione",
        font=("Helvetica", 16, "bold")  # Opzionale: cambia il font per enfatizzare il titolo
    )

    # Creazione del frame per l'inserimento dell'username
    user_entry_frame = ctk.CTkFrame(master=frame_singup)

    # Label e Entry per l'username
    user_label_singup = ctk.CTkLabel(
        master=user_entry_frame, 
        bg_color=['gray92', 'gray14'], 
        text="Username"
    )

    user_singup_entry = ctk.CTkEntry(
        master=user_entry_frame, 
        bg_color=['gray92', 'gray14'],
        width= mapper._map_item_x(150, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(38, SINGUP_FRAME_HEIGHT)
    )

    # Creazione del frame per l'inserimento della password
    user_password_entry_frame = ctk.CTkFrame(master=frame_singup)

    # Label e Entry per la password
    passwd_label_singup = ctk.CTkLabel(
        master=user_password_entry_frame, 
        bg_color=['gray92', 'gray14'], 
        text="Password"
    )

    passwd_singup_entry = ctk.CTkEntry(
        master=user_password_entry_frame, 
        bg_color=['gray92', 'gray14'],
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
    )
    passwd_singup_entry.configure(show='*')

    #Creazione del frame per la ripetizione della password
    user_password_repeat_entry_frame = ctk.CTkFrame(master=frame_singup)

    # Label e Entry per la ripetizione della password
    repeat_passwd_label_singup = ctk.CTkLabel(
        master=user_password_repeat_entry_frame, 
        bg_color=['gray92', 'gray14'], 
        text="Ripeti password"
    )

    passwd_repeat_singup_entry = ctk.CTkEntry(
        master=user_password_repeat_entry_frame, 
        bg_color=['gray92', 'gray14'],
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT)
    )
    passwd_repeat_singup_entry.configure(show='*')

    #Creazione del frame per i pulsanti Registra e Indietro
    button_signup_frame = ctk.CTkFrame(master=frame_singup)

    # Pulsante di registrazione
    singup_button = ctk.CTkButton(
        master=button_signup_frame, 
        bg_color=['gray92', 'gray14'], 
        text="Registrati",
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
        command=lambda: perform_registration()
    )

    # Pulsante per tornare indietro
    back_button_singup = ctk.CTkButton(
        master=button_signup_frame,
        bg_color=['gray92','gray14'],
        text="Indietro",
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
        command=lambda: switch_page(home_page)
        )
    
    registration_title_label.grid(row=0, column=0, padx=10, pady=10)

    user_entry_frame.grid(row=1, column=0, padx=10, pady=10)
    user_label_singup.grid(row=0, column=0, padx=5)
    user_singup_entry.grid(row=1, column=0, padx=5)

    user_password_entry_frame.grid(row=2, column=0, padx=10, pady=10)
    passwd_label_singup.grid(row=0, column=0, padx=5)
    passwd_singup_entry.grid(row=1, column=0, padx=5)

    user_password_repeat_entry_frame.grid(row=3, column=0, padx=10, pady=10)
    repeat_passwd_label_singup.grid(row=0, column=0, padx=5)
    passwd_repeat_singup_entry.grid(row=1, column=0, padx=5)

    button_signup_frame.grid(row=4, column=0, padx=10, pady=10)
    singup_button.grid(row=0, column=0, pady=5)
    back_button_singup.grid(row=1, column=0, pady=5)

    entry_list = [passwd_singup_entry, passwd_repeat_singup_entry]

    numpads_signup = numPads.generate_numpads(entry_list, keyheight= var.KEYHEIGHT, keywidth= var.KEYWIDTH)

    frame_singup.grid(row=0, column=0, padx=10, pady=10) 
        #place(relx=0.40, rely=0.1, anchor='n')

    # Creazione del frame SETTINGS come frame scrollabile
    frame_settings = ctk.CTkFrame(
        master=frame_singup_settings
        #orientation='vertical'                                  
    )
    frame_settings.grid_rowconfigure(0)
    frame_settings.grid(row=0, column=1, padx=20, pady=10)
    frame_singup.grid(row=0, column=0, padx=20, pady=10)

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
    num_board_select_num.configure(command=lambda: var.update_num_board(num_board_select_num.get()))

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

    gui_scale_select_num.configure(command=lambda: var.update_gui_scale(gui_scale_select_num.get()))

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
    db_settings.grid(row=1, column=0, pady= 2)

    # Pulsante per le impostazioni dei disegni
    draw_settings = ctk.CTkButton(
        master=frame_settings,
        bg_color=['gray92','gray14'],
        text="Impostazioni Disegni",
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
        command=lambda: show_draw_config_dialog()
    )
    draw_settings.grid(row=2, column=0, pady= 2)

    run_update = ctk.CTkButton(
        master=frame_settings,
        bg_color=['gray92','gray14'],
        text="Applica aggiornamento",
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
        command=lambda: show_draw_config_dialog()
    )
    run_update.grid(row=3, column=0, pady= 2)

    # Pulsante per le impostazioni dei disegni
    update_settings = ctk.CTkButton(
        master=frame_settings,
        bg_color=['gray92','gray14'],
        text="Impost. Update",
        width= mapper._map_item_x(140 + 10, SINGUP_FRAME_WIDTH),
        height= mapper._map_item_y(28 + 10, SINGUP_FRAME_HEIGHT),
        command=lambda: show_update_config_dialog()
    )

    update_settings.grid(row=4, column=0, pady= 2)
    frame_settings.grid(row=0, column=1, padx=10, pady=10)
    #place(relx=0.60, rely=0.1, anchor='n')
