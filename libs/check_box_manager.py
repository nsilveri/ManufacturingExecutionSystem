import json

class CheckboxStateHandler:
    def __init__(self, machine_data):
        self.machine_data = machine_data

    def create_json_string(self, checkbox_states):
        return json.dumps(checkbox_states)

    def parse_json_string(self, json_string):
        return json.loads(json_string)

    def count_true(self, MACCHINARIO):
        checkbox_states_string = self.machine_data[MACCHINARIO].prod_data.get_prod_data("checkbox_state")
        checkbox_states = json.loads(checkbox_states_string)  # Analizza la stringa JSON in un dizionario Python
        #print("checkbox_states:", checkbox_states)
        if checkbox_states is None:
            return 0
        count = sum(1 for state in checkbox_states.values() if isinstance(state, bool) and state)
        print("count:", count)
        return count

    def set_checkbox_states(self, checkbox_states, MACCHINARIO):
        json_string = self.create_json_string(checkbox_states)
        self.machine_data[MACCHINARIO].prod_data.set_prod_data("checkbox_state", json_string)

    def get_checkbox_states(self, MACCHINARIO):
        json_string = self.machine_data[MACCHINARIO].prod_data.get_prod_data("checkbox_state")
        return self.parse_json_string(json_string)
    
    def set_checkbox_state(self, checkbox_name, state, MACCHINARIO):
        checkbox_states = self.get_checkbox_states(MACCHINARIO)
        checkbox_states[checkbox_name] = state
        self.set_checkbox_states(checkbox_states, MACCHINARIO)

    def get_checkbox_state(self, checkbox_name, MACCHINARIO):
        checkbox_states = self.get_checkbox_states(MACCHINARIO)
        return checkbox_states.get(checkbox_name, False)