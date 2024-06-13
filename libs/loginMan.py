import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import libs.CTkPopupKeyboard.numpad as CTkPopupKeyboard
import libs.variables as var

def switch_page_for_login(switch_page, home_page, login_page, users_list, mapper, get_user_databases, DBMan, carica_temp, KEYWIDTH, KEYHEIGHT):#, var.LOGGED_USER, var.LOGGED_USER_DB):

    def perform_login(username, password):
        print("Performing login...")
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

            DBMan.connect(db_name)
            password_hash = DBMan.fetch_data("SELECT password_hash FROM password")
            password_hash = password_hash[0][0]

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

                var.set_logged_user(username, db_name)

                print("Username:", var.LOGGED_USER)
                print("DB Name:", var.LOGGED_USER_DB)

                switch_page(home_page)
                carica_temp()
                LOAD_TEMP = False
                print("LOAD_TEMP: " + str(LOAD_TEMP))
                print("Utente loggato: " + var.LOGGED_USER, "Database: " + var.LOGGED_USER_DB)

            else:
                CTkMessagebox(
                    master= login_page,
                    title="Errore di login", 
                    message="Credenziali non valide. Riprova!",
                    icon="info"
                    )

        finally:
            if DBMan:
                DBMan.disconnect()

    def accedi(username, password):
        
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
        
        perform_login(username, password)

    if users_list == ["Errore1", "Errore2", "Errore3"]:
        users_list = get_user_databases()

    #LOGIN FRAME
    LOGIN_FRAME_WIDTH = 190 + 20
    LOGIN_FRAME_HEIGHT = 263 + 20

    frame_login = ctk.CTkFrame(master=login_page)

    user_menu_label = ctk.CTkLabel(
        master=frame_login,
        bg_color=['gray92', 'gray14'], 
        text="Seleziona utente"
        )


    menu_tendina_utenti = ctk.CTkOptionMenu(
        master=frame_login,
        values=[],
        bg_color=['gray86', 'gray17'],
        width=mapper._map_item_x(150, LOGIN_FRAME_WIDTH),
        height=mapper._map_item_y(38, LOGIN_FRAME_HEIGHT),
        dropdown_font = ctk.CTkFont(
            'Roboto',
            size=16),
        hover=False)

    passwd_login_entry = ctk.CTkEntry(
        master=frame_login, 
        width= 140 + 10,
        height= 28 + 10,
        bg_color=['gray92', 'gray14']
        )
    passwd_login_entry.configure(show='*')

    passwd_label = ctk.CTkLabel(
        master=frame_login,
        bg_color=['gray92', 'gray14'],
        text="Password")

    login_button = ctk.CTkButton(
        master=frame_login, 
        bg_color=['gray92', 'gray14'], 
        width=mapper._map_item_x(140 + 10, LOGIN_FRAME_WIDTH),
        height=mapper._map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
        text="Accedi")
    
    numpad_login = CTkPopupKeyboard.PopupNumpad(
        attach= passwd_login_entry,
        keycolor= 'dodgerblue2',
        keywidth= KEYWIDTH,
        keyheight= KEYHEIGHT
        )

    #menu_tendina_utenti.
    menu_tendina_utenti.configure(values=users_list)

    # Imposta il testo predefinito
    default_text = "Seleziona un utente"  # Puoi cambiare questo testo se necessario
    menu_tendina_utenti.set(default_text)

    # Collega la funzione al pulsante "Accedi"
    login_button.configure(command=lambda: accedi(menu_tendina_utenti.get(), passwd_login_entry.get()))

    back_login_button = ctk.CTkButton(
        master=frame_login,
        bg_color=['gray92','gray14'],
        command=lambda: switch_page(home_page),
        width=mapper._map_item_x(140 + 10, LOGIN_FRAME_WIDTH),
        height=mapper._map_item_y(28 + 10, LOGIN_FRAME_HEIGHT),
        text="Indietro")

    user_menu_label.grid(    row= 0,padx= 10,   pady= 10)
    menu_tendina_utenti.grid(row= 1,padx= 10,   pady= 10)
    passwd_login_entry.grid( row= 2,padx= 10,   pady= 10)
    passwd_label.grid(       row= 3,padx= 10,   pady= 10)
    login_button.grid(       row= 4,padx= 10,   pady= 10)
    back_login_button.grid(  row= 5,padx= 10,   pady= 10)

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

    menu_tendina_utenti.configure(values=users_list)
    switch_page(login_page)