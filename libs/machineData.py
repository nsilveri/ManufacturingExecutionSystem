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
        if(self.attach_start and self.attach_stop and self.attach_reset):
            self.attach_start.configure(state="disabled")
            self.attach_stop.configure(state="normal")
            self.attach_reset.configure(state="normal")

    def stop(self):
        self.counter.pause()
        if(self.attach_start and self.attach_stop and self.attach_reset):
            self.attach_start.configure(state="normal")
            self.attach_stop.configure(state="disabled")
            self.attach_reset.configure(state="normal")

    def reset(self):
        self.counter.reset()
        if(self.attach_start and self.attach_stop and self.attach_reset):
            self.attach_start.configure(state="normal")
            self.attach_stop.configure(state="disabled")
            self.attach_reset.configure(state="disabled")

    def set_start_from_minutes(self, minutes):
        self.counter.set_start_time(minutes)
        if(self.attach_start and self.attach_stop and self.attach_reset):
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
        self.machines = {}

    class TimerManager:
        def __init__(self):
            self.timers = self.Timers()

        class Timers:
            def __init__(self):
                self.timers = {}
                self.attachments = {}

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

            def reset_timer(self, name, FORCE=False):
                if name in self.timers:
                    if FORCE:
                        self.timers[name].reset()
                    elif self.ask_reset_confirm(name):
                        self.timers[name].reset()

            def reset_all_timers(self):
                for timer in self.timers:
                    self.reset_timer(timer, FORCE=True)

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
    
    class DateManager:
        def __init__(self):
            self.dates = self.Dates()

        class Dates:
            def __init__(self):
                self.dates = {}

            def add_date(self, name):
                if name not in self.dates:
                    self.dates[name] = None
                else:
                    print(f"Errore: La data '{name}' è già stata impostata.")

            def set_date(self, name, date):
                if name in self.dates:
                    self.dates[name] = date
                    #print(f'Dato {name}, {date} aggiunto.')
                else:
                    print(f'Dato {name}, {date} aggiunto.')
                    print(f"Errore: La data '{name}' non è stata aggiunta.")

            def get_date(self, name):
                return self.dates.get(name, None)

            def update_date(self, name, new_date):
                if name in self.dates:
                    self.dates[name] = new_date
                else:
                    print(f"Errore: La data '{name}' non esiste.")

    class InfoProductionManager:
        def __init__(self):
            self.dates = self.InfoProduction()

        class InfoProduction:
            def __init__(self):
                self.production = {}

            def add_prod_data(self, name):
                if name not in self.production:
                    self.production[name] = ""
                else:
                    print(f"Errore: Il dato '{name}' è già stato impostato.")

            def set_prod_data(self, name, data):
                if name in self.production:
                    if isinstance(data, str):
                        self.production[name] = data
                        #print("\nContenuto di self.production:", self.production)  # Output di debug
                        #print(f'Dato {name}, {data} aggiunto.')
                    else:
                        self.production[name] = str(data)
                        #print(f'Dato {name}, {data} aggiunto.')
                        #print("\nContenuto di self.production:", self.production)  # Output di debug
                        #print("Dato convertito in stringa.")
                else:
                    print(f"Errore: Il dato '{name}' non è stato aggiunto.")

            def get_prod_data(self, name):
                if name in self.production:
                    print("\nContenuto di self.production:", self.production[name])  # Output di debug
                    return self.production.get(name)
                else:
                    print(f"Errore: Il dato '{name}' non esiste.")

            def print_prod_data(self, name):
                if name in self.production:
                    print("\nContenuto di self.production:", self.production[name])
                else:
                    print(f"Errore: Il dato '{name}' non esiste.")

            def update_prod_data(self, name, new_data):
                if name in self.production:
                    if isinstance(new_data, str):
                        self.production[name] = new_data
                    else:
                        self.production[name] = str(new_data)
                        print("Dato convertito in stringa.")
                else:
                    print(f"Errore: Il dato '{name}' non esiste.")


    def __getitem__(self, key):
        return self.machines[key]

    def add_empty_machine(self, machine_name):
        machine = MachineManager()
        machine.timers = self.TimerManager.Timers()
        machine.dates = self.DateManager.Dates()
        machine.prod_data = self.InfoProductionManager.InfoProduction()
        self.machines[machine_name] = machine


        