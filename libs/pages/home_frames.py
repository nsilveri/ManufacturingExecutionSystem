import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from .. import map_func as mapper

class MyHomePage:
    def __init__(self, root):
        self.root = root
        self.setup_home_page()

    def setup_home_page(self):
        #FRAME NOTE
        N_NOTE_FRAME_WIDTH = 210
        N_NOTE_FRAME_HEIGHT = 100

        self.home_page = ctk.CTkFrame(self.root, fg_color='transparent', corner_radius=0, border_width=0)
        self.home_page.pack(expand=True, fill='both')

        self.frame_note = ctk.CTkFrame(
            master=self.home_page,
            width=mapper._map_frame_x(N_NOTE_FRAME_WIDTH), 
            height=mapper._map_frame_y(N_NOTE_FRAME_HEIGHT)
        )

        self.note_mode_checkbox = ctk.CTkCheckBox(
            master=self.frame_note, 
            bg_color=['gray86', 'gray17'], 
            text="Auto"
        )

        self.note_num_label = ctk.CTkLabel(
            master=self.frame_note, 
            bg_color=['gray92', 'gray14'], 
            text="Aggiungi note"
        )

        self.note_num_entry = ctk.CTkEntry(
            master=self.frame_note, 
            width= 140 + 10,
            height= 28 + 10,
            bg_color=['gray92', 'gray14']
        )

        self.note_num_label.grid(row= 0, column= 0, padx= 10, pady= 10)
        self.note_num_entry.grid(row= 1, columnspan= 2, padx= 10, pady= 10)

        #FRAME COMMESSA
        N_NOTE_FRAME_WIDTH = 210
        N_NOTE_FRAME_HEIGHT = 100

        self.frame_commessa = ctk.CTkFrame(
            master=self.home_page,
            width=mapper._map_frame_x(N_NOTE_FRAME_WIDTH), 
            height=mapper._map_frame_y(N_NOTE_FRAME_HEIGHT)
        )

        self.commessa_mode_checkbox = ctk.CTkCheckBox(
            master=self.frame_commessa, 
            bg_color=['gray86', 'gray17'], 
            text="Auto"
        )

        #FRAME SELEZIONA MACCHINA
        ORDER_MAN_FRAME_WIDTH = 400 
        ORDER_MAN_FRAME_HEIGHT = 200

        # Creazione del frame
        self.frame_seleziona_macchina = ctk.CTkFrame(
            master=self.home_page
        )

        
