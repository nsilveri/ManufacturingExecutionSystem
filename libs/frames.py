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
        command=lambda: switch_page(signup_page))

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

