# queries.py

CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS {} (
        id SERIAL PRIMARY KEY,
        orario_inizio TIMESTAMP,
        orario_fine TIMESTAMP,
        numero_disegno TEXT,
        commessa_lavorazione TEXT,
        tempo_taglio INTEGER,
        tempo_tornitura INTEGER,
        tempo_fresatura INTEGER,
        tempo_elettroerosione INTEGER,
        tempo_setup INTEGER,
        numero_pezzi INTEGER,
        note_lavorazione TEXT,
        macchina TEXT
    )
"""

INSERT_QUERY = """
    INSERT INTO {} (
        orario_inizio, 
        orario_fine, 
        numero_disegno, 
        commessa_lavorazione,
        tempo_taglio, 
        tempo_tornitura, 
        tempo_fresatura, 
        tempo_elettroerosione, 
        tempo_setup, 
        numero_pezzi, 
        note_lavorazione,
        macchina
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
