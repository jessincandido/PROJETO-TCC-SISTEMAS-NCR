import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import sqlite3

# ================= BANCO =================
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY,
    nome TEXT,
    preco REAL
)
""")
conn.commit()

# ================= FUNÇÃO ARREDONDADA =================
def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1+r*2, y1+r*2, start=90, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2-r*2, y1, x2, y1+r*2, start=0, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90, style="pieslice", **kwargs)
    canvas.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90, style="pieslice", **kwargs)
    canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
    canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)

# ================= CORES =================
COR_FUNDO = "#87CEFA"
COR_CARD = "#B0C4DE"

# ================= JANELA PRINCIPAL =================
janela = tk.Tk()
janela.title("Consulta de Produtos")
janela.geometry("900x600")
janela.configure(bg=COR_FUNDO)

# ================= FONTE PADRÃO (HELVETICA) =================
fonte_padrao = tkfont.nametofont("TkDefaultFont")
fonte_padrao.configure(family="Helvetica", size=12)
janela.option_add("*Font", fonte_padrao)

produto_var = tk.StringVar(value="—")
preco_var = tk.StringVar(value="R$ 0,00")
codigo_var = tk.StringVar()

# ================= TÍTULO =================
tk.Label(
    janela,
    text="SISTEMAS NCR",
    bg=COR_FUNDO,
    fg="blue",
    font=("Helvetica", 40, "bold")
).pack(pady=15)

# ================= CARD BUSCA =================
canvas_busca = tk.Canvas(janela, width=800, height=120, bg=COR_FUNDO, highlightthickness=0)
canvas_busca.pack()
rounded_rect(canvas_busca, 0, 0, 800, 120, 30, fill="white", outline="white")

tk.Label(
    janela,
    text="Digite o nome ou o código do produto",
    bg="white",
    font=("Helvetica", 14, "bold")
).place(relx=0.5, y=115, anchor="center")

entry_busca = tk.Entry(
    janela,
    textvariable=codigo_var,
    font=("Helvetica", 22),
    justify="center"
)
entry_busca.place(x=100, y=145, width=700, height=45)
entry_busca.focus()

# ================= CARD PRODUTO =================
canvas_card = tk.Canvas(janela, width=800, height=220, bg=COR_FUNDO, highlightthickness=0)
canvas_card.pack(pady=30)
rounded_rect(canvas_card, 0, 0, 800, 220, 30, fill=COR_CARD, outline=COR_CARD)

tk.Label(
    janela,
    textvariable=produto_var,
    bg=COR_CARD,
    font=("Helvetica", 28, "bold")
).place(x=120, y=300)

tk.Label(
    janela,
    textvariable=preco_var,
    bg=COR_CARD,
    fg="blue",
    font=("Helvetica", 34, "bold")
).place(x=120, y=350)

# ================= CONSULTA =================
def consultar(event=None):
    codigo = codigo_var.get()
    cursor.execute(
        "SELECT nome, preco FROM produtos WHERE codigo=? OR nome=?",
        (codigo, codigo)
    )
    r = cursor.fetchone()

    if r:
        produto_var.set(r[0])
        preco_var.set(f"R$ {r[1]:.2f}".replace(".", ","))
    else:
        produto_var.set("PRODUTO NÃO ENCONTRADO")
        preco_var.set("—")

    codigo_var.set("")

entry_busca.bind("<Return>", consultar)

# ================= TELA CADASTRO / EDIÇÃO =================
def abrir_tela_produto(titulo, codigo="", nome="", preco="", editar=False):
    t = tk.Toplevel(janela)
    t.geometry("900x600")
    t.configure(bg=COR_FUNDO)
    t.title(titulo)

    tk.Label(
        t,
        text="SISTEMAS NCR",
        bg=COR_FUNDO,
        fg="blue",
        font=("Helvetica", 40, "bold")
    ).pack(pady=15)

    canvas = tk.Canvas(t, width=800, height=360, bg=COR_FUNDO, highlightthickness=0)
    canvas.pack()
    rounded_rect(canvas, 0, 0, 800, 360, 30, fill=COR_CARD, outline=COR_CARD)

    # CÓDIGO
    tk.Label(t, text="Código", bg=COR_CARD, font=("Helvetica", 14, "bold")).place(x=120, y=150)
    entry_codigo = tk.Entry(t, font=("Helvetica", 18))
    entry_codigo.place(x=120, y=180, width=300)
    entry_codigo.insert(0, codigo)

    if editar:
        entry_codigo.config(state="disabled")

    # NOME
    tk.Label(t, text="Nome do Produto", bg=COR_CARD, font=("Helvetica", 14, "bold")).place(x=120, y=230)
    entry_nome = tk.Entry(t, font=("Helvetica", 18))
    entry_nome.place(x=120, y=260, width=660)
    entry_nome.insert(0, nome)

    # PREÇO
    tk.Label(t, text="Preço", bg=COR_CARD, font=("Helvetica", 14, "bold")).place(x=120, y=310)
    entry_preco = tk.Entry(t, font=("Helvetica", 18))
    entry_preco.place(x=120, y=340, width=300)
    entry_preco.insert(0, preco)

    def salvar():
        if not entry_nome.get() or not entry_preco.get():
            messagebox.showwarning("Atenção", "Preencha todos os campos")
            return

        try:
            if editar:
                cursor.execute(
                    "UPDATE produtos SET nome=?, preco=? WHERE codigo=?",
                    (entry_nome.get(), float(entry_preco.get().replace(",", ".")), codigo)
                )
            else:
                cursor.execute(
                    "INSERT INTO produtos VALUES (?, ?, ?)",
                    (entry_codigo.get(), entry_nome.get(), float(entry_preco.get().replace(",", ".")))
                )

            conn.commit()
            messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
            t.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(
        t,
        text="SALVAR",
        font=("Helvetica", 16, "bold"),
        bg="#10B981",
        fg="white",
        bd=0,
        command=salvar
    ).place(x=300, y=520, width=300, height=55)

# ================= BOTÕES =================
tk.Button(
    janela,
    text="Cadastrar Produto",
    font=("Helvetica", 12, "bold"),
    bg="#2563EB",
    fg="white",
    bd=0,
    command=lambda: abrir_tela_produto("Cadastrar Produto")
).pack(pady=5)

def abrir_edicao():
    codigo = codigo_var.get()
    cursor.execute("SELECT nome, preco FROM produtos WHERE codigo=?", (codigo,))
    r = cursor.fetchone()

    if not r:
        messagebox.showerror("Erro", "Produto não encontrado")
        return

    abrir_tela_produto("Editar Produto", codigo, r[0], str(r[1]).replace(".", ","), True)

tk.Button(
    janela,
    text="Editar Produto",
    font=("Helvetica", 12, "bold"),
    bg="#F59E0B",
    fg="white",
    bd=0,
    command=abrir_edicao
).pack()

# ================= FECHAR =================
def fechar():
    conn.close()
    janela.destroy()

janela.protocol("WM_DELETE_WINDOW", fechar)
janela.mainloop()
