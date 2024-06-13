intestazioni = ["ID",               
                "Inizio",           
                "Fine",             
                "N.disegno",   
                "Taglio",        
                "Tornitura",     
                "Fresatura",     
                "Elettro..",     
                "Setup",         
                "N pezzi",          
                "Note",             
                "Comm..",         
                "Macch.."       
                ]

db_index_to_names = {
    0: "id",
    1: "orario_inizio",
    2: "orario_fine",
    3: "numero_disegno",
    4: "tempo_taglio",
    5: "tempo_tornitura",
    6: "tempo_fresatura",
    7: "tempo_elettroerosione",
    8: "tempo_setup",
    9: "numero_pezzi",
    10: "note_lavorazione",
    11: "commessa_lavorazione",
    12: "macchina"
}

db_names_to_index = {
    "id": 0,
    "orario_inizio": 1,
    "orario_fine": 2,
    "numero_disegno": 3,
    "tempo_taglio": 4,
    "tempo_tornitura": 5,
    "tempo_fresatura": 6,
    "tempo_elettroerosione": 7,
    "tempo_setup": 8,
    "numero_pezzi": 9,
    "note_lavorazione": 10,
    "commessa_lavorazione": 11,
    "macchina": 12
}

machines = [
    "PUMA",
    "ECOCA-SJ20", 
    "E.CUT", 
    "DVF5000", 
    "DMU50",
    "AWEA"
]