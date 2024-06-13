# Desc: Modulo per la modifica degli ordini
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from ctkdlib.custom_widgets import *
from CTkTable import *
from datetime import datetime
from libs.definitions import db_index_to_names, db_names_to_index, intestazioni, machines
from libs.support_functions import *
#from libs.variables import var.LOGGED_USER, var.LOGGED_USER_DB
import libs.variables as var

selected_row = None
selected_column = None
recent_orders_from_db = None

def modifica_ordine(switch_page, home_page, modify_order_page, ctk, screen_mapper, DBMan, TABLE_ORDERS_ROW = 20):
    #global recent_orders_from_db, selected_order_from_table, TABLE_ORDERS_ROW, var.LOGGED_USER, var.LOGGED_USER_DB
    global recent_orders_from_db, selected_row, selected_column
    ORDER_MOD_BUTTON_WIDTH = 100
    ORDER_MAN_FRAME_WIDTH = 400 
    ORDER_MAN_FRAME_HEIGHT = 200
    ORDER_BUTTONS_FRAME_WIDTH = 160
    ORDER_BUTTONS_FRAME_HEIGHT = 40

    if(var.LOGGED_USER == '' and var.LOGGED_USER_DB == ''):
        CTkMessagebox(title="Errore", 
                  message=f"Devi effettuare il login per poter concludere l'ordine!",
                  icon="info"
                  )
        return
    
    switch_page(modify_order_page)

    def get_last_orders(num_ordini):
        # Query per ottenere gli ultimi ordini
        query = f"""
            SELECT * FROM ordini
            ORDER BY id DESC
            LIMIT %s
        """
        #cur.execute(query, (num_ordini,))
        column_names, ultimi_ordini = DBMan.fetch_data(query, (num_ordini,), autoconnect=var.LOGGED_USER_DB, column_names=True) #cur.fetchall()

        # Costruire una lista di dizionari usando i nomi delle colonne come chiavi
        result = []
        for row in ultimi_ordini:
            order_dict = {column_names[i]: row[i] for i in range(len(row))}
            result.append(order_dict)

        print("Ultimi ordini:", result[0])

        return result

    def back_to_home():
        try:
            frame_gestione_modifica_ordine_selezionato.place_forget()

            frame_modify_order.grid_forget()
            button_modifica_ordine_selezionato.grid_forget()
            button_elimina_ordine_selezionato.grid_forget()
            frame_gestione_selezione_ordine_effettuato.place_forget()

            #button_conferma_modifica.grid_forget()
            button_indietro_modifica.grid_forget()
            frame_gestione_lista_ordini_effettuati.place_forget()
            table_orders_list.destroy()
        except Exception as e:
            print(f"Errore durante il ritorno alla home: {e}")
        switch_page(home_page)

    def gestione_selezione():
        
        def draw_selected_order():
            global selected_order_from_table, intestazioni
            
            for col, intestazione in enumerate(intestazioni):
                #print(f'col: {col}, intestazione: {intestazione}')
                table_selected_order.insert(0, col, intestazione, bg_color="lightgrey")

            # Popolamento della tabella con l'ordine selezionato
            ordine = selected_order_from_table
            for col, valore in enumerate(ordine, start=0):
                if isinstance(valore, datetime):
                    valore = valore.strftime("%Y-%m-%d %H:%M:%S")

                if col == 3 or col == 10 or col == 11 or col == 12:
                    if valore == None:
                        valore = ''
                table_selected_order.insert(1, col, valore)

            table_selected_order.grid(row=1, padx=5, pady=10)

        draw_selected_order()
        if frame_gestione_selezione_ordine_effettuato.winfo_exists():
            frame_modify_order.grid_forget()
            button_modifica_ordine_selezionato.grid_forget()
            frame_gestione_selezione_ordine_effettuato.grid_forget()

        frame_modify_order.grid(row=1, column= 0, columnspan= 3, padx=10, pady=10)
        button_elimina_ordine_selezionato.grid( row=0, column=1, padx=10, pady=10)
        frame_buttons_selezione_ordine_effettuato.grid(row=2, padx=10, pady=10)
        frame_buttons_selezione_ordine_effettuato.lift()

        frame_gestione_selezione_ordine_effettuato.grid(row=1,padx=10, pady=10)#place(relx=0.5, rely=0.8, anchor='s')

    def show_row_select(cell):
        global selected_row, prev_selected_row, selected_column, prev_selected_column, selected_order_from_table

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
        selected_order_from_table = selected
        selected_row = cell["row"]
        table_orders_list.edit_row(selected_row, fg_color=table_orders_list.hover_color)

        gestione_selezione()

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

    def update_db_value(id, value):
        global selected_column, column_value, db_index_to_names
        db_column_name = db_index_to_names[selected_column]
        #try:
        db_name = var.LOGGED_USER_DB

        # Genera la query di aggiornamento dinamicamente
        query = f"""
            UPDATE {'ordini'} 
            SET {db_column_name} = %s
            WHERE id = %s
        """

        result = DBMan.execute_query(query, (value, id), commit=True, autoconnect=db_name)

        if result:
            CTkMessagebox(
                title="Aggiornamento ordine",
                message="Ordine aggiornato con successo!",
                icon="info",
                button_height=38,
                button_width=150
            )
        
        else:
            CTkMessagebox(
                title="Errore",
                message="Errore durante l'aggiornamento dell'ordine!",
                icon="warning",
                button_height=38,
                button_width=150
            )
        

    def machine_modify_dialog(machines):
        global DATA_ORDER_CHANGE, column_value

        column_name = "Macchinario"
        if column_value == None:
            column_value = ''

        def save_machine():
            global column_value, DATA_ORDER_CHANGE, value_for_db, value_for_table
            value_for_db = machine_select.get()
            value_for_table = value_for_db
            print(f"Modifica '{column_name}': {column_value}")
            DATA_ORDER_CHANGE = True
            dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

        dialog = ctk.CTkToplevel()
        dialog.title(f"Modifica {column_name}")

        ctk.CTkLabel(master=dialog, text=f"{column_name}:").grid(row=0, column=0, padx=5, pady=5)
        machine_select = ctk.CTkOptionMenu(master=dialog, values=machines, width=76, height=44)
        #int_spinbox = CTkSpinbox(master=dialog, button_width=50, width=76, height=44)  # Personalizza i valori di 'from_' e 'to' secondo le tue esigenze
        machine_select.grid(row=0, column=1, padx=5, pady=5)
        #int_spinbox.set(column_value)

        save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_machine)
        save_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        DATA_ORDER_CHANGE = False
        
        dialog.lift()
        dialog.focus_set()
        dialog.grab_set()
        dialog.wait_window()

    def int_modify_dialog(column_name):
        global DATA_ORDER_CHANGE, column_value
        if column_value == None:
            column_value = 0

        def save_int():
            global column_value, DATA_ORDER_CHANGE, value_for_db, value_for_table
            value_for_db = int_spinbox.get()
            value_for_table = value_for_db
            print(f"Modifica '{column_name}': {column_value}")
            DATA_ORDER_CHANGE = True
            dialog.destroy()  # Chiudi il dialogo dopo aver salvato i dati

        dialog = ctk.CTkToplevel()
        dialog.title(f"Modifica {column_name}")

        ctk.CTkLabel(master=dialog, text=f"{column_name}:").grid(row=0, column=0, padx=5, pady=5)

        int_spinbox = CTkSpinbox(
            master=dialog, 
            bg_color=['gray86', 'gray17'],
            button_width=50,
            width=76, 
            height=44, 
            value= column_value, 
            fg_color=['gray81', 'gray20']
        )# Personalizza i valori di 'from_' e 'to' secondo le tue esigenze
        
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
        global DATA_ORDER_CHANGE, column_value, value_for_db, value_for_table
        global recent_orders_from_db, selected_row, selected_column
        index_to_modify = find_index_from_id(selected_order_from_table[0])
        value_for_db = recent_orders_from_db[index_to_modify][db_index_to_names[selected_column]]
        if value_for_db == None:
            value_for_db = ''
        if value_for_table == None:
            value_for_table = ''
        print(f"value_for_db_1 prima della mod: {value_for_db}")
        print(f'valore "value_for_table" in string modify dialog: {value_for_table}')
        print(f'column_value: {column_value}')
        
        def clean_string(string_to_clean):
            print(f"string_to_clean 1: {string_to_clean}")
            while string_to_clean[-1] == '\n':
                string_to_clean = string_to_clean[:-1]
            print(f"string_to_clean 2: {string_to_clean}")
            return string_to_clean
        
        def save_string():
            global column_value, DATA_ORDER_CHANGE, value_for_db, value_for_table
            value_for_db = clean_string(entry_string.get("0.0", "end"))
            value_for_table = value_for_db[:10]

            print(f'valore "value_for_db" in save string: {value_for_db}')
            print(f'valore "value_for_table" in save string: {value_for_table}')
            DATA_ORDER_CHANGE = True
            dialog.destroy()

        dialog = ctk.CTkToplevel()
        dialog.title(f"Modifica {column_name}")

        ctk.CTkLabel(master=dialog, text=f"{column_name}:").grid(row=0, column=0, padx=5, pady=5)
        entry_string = ctk.CTkTextbox(master=dialog, width=250, height=150)
        entry_string.grid(row=1, column=0, padx=5, pady=5)

        save_button = ctk.CTkButton(master=dialog, text="Salva", command=save_string)
        save_button.grid(row=2, column=0, padx=5, pady=5)

        if(column_value == None):
            column_value = ''
            entry_string.insert("0.0", value_for_db)
        else:
            entry_string.insert("0.0", value_for_db)

        DATA_ORDER_CHANGE = False
        
        dialog.lift()
        dialog.focus_set()
        dialog.grab_set()
        dialog.wait_window()

    def datetime_modify_dialog(datetime_to_mod):
        global DATA_ORDER_CHANGE

        def save_datetime():
            global new_date, column_value, DATA_ORDER_CHANGE, value_for_db, value_for_table
            selected_date = datetime.strptime(f"{day_spinbox.get()}/{month_spinbox.get()}/{year_spinbox.get()}", "%d/%m/%Y")
            selected_hour = int(hour_spinbox.get())
            selected_minute = int(minute_spinbox.get())
            value_for_db = datetime(selected_date.year, selected_date.month, selected_date.day, selected_hour, selected_minute)
            value_for_table = value_for_db.strftime("%m-%d %H:%M:%S")
            print("Data e ora inserite:", column_value)
            DATA_ORDER_CHANGE = True
            dialog.destroy()

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

    def find_index_from_id(selected_id):
        global recent_orders_from_db, selected_row, selected_column
        index_recent_orders = -1
        for i, order in enumerate(recent_orders_from_db):
            print(f'order[0]: {order}, selected_id: {selected_id}')
            if order['id'] == selected_id:
                index_recent_orders = i
                break
        return index_recent_orders
    
    def update_tables_values(index_recent_orders):
        global value_for_table
        global recent_orders_from_db, selected_row, selected_column
        print(f'update_tables_values\nvalue_for_db: {value_for_db}, value_for_table: {value_for_table}')
        recent_orders_from_db[index_recent_orders][selected_column] = value_for_db #ins valore nel dict del db
        print(f'recent_orders_from_db: {recent_orders_from_db[index_recent_orders][selected_column]}')
        table_selected_order.insert(1, selected_column, value_for_table)# ins valore nella tabella selezionata
        selected_order_from_table[selected_column] = value_for_table# ins valore nella tabella ordini recenti
        print(f'selected_order_from_table: {selected_order_from_table[selected_column]}')
        table_orders_list.insert(selected_row, selected_column, value_for_table)
        
    def modifica_valore_colonna():
        global selected_column, column_name, column_value, new_date, selected_order_from_table, value_for_db, value_for_table
        selected_id = selected_order_from_table[0]
        print(f'selected_id: {selected_id}, selected_order_from_db: {selected_order_from_table}')
        print(f'selected_id: {selected_id}, selected_order_from_table: {selected_order_from_table}')
        index_recent_orders = find_index_from_id(selected_id)
        print(f'selected_column: {selected_column}')

        value_for_db = None
        value_for_table = None

        if selected_column == 1 or selected_column == 2:
            if column_value == None or column_value == 'error':
                print('error value found')
                column_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_value_datetime = datetime.strptime(column_value, "%Y-%m-%d %H:%M:%S")
            
            datetime_modify_dialog(date_value_datetime)
            if(DATA_ORDER_CHANGE):
                update_tables_values(index_recent_orders)

        elif selected_column == 3 or selected_column == 10 or selected_column == 11:
            string_modify_dialog(column_name)
            if(DATA_ORDER_CHANGE):
                update_tables_values(index_recent_orders)

        elif selected_column == 4 or selected_column == 5 or selected_column == 6 or selected_column == 7 or selected_column == 8 or selected_column == 9:
            int_modify_dialog(column_name)
            if(DATA_ORDER_CHANGE):
                update_tables_values(index_recent_orders)

        elif selected_column == 12:
            machine_modify_dialog(machines)
            if(DATA_ORDER_CHANGE):
                update_tables_values(index_recent_orders)

        if DATA_ORDER_CHANGE:
            print(f'DATA_ORDER_CHANGE: {DATA_ORDER_CHANGE}')
            update_db_value(selected_order_from_table[0], value_for_db)
            value_for_db = None
            value_for_table = None

        else:
            print(f'DATA_ORDER_CHANGE: {DATA_ORDER_CHANGE}')

    def elimina_ordine():
        global selected_order_from_table, selected_row

        CHOICE = ask_question_choice(f"Sei sicuro di voler eliminare l'ordine con ID:{selected_order_from_table[0]}", modify_order_page)

        if CHOICE:
            db_name = var.LOGGED_USER_DB

            query = """
                DELETE FROM {} 
                WHERE id = %s
            """.format('ordini')

            result = DBMan.execute_query(query, (selected_order_from_table[0],), commit=True, autoconnect=db_name)

            if result:
                CTkMessagebox(
                    title="Eliminazione ordine",
                    message="Ordine eliminato con successo!",
                    icon="info",
                    button_height=38,
                    button_width=150
                )
            
            else:
                CTkMessagebox(
                    title="Errore",
                    message="Errore durante l'eliminazione dell'ordine!",
                    icon="warning",
                    button_height=38,
                    button_width=150
                )
                return

            table_orders_list.delete_row(selected_row)
            draw_table_orders()
            button_modifica_ordine_selezionato.grid_forget()
            button_elimina_ordine_selezionato.grid_forget()
            frame_gestione_selezione_ordine_effettuato.place_forget()

    frame_order = ctk.CTkFrame(master=modify_order_page)
    frame_order.place(relx=0.5, anchor='n')

    frame_order_list = ctk.CTkScrollableFrame(master=frame_order, width= 900)#root_width - 100)#, height= root_height / 2)#, height=ORDER_MAN_FRAME_HEIGHT)
    frame_order_list.grid(row=0, column=0, columnspan= 3, padx=5, pady=5)

    frame_modify_order = ctk.CTkFrame(master=frame_order, width=ORDER_MAN_FRAME_WIDTH)

    frame_gestione_selezione_ordine_effettuato = ctk.CTkFrame(
        master=frame_modify_order,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )

    COLUMN_NUM = 13

    table_orders_list = CTkTable(master=frame_order_list, width= 50, height= 38, row=TABLE_ORDERS_ROW + 1, command=show_row_select, column=COLUMN_NUM)
    table_selected_order = CTkTable(master=frame_gestione_selezione_ordine_effettuato, width= 50, height= 38,  command=show_column_select, row=2, column=COLUMN_NUM)

    # Creazione del frame
    frame_gestione_lista_ordini_effettuati = ctk.CTkFrame(
        master=frame_order, #modify_order_page,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )
    
    button_indietro_modifica = ctk.CTkButton(
        master=frame_gestione_lista_ordini_effettuati, 
        bg_color=['gray92', 'gray14'],
        text="Indietro",
        width=screen_mapper._map_item_x(140 + 10, ORDER_MAN_FRAME_WIDTH),
        height=screen_mapper._map_item_y(28 + 10, ORDER_MAN_FRAME_HEIGHT),
        command=lambda: back_to_home()
    )

    # Posizionamento del frame
    frame_buttons_selezione_ordine_effettuato = ctk.CTkFrame(
        master=frame_gestione_selezione_ordine_effettuato,
        width=ORDER_BUTTONS_FRAME_WIDTH,
        height=ORDER_BUTTONS_FRAME_WIDTH
    )

    button_modifica_ordine_selezionato = ctk.CTkButton(
        master=frame_buttons_selezione_ordine_effettuato, 
        bg_color=['gray92', 'gray14'],
        text="Modifica ordine",
        width=screen_mapper._map_item_x(140 + 10, ORDER_BUTTONS_FRAME_WIDTH),
        height=screen_mapper._map_item_y(28 + 10, ORDER_BUTTONS_FRAME_HEIGHT),
        command=lambda: modifica_valore_colonna()
    )

    button_elimina_ordine_selezionato = ctk.CTkButton(
        master=frame_buttons_selezione_ordine_effettuato, 
        bg_color=['gray92', 'gray14'], 
        text="Elimina ordine",
        width=screen_mapper._map_item_x(140 + 10, ORDER_BUTTONS_FRAME_WIDTH),
        height=screen_mapper._map_item_y(28 + 10, ORDER_BUTTONS_FRAME_HEIGHT),
        command=lambda: elimina_ordine()
    )

    frame_gestione_lista_ordini_effettuati.grid(row=2, column= 1, padx=10, pady=10)
    button_indietro_modifica.grid(row=0, column=3, padx=10, pady=10)

    def draw_table_orders():
        global recent_orders_from_db, selected_row, selected_column
        frame_order_list.grid(row=0, padx=10, pady=10)

        recent_orders_from_db = None
        while recent_orders_from_db is None:
            recent_orders_from_db = get_last_orders(TABLE_ORDERS_ROW)
        #TABLE_ORDERS_ROW = len(recent_orders_from_db)
        #print('recent_orders_from_db len:', len(recent_orders_from_db))

        # Popolamento dell'intestazione della tabella
        try:
            for col, intestazione in enumerate(intestazioni):
                print(f'col: {col}, intestazione: {intestazione}')#, valore: {recent_orders_from_db[0][intestazioni[col]]}')
                table_orders_list.insert(0, col, intestazione, bg_color="lightgrey")    
        
        except Exception as e:
            print(f"Errore durante il popolamento dell'intestazione della tabella: {e}")
        
        # Popolamento della tabella con gli ordini
        print("qui ci arrivo")
        print(f'recent_orders_from_db: {recent_orders_from_db[0]}')
        
        for row, ordine in enumerate(recent_orders_from_db, start=1):
            for col, valore in ordine.items():  # Usiamo items() per iterare su chiave e valore del dizionario
                col_index = db_names_to_index.get(col)
                print(f'col_index: {col_index}, valore: {valore}')
                try:
                    if col_index == 1 or col_index == 2:
                        val_for_table = valore.strftime("%Y-%m-%d %H:%M:%S")
                    elif col_index == 3 or col_index == 10 or col_index == 11 or col_index == 12:
                        if valore == None:
                            valore = ''
                        val_for_table = valore[:10]
                    elif col_index == 0   or col_index == 4   or col_index == 5 or col_index == 6 or col_index == 7 or col_index == 8 or col_index == 9:
                        val_for_table = valore
                except:
                    val_for_table = 'error'
                print(f'val_for_table: {val_for_table}')
                table_orders_list.insert(row, col_index, val_for_table)
                val_for_table = None
        #print(recent_orders_from_db)
        table_orders_list.pack(expand=True, padx=20, pady=20, anchor='n')
        

    draw_table_orders()

    frame_gestione_modifica_ordine_selezionato = ctk.CTkFrame(
        master=modify_order_page,
        width=ORDER_MAN_FRAME_WIDTH,
        height=ORDER_MAN_FRAME_HEIGHT
    )

    pass