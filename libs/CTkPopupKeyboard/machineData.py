import time
from count_timer import CountTimer as Count
from CTkMessagebox import CTkMessagebox as msgbox

class Timer:
    def __init__(self):
        self.counter = Count()
        self.start_time = None
        self.timer_running = False
        self.paused_time = 0
        self.elapsed_time = 0
        self.minutes = 0
        self.seconds = 0
        self.attach_start = None
        self.attach_stop = None
        self.attach_reset = None

    def set_attach(self, buttons):
        # buttons = [start, stop, reset] timer.set_attach("name", [start_button, stop_button, reset_button])
        self.attach_start = buttons[0]
        self.attach_stop = buttons[1]
        self.attach_reset = buttons[2]

    def disable_buttons(self):
        if self.attach:
            for button in self.attach:
                button.configure(state="disabled")

    def enable_buttons(self):
        if self.attach:
            for button in self.attach:
                button.configure(state="normal")

    def start(self):
        if self.counter._get():
            self.counter.resume()
        else:
            self.counter.start()
        self.attach_start.configure(state="disabled")
        self.attach_stop.configure(state="normal")
        self.attach_reset.configure(state="normal")

    def stop(self):
        self.counter.pause()
        self.attach_start.configure(state="normal")
        self.attach_stop.configure(state="disabled")
        self.attach_reset.configure(state="normal")

    def reset(self):
        self.counter.reset()
        self.attach_start.configure(state="normal")
        self.attach_stop.configure(state="disabled")
        self.attach_reset.configure(state="disabled")

    def set_start_from_minutes(self, minutes):
        self.counter.set_start_time(minutes)
        self.attach_start.configure(state="normal")
        self.attach_stop.configure(state="disabled")
        self.attach_reset.configure(state="disabled")

    def _running(self):
        self.timer_running = self.counter.running
        return self.timer_running

    def _update_elapsed_time(self):
        self.elapsed_time = self.counter._get()

    def get_elapsed_time(self):
        self._update_elapsed_time()
        self.minutes = int(self.elapsed_time / 60)
        self.seconds = int(self.elapsed_time % 60)
        return f"{self.minutes:02}:{self.seconds:02}"

class MachineManager:
    def __init__(self):
        self.machines = {}  # Dizionario per memorizzare i timer associati a ciascun macchinario
        #self.attachments = {}  # Dizionario per memorizzare gli attachments per ciascun timer

    class TimerManager:

        def __init__(self):
            self.timers = {}
            self.attachments = {}  # Dizionario per memorizzare gli attachments per ciascun timer

        def set_attach_buttons(self, name, buttons):
            self.timers[name].set_attach(buttons)


        def disable_buttons(self, name):
            if name in self.attachments:
                for button in self.attachments[name]:
                    button.configure(state="disabled")

        def enable_buttons(self, name):
            if name in self.attachments:
                for button in self.attachments[name]:
                    button.configure(state="normal")

        def ask_reset_confirm(self, name):
            if name in self.timers:
                if self.get_elapsed_time(name) != '00:00':
                    msg = msgbox(
                        title="Conferma reset", 
                        message= f'Sei sicuro di voler resettare il timer {name}?',
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

        def add_timer(self, name):
            self.timers[name] = Timer()

        def start_timer(self, name):
            if name in self.timers:
                self.timers[name].start()
                self.disable_buttons(name)

        def stop_timer(self, name):
            if name in self.timers:
                self.timers[name].stop()

        def reset_timer(self, name):
            if name in self.timers:
                self.ask_reset_confirm(name)
                self.timers[name].reset()

        def set_start(self, name, minutes):
            if name in self.timers:
                self.timers[name].set_start_from_minutes(minutes)

        def running(self, name):
            if name in self.timers:
                return self.timers[name]._running()
            else:
                return False

        def get_elapsed_time(self, name):
            if name in self.timers:
                return self.timers[name].get_elapsed_time()
            else:
                return "00:00"

    def add_empty_machine(self, machine_name):
        # Aggiungi un macchinario vuoto
        if machine_name not in self.machines:
            self.machines[machine_name] = {}

    def add_timer_to_machine(self, machine_name, timer_name):
            # Aggiungi un timer a un macchinario esistente
            if machine_name in self.machines:
                self.machines[machine_name]= self.TimerManager()
            else:
                print(f"Errore: Il macchinario {machine_name} non esiste.")