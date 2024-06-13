import psycopg2
from CTkMessagebox import CTkMessagebox

class DbManager:
    def __init__(self, db_config, db_name):
        self.db_config = db_config
        self.db_name = db_name
        self.conn = None
        self.cur = None

    def connect(self, db_name= '', test_connection = False):
        try:
            self.db_name = db_name
            self.conn = psycopg2.connect(dbname=self.db_name, **self.db_config)
            self.cur = self.conn.cursor()
            return True
        
        except psycopg2.Error as e:
            print("Error connecting to database:", e)
            CTkMessagebox(title= "Errore", message= f"Errore durante la connessione al database: {e}", icon="error", 
                          option_1="OK", button_width= 50)
            return False

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None, commit=False, autoconnect=None):
        '''
        Execute a query on the database.
        :param query: The query to execute.
        :param params: The parameters to pass to the query.
        :param commit: If True, the query will be committed.
        :param autoconnect: If True, the connection will be opened and closed automatically with a specific database name.
        
        Examples:

        with autoconnect:
        db_manager.execute_query('SELECT * FROM table WHERE id = %s', (1,), autoconnect='my_db')

        without autoconnect and with commit:
        db_manager.conect('my_db')
        db_manager.execute_query('SELECT * FROM table WHERE id = %s', (1,), commit=True)
        db_manager.disconnect()

        without autoconnect and without commit:
        db_manager.conect('my_db')
        db_manager.execute_query('SELECT * FROM table WHERE id = %s', (1,))
        db_manager.disconnect()

        '''

        try:
            if autoconnect is not None:
                self.connect(autoconnect)
            if params:
                if commit:
                    self.conn.set_isolation_level(0)
                    self.cur.execute(query, params)
                    self.conn.set_isolation_level(1)
                else:
                    self.cur.execute(query, params)
            else:
                if commit:
                    self.conn.set_isolation_level(0)
                    self.cur.execute(query)
                    self.conn.set_isolation_level(1)
                else:
                    self.cur.execute(query)
            if commit:
                self.conn.commit()
            if autoconnect is not None:
                self.disconnect()
            return True
        except psycopg2.Error as e:
            print("Error executing query:", e)
            CTkMessagebox(title= "Errore", message= f"Errore durante l'esecuzione della query: {e}", icon= "error", button_width= 50)
            return False

    def fetch_data(self, query, params=None, autoconnect=None, column_names=False):
        '''
        Fetch data from the database.
        :param query: The query to execute.
        :param params: The parameters to pass to the query.
        :param autoconnect: If True, the connection will be opened and closed automatically with a specific database name.
        :param column_names: If True, the column names will be returned with the result.
        '''
        try:
            if autoconnect is not None:
                self.connect(autoconnect)
            if params:
                self.cur.execute(query, params)
                result = self.cur.fetchall()
                if column_names:
                    column_names = [desc[0] for desc in self.cur.description]
                    if autoconnect:
                        self.disconnect()
                    return column_names, result
                else:
                    if autoconnect:
                        self.disconnect()
                    return result
            else:
                self.cur.execute(query)
                result = self.cur.fetchall()
                if column_names:
                    column_names = [desc[0] for desc in self.cur.description]
                    if autoconnect is not None:
                        self.disconnect()
                    return column_names, result
                else:
                    if autoconnect is not None:
                        self.disconnect()
                    return result
        except psycopg2.Error as e:
            print("Error fetching data:", e)
            CTkMessagebox(title= "Errore", message= f"Errore durante il recupero dei dati: {e}", icon= "error", button_width= 50)
            return None
        
    def test_connection(self):
        try:
            self.connect()
            self.disconnect()
            return True
        except psycopg2.Error as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_column_names(self, table_name):
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';"
        result = self.fetch_data(query)
        if result:
            column_names = [row[0] for row in result]
            return column_names
        else:
            return None
