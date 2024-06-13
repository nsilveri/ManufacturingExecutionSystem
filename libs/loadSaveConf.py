import json

def load_config(conf_item, default=None):
    default_config = {
        "gui_scale": 100,
        "theme": "Light",
        "color": "blue",
        "pg_host": "",
        "pg_port": "",
        "pg_user": "",
        "pg_passwd": "",
        "draw_directory": "",
        "draw_mode_checkbox": 1,
        "keywidth": 75,
        "keyheight": 75,
        "num_board_scale": 100,
        "update_directory": ""
    }
    
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
            if conf_item in config_data:
                print(f'conf item:{conf_item}, {config_data[conf_item]}')
                return config_data[conf_item]
            else:
                print(f"Configuration '{conf_item}' not found, adding to config file with default value.")
                config_data[conf_item] = default
                with open("config.conf", "w") as updated_config_file:
                    json.dump(config_data, updated_config_file)
                return default
    except FileNotFoundError:
        # Se il file di configurazione non esiste, creiamo un nuovo file di configurazione con le impostazioni predefinite
        print(f"Configuration file not found, creating new config file with default value for '{conf_item}'.")
        config_data = default_config
        with open("config.conf", "w") as new_config_file:
            json.dump(config_data, new_config_file)
        return default_config[conf_item]

def save_config(conf_item, value):
    try:
        with open("config.conf", "r") as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        config_data = {}

    config_data[conf_item] = value

    with open("config.conf", "w") as config_file:
        json.dump(config_data, config_file)