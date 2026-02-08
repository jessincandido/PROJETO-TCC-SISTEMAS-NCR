import sqlite3
import hashlib

# ================= CONEXÃO =================
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

# ================= TABELA PRODUTOS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL
)
""")

# ================= TABELA USUÁRIOS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nivel TEXT NOT NULL CHECK (nivel IN ('admin', 'operador'))
)
""")

# ================= HASH =================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ================= USUÁRIOS PADRÃO =================
usuarios = [
    ("admin", hash_senha("admin123"), "admin"),
    ("operador", hash_senha("123"), "operador")
]

cursor.executemany("""
INSERT OR IGNORE INTO usuarios (usuario, senha, nivel)
VALUES (?, ?, ?)
""", usuarios)

conn.commit()
conn.close()

print("Banco criado com sucesso!")
