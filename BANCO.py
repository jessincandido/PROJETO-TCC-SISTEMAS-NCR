import sqlite3

# Cria ou abre o banco
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

# Cria a tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL
)
""")

# Insere alguns produtos de exemplo
produtos = [
    ("789", "PILHA RAYOVAC AAA", 3.99),
    ("123", "CABO USB TIPO C", 12.50),
    ("456", "CARREGADOR TURBO", 59.90)
]

cursor.executemany(
    "INSERT OR IGNORE INTO produtos VALUES (?, ?, ?)",
    produtos
)

conn.commit()
conn.close()

print("Banco criado com sucesso!")
