from CTkMessagebox import CTkMessagebox

def ask_question_choice(message, page):
    # Creazione del messaggio di messagebox
    msg = CTkMessagebox(
        master= page,
        title="Conferma ordine", 
        message= message,
        width=500,
        icon="question", 
        option_1="Conferma", 
        option_2="No" 
    )

    # Ottieni la risposta dal messagebox
    response = msg.get()
    
    if response=="Conferma":
        return True
    elif response=="No":
        return False