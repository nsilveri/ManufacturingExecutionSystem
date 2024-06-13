import customtkinter as ctk
import libs.map_func as mapper
from libs import variables as var

class Pages:
    def __init__(self, root):
        self.home_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
        self.home_page.pack(expand=True, fill='both')
        self.signup_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
        self.login_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)
        self.modify_order_page = ctk.CTkFrame(root, fg_color='transparent', corner_radius=0, border_width=0)