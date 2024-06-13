from libs import CTkPopupKeyboard
import libs.variables as var

def generate_numpads(entry_list, keycolor='dodgerblue2', keywidth=var.KEYWIDTH, keyheight=var.KEYHEIGHT):
    numpads = []
    for entry in entry_list:
        numpad = CTkPopupKeyboard.PopupNumpad(
            attach=entry,
            keycolor=keycolor,
            keywidth=keywidth,
            keyheight=keyheight
        )
        numpads.append(numpad)
    return numpads