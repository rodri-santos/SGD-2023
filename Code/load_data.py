import pandas as pd
from dotenv import dotenv_values
import psycopg2

config = dotenv_values(".env")

def db_connection():
    try:
        db = psycopg2.connect(
            user=config.get("USER"),
            password=config.get("PASSWORD"),
            host=config.get("HOST"),
            port=config.get("PORT"),
            database=config.get("DATABASE")
        )
        return db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def query(connection, statement, values=None):
    cur = connection.cursor()
    try:
        cur.execute(statement, values)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        connection.rollback()
    finally:
        cur.close()

conn = db_connection()

drop_tables = """
DROP TABLE IF EXISTS produtocompra;
DROP TABLE IF EXISTS produtocarrinho;
DROP TABLE IF EXISTS compra;
DROP TABLE IF EXISTS carrinho;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS categoria;
"""

query(conn, drop_tables)

create_tables = """
CREATE TABLE produto (
	produto_id		 BIGSERIAL,
	nome			 VARCHAR(512) NOT NULL,
	stock			 INTEGER,
	descricao		 VARCHAR(512),
	fabrica		 VARCHAR(512) NOT NULL,
	peso			 INTEGER NOT NULL,
	url_imagem		 VARCHAR(512) NOT NULL,
	preco			 FLOAT(8),
	categoria_categoria_id BIGINT NOT NULL,
	PRIMARY KEY(produto_id)
);

CREATE TABLE carrinho (
	data		 DATE,
	cliente_cliente_id BIGINT,
	PRIMARY KEY(cliente_cliente_id)
);

CREATE TABLE cliente (
	cliente_id	 BIGINT,
	cliente_nome	 VARCHAR(512) NOT NULL,
	cliente_email VARCHAR(512) NOT NULL,
	PRIMARY KEY(cliente_id)
);

CREATE TABLE compra (
	compra_id		 BIGINT,
	data		 DATE NOT NULL,
	cliente_cliente_id BIGINT NOT NULL,
	PRIMARY KEY(compra_id)
);

CREATE TABLE produtocompra (
	quantidade	 BIGINT,
	preco		 FLOAT(8),
	compra_compra_id	 BIGINT,
	produto_produto_id BIGINT,
	PRIMARY KEY(compra_compra_id,produto_produto_id)
);

CREATE TABLE produtocarrinho (
	quantidade			 INTEGER,
	produto_produto_id		 BIGINT,
	carrinho_cliente_cliente_id BIGINT,
	PRIMARY KEY(produto_produto_id,carrinho_cliente_cliente_id)
);

CREATE TABLE categoria (
	categoria_id BIGINT,
	nome	 VARCHAR(512),
	PRIMARY KEY(categoria_id)
);

ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (categoria_categoria_id) REFERENCES categoria(categoria_id);
ALTER TABLE carrinho ADD CONSTRAINT carrinho_fk1 FOREIGN KEY (cliente_cliente_id) REFERENCES cliente(cliente_id);
ALTER TABLE compra ADD CONSTRAINT compra_fk1 FOREIGN KEY (cliente_cliente_id) REFERENCES cliente(cliente_id);
ALTER TABLE produtocompra ADD CONSTRAINT produtocompra_fk1 FOREIGN KEY (compra_compra_id) REFERENCES compra(compra_id);
ALTER TABLE produtocompra ADD CONSTRAINT produtocompra_fk2 FOREIGN KEY (produto_produto_id) REFERENCES produto(produto_id);
ALTER TABLE produtocarrinho ADD CONSTRAINT produtocarrinho_fk1 FOREIGN KEY (produto_produto_id) REFERENCES produto(produto_id);
ALTER TABLE produtocarrinho ADD CONSTRAINT produtocarrinho_fk2 FOREIGN KEY (carrinho_cliente_cliente_id) REFERENCES carrinho(cliente_cliente_id);
"""

query(conn, create_tables)

def insert_data(connection, table_name, dataframe):
    for _, row in dataframe.iterrows():
        columns = ', '.join(row.index)
        placeholders = ', '.join(['%s'] * len(row))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        query(connection, sql, tuple(row))

files_to_tables = {
    'categoria.csv': 'categoria',
    'produto.csv': 'produto',
    'cliente.csv': 'cliente',
    'carrinho.csv': 'carrinho',
    'compra.csv': 'compra',

}

for file, table in files_to_tables.items():
    data = pd.read_csv(file)
    insert_data(conn, table, data)

conn.close()
print("Dados carregados com sucesso!")