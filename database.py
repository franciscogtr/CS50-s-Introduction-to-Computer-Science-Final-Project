import sqlite3

class Database:

    def __init__(self, db_name='barber_agenda.db'):
        self.db_name = db_name
        self.conn = None

    def initialize_db(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def close_connection(self, exception):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self, query, params=()):
        if not self.conn:
            self.initialize_db()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS barbearia(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        cnpj TEXT NOT NULL,
        razao_social TEXT NOT NULL,
        nome_fantasia TEXT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL
        );
        '''
        )

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS barbeariaUser ON barbearia (username)")

        cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS barbeiros(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL,
        barbeariaId INTEGER NOT NULL,

        FOREIGN KEY (barbeariaId) REFERENCES barbearia(id)
        );
        '''
        )

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS barbeiroUser ON barbeiros (username)")

        cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        nome TEXT NOT NULL,
        preco NUMERIC NOT NULL,
        barbeariaId INTEGER NOT NULL,

        FOREIGN KEY (barbeariaId) REFERENCES barbearia(id)
        );
        '''
        )

        cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS agenda(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nomeCliente TEXT NOT NULL,
            barbeariaId INTEGER NOT NULL,
            barbeiroId INTEGER NOT NULL,
            servicoId INTEGER NOT NULL,
            dataAgendamento TEXT NOT NULL,
            dataAgendada TEXT NOT NULL,

            FOREIGN KEY (barbeariaId) REFERENCES barbearia(id),
            FOREIGN KEY (barbeiroId) REFERENCES barbeiros(id),
            FOREIGN KEY (servicoId) REFERENCES servicos(Id)
        );
        '''
        )
        
        self.conn.commit()
        

# Example usage:
# db = Database()
# conn = db.initialize_db()
# db.create_tables()
# db.close_connection(None)

