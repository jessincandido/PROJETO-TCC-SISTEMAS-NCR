import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import sqlite3
import hashlib
from tkinter import ttk
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from tkinter import filedialog
from PIL import Image as PILImage, ImageTk
from reportlab.platypus import Image




# ================= TEMA =================
COR_FUNDO = "#D3D3D3"
COR_CARD = "#ADD8E6"
COR_TEXTO = "#0F172A"
COR_SUBTEXTO = "#475569"
COR_PRIMARIA = "#2563EB"
COR_ALERTA = "#F59E0B"
COR_SUCESSO = "#10B981"

# ================= BANCO =================
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

# ================= JANELA =================
janela = tk.Tk()
janela.title("Sistema Comercial - Produtos")
janela.geometry("900x650")
janela.configure(bg=COR_FUNDO)
janela.withdraw()

# ================= FONTE =================
fonte_padrao = tkfont.nametofont("TkDefaultFont")
fonte_padrao.configure(family="Segoe UI", size=11)
janela.option_add("*Font", fonte_padrao)

# ================= VARIÁVEIS =================
codigo_entry_var = tk.StringVar()          # campo de digitação
codigo_var = tk.StringVar(value="Código: —")  # aparece no card
produto_var = tk.StringVar(value="—")
preco_var = tk.StringVar(value="R$ 0,00")
quantidade_var = tk.StringVar(value="Quantidade: —")

produto_codigo_atual = None
produto_nome_atual = None
produto_preco_atual = None
produto_qtd_atual = None

# ================= USUÁRIO LOGADO =================
usuario_logado = None
usuario_label_var = tk.StringVar(value="Usuário: —")


# ================= HEADER =================
header = tk.Frame(janela, bg=COR_CARD, height=110)
header.pack(fill="x")
usuario_label = tk.Label(header,
                         textvariable=usuario_label_var,
                         bg=COR_CARD,
                         fg=COR_TEXTO,
                         font=("Segoe UI", 10, "bold"))

usuario_label.pack(side="right", padx=20)
usuario_nivel = None

# ===== LOGO =====
logo_img = PILImage.open("LOGONCR2.png")
logo_img = logo_img.resize((450, 130))
logo_tk = ImageTk.PhotoImage(logo_img)

logo_label = tk.Label(header, image=logo_tk, bg=COR_CARD)
logo_label.image = logo_tk
logo_label.pack(side="left", padx=20, pady=10)


tk.Label(header, text="Consulta de Produtos",
         bg=COR_CARD, fg="black").pack(side="left")

# ================= BUSCA =================
frame_busca = tk.Frame(janela, bg=COR_CARD)
frame_busca.pack(padx=30, pady=20, fill="x")

tk.Label(frame_busca, text="Buscar produto",
         bg=COR_CARD, fg=COR_SUBTEXTO).pack(anchor="w")

# ================= VALIDAÇÃO BUSCA =================
def validar_busca(texto):
    return texto.isalnum() or texto == ""

vcmd = (janela.register(validar_busca), "%P")

entry_busca = tk.Entry(frame_busca,
                       textvariable=codigo_entry_var,
                       font=("Segoe UI", 18),
                       validate="key",
                       validatecommand=vcmd)

entry_busca.pack(fill="x", ipady=8)
entry_busca.focus()



# ================= CARD PRODUTO =================
card = tk.Frame(janela, bg=COR_CARD)
card.pack(padx=50, pady=30, fill="x")

tk.Label(card, textvariable=codigo_var,
         bg=COR_CARD, fg=COR_SUBTEXTO,
         font=("Segoe UI", 16)).pack(anchor="w", padx=20, pady=(15, 0))

tk.Label(card, textvariable=produto_var,
         bg=COR_CARD, fg=COR_TEXTO,
         font=("Segoe UI", 40, "bold")).pack(anchor="w", padx=20, pady=(5, 5))

tk.Label(card, textvariable=preco_var,
         bg=COR_CARD, fg=COR_PRIMARIA,
         font=("Segoe UI", 40, "bold")).pack(anchor="w", padx=20)

tk.Label(card, textvariable=quantidade_var,
         bg=COR_CARD, fg=COR_SUBTEXTO).pack(anchor="w", padx=20, pady=(5, 15))


# ================= CONSULTAR =================
def consultar(event=None):
    global produto_codigo_atual, produto_nome_atual, produto_preco_atual, produto_qtd_atual

    termo = codigo_entry_var.get().strip()
    if not termo:
        return

    cursor.execute("""
        SELECT codigo, nome, preco, quantidade
        FROM produtos
        WHERE codigo = ? OR nome LIKE ?
        LIMIT 1
    """, (termo, f"%{termo}%"))

    r = cursor.fetchone()

    if r:
        produto_codigo_atual, produto_nome_atual, produto_preco_atual, produto_qtd_atual = r
        produto_var.set(r[1])
        preco_var.set(f"R$ {r[2]:.2f}".replace(".", ","))
        quantidade_var.set(f"Quantidade disponível: {r[3]}")
        codigo_var.set(f"Código: {r[0]}")
    else:
        produto_codigo_atual = None
        produto_var.set("Produto não encontrado")
        preco_var.set("—")
        quantidade_var.set("Quantidade: —")
        codigo_var.set("Código: —")

    codigo_entry_var.set("")


entry_busca.bind("<Return>", consultar)

# ================= VENDER PRODUTO =================
def vender_produto():
    global produto_codigo_atual, produto_qtd_atual

    if not produto_codigo_atual:
        messagebox.showwarning("Atenção", "Pesquise um produto primeiro")
        return

    janela_qtd = tk.Toplevel(janela)
    janela_qtd.title("Quantidade")
    janela_qtd.geometry("250x150")

    tk.Label(janela_qtd, text="Quantidade para vender:").pack(pady=10)
    entry_qtd = tk.Entry(janela_qtd)
    entry_qtd.pack()

    def confirmar():
        global produto_qtd_atual

        try:
            qtd = int(entry_qtd.get())

            if qtd <= 0:
                raise ValueError

            estoque_atual = int(produto_qtd_atual)

            if qtd > estoque_atual:
                messagebox.showerror("Erro", "Estoque insuficiente")
                return

            nova_qtd = estoque_atual - qtd

            # Atualiza estoque
            cursor.execute(
                "UPDATE produtos SET quantidade=? WHERE codigo=?",
                (nova_qtd, produto_codigo_atual)
            )

            # -------- REGISTRAR VENDA --------
            data_hoje = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO vendas (codigo_produto, nome_produto, quantidade, preco, data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                produto_codigo_atual,
                produto_nome_atual,
                qtd,
                produto_preco_atual,
                data_hoje
            ))

            conn.commit()
            # ---------------------------------

            produto_qtd_atual = nova_qtd
            quantidade_var.set(f"Quantidade disponível: {nova_qtd}")

            messagebox.showinfo("Sucesso", "Venda realizada!")
            janela_qtd.destroy()

        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida")

    tk.Button(janela_qtd, text="Confirmar", command=confirmar).pack(pady=10)



# ================= LOGIN ADMIN =================
def login_admin(callback):
    login = tk.Toplevel(janela)
    login.title("Autenticação")
    login.geometry("350x250")
    login.configure(bg=COR_FUNDO)

    card = tk.Frame(login, bg=COR_CARD)
    card.pack(expand=True, padx=30, pady=30)

    tk.Label(card, text="Login Administrativo",
             bg=COR_CARD, font=("Segoe UI", 15, "bold")).pack(pady=10)

    entry_user = tk.Entry(card)
    entry_user.pack(fill="x", pady=5)

    entry_senha = tk.Entry(card, show="*")
    entry_senha.pack(fill="x", pady=5)

    def validar():
        senha_hash = hashlib.sha256(entry_senha.get().encode()).hexdigest()
        cursor.execute(
            "SELECT nivel FROM usuarios WHERE usuario=? AND senha=?",
            (entry_user.get(), senha_hash)
        )
        r = cursor.fetchone()
        if r and r[0].upper() == "ADMIN":
            login.destroy()
            callback()
        else:
            messagebox.showerror("Erro", "Acesso negado")

    tk.Button(card, text="ENTRAR",
              bg=COR_PRIMARIA, fg="white",
              command=validar).pack(fill="x", pady=15)

# ================= CRIAR USUÁRIO =================
def criar_usuario():
    t = tk.Toplevel(janela)
    t.title("Criar Usuário")
    t.geometry("450x400")
    t.configure(bg=COR_FUNDO)

    card = tk.Frame(t, bg=COR_CARD)
    card.pack(expand=True, padx=30, pady=30)

    tk.Label(card, text="Cadastro de Usuário",
             bg=COR_CARD, font=("Segoe UI", 15, "bold")).pack(pady=10)

    tk.Label(card, text="Usuário", bg=COR_CARD).pack(anchor="w")
    entry_user = tk.Entry(card)
    entry_user.pack(fill="x", pady=5)

    tk.Label(card, text="Senha", bg=COR_CARD).pack(anchor="w")
    entry_senha = tk.Entry(card, show="*")
    entry_senha.pack(fill="x", pady=5)

    tk.Label(card, text="Nível", bg=COR_CARD).pack(anchor="w")

    combo_nivel = ttk.Combobox(
        card,
        values=["admin", "operador"],
        state="readonly"
    )

    combo_nivel.pack(fill="x", pady=5)
    combo_nivel.current(0)

    def salvar():
        usuario = entry_user.get().strip()
        senha = entry_senha.get().strip()
        nivel = combo_nivel.get().lower()

        if not usuario or not senha or not nivel:
            messagebox.showwarning("Atenção", "Preencha todos os campos")
            return

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        try:
            cursor.execute("""
                INSERT INTO usuarios (usuario, senha, nivel)
                VALUES (?, ?, ?)
            """, (usuario, senha_hash, nivel))
            conn.commit()

            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
            t.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe")

    tk.Button(card, text="SALVAR",
              bg=COR_SUCESSO, fg="white",
              command=salvar).pack(fill="x", pady=20)

# ================= CADASTRAR =================
def cadastrar_produto():
    t = tk.Toplevel(janela)
    t.title("Cadastrar Produto")
    t.geometry("500x420")
    t.configure(bg=COR_FUNDO)

    card = tk.Frame(t, bg=COR_CARD)
    card.pack(expand=True, padx=30, pady=30)

    entries = {}

    for campo in ["Código", "Nome", "Preço", "Quantidade"]:
        tk.Label(card, text=campo, bg=COR_CARD).pack(anchor="w")
        e = tk.Entry(card)
        e.pack(fill="x", pady=5)
        entries[campo] = e

    def salvar():
        try:
            cursor.execute(
                "INSERT INTO produtos VALUES (?, ?, ?, ?)",
                (entries["Código"].get(),
                 entries["Nome"].get(),
                 float(entries["Preço"].get()),
                 int(entries["Quantidade"].get()))
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado")
            t.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(card, text="SALVAR",
              bg=COR_SUCESSO, fg="white",
              command=salvar).pack(fill="x", pady=20)

# ================= EDITAR =================
def editar_produto():
    if not produto_codigo_atual:
        messagebox.showwarning("Atenção", "Pesquise um produto primeiro")
        return

    def abrir():
        t = tk.Toplevel(janela)
        t.title("Editar Produto")
        t.geometry("500x420")
        t.configure(bg=COR_FUNDO)

        card = tk.Frame(t, bg=COR_CARD)
        card.pack(expand=True, padx=30, pady=30)

        nome = tk.Entry(card)
        nome.pack(fill="x")
        nome.insert(0, produto_nome_atual)

        preco = tk.Entry(card)
        preco.pack(fill="x", pady=5)
        preco.insert(0, produto_preco_atual)

        qtd = tk.Entry(card)
        qtd.pack(fill="x", pady=5)
        qtd.insert(0, produto_qtd_atual)

        def salvar():
            cursor.execute(
                "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE codigo=?",
                (nome.get(), float(preco.get()), int(qtd.get()), produto_codigo_atual)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado")
            t.destroy()

        tk.Button(card, text="SALVAR",
                  bg=COR_ALERTA, fg="white",
                  command=salvar).pack(fill="x", pady=20)

    login_admin(abrir)

# ================= RELATORIO =================
def relatorio_diario():
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT codigo_produto, nome_produto, 
               SUM(quantidade), 
               SUM(quantidade * preco)
        FROM vendas
        WHERE data = ?
        GROUP BY codigo_produto, nome_produto
    """, (data_hoje,))

    resultados = cursor.fetchall()

    if not resultados:
        messagebox.showinfo("Relatório", "Nenhuma venda hoje.")
        return

    # Abrir janela para escolher onde salvar
    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=f"relatorio_{data_hoje}.pdf",
        filetypes=[("Arquivo PDF", "*.pdf")]
    )

    if not caminho:  # Se cancelar
        return

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import pagesizes
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate(caminho, pagesize=pagesizes.A4)

    elements = []
    styles = getSampleStyleSheet()

    # ===== LOGO NO TOPO =====
    logo = Image("LOGONCR2.png")
    logo.drawHeight = 60
    logo.drawWidth = 150
    logo.hAlign = 'CENTER'

    elements.append(logo)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>RELATÓRIO DIÁRIO DE VENDAS</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Data: {data_hoje}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    dados = [["Código", "Produto", "Quantidade", "Total (R$)"]]
    total_geral = 0

    for codigo, nome, qtd_total, valor_total in resultados:
        dados.append([
            codigo,
            nome,
            str(qtd_total),
            f"{valor_total:.2f}"
        ])
        total_geral += valor_total

    tabela = Table(dados, colWidths=[1.2 * inch, 2.5 * inch, 1.2 * inch, 1.5 * inch])

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(tabela)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(
        Paragraph(f"<b>TOTAL GERAL DO DIA: R$ {total_geral:.2f}</b>", styles["Heading2"])
    )

    doc.build(elements)

    messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso!")

# ================= BARRA INFERIOR =================
barra = tk.Frame(janela, bg="#D3D3D3")
barra.pack(fill="x", side="bottom", pady=10)

tk.Button(barra, text="Cadastrar Produto",
          bg="#ADD8E6", fg="black",
          command=lambda: login_admin(cadastrar_produto)
          ).pack(side="left", padx=20)

tk.Button(barra, text="Editar Produto",
          bg="#FFDE21", fg="black",
          command=editar_produto
          ).pack(side="left")

tk.Button(barra, text="Criar Usuário",
          bg="#10B981", fg="black",
          command=lambda: login_admin(criar_usuario)
          ).pack(side="left", padx=20)

tk.Button(barra, text="Vender",
          bg="#EF4444", fg="white",
          command=vender_produto
          ).pack(side="left", padx=10)

tk.Button(barra, text="Relatório Diário",
          bg="#2563EB", fg="white",
          command=relatorio_diario
          ).pack(side="left", padx=10)


# ================= FECHAR =================
def fechar():
    conn.close()
    janela.destroy()
# ================= TELA LOGIN =============
def login_inicial():
    login = tk.Toplevel()
    login.title("Login do Sistema")
    login.geometry("620x420")
    login.configure(bg=COR_FUNDO)
    login.grab_set()
    login.resizable(False, False)

    card = tk.Frame(login, bg=COR_CARD, bd=0)
    card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=360)

    # ===== LOGO =====
    try:
        logo_img = PILImage.open("LOGONCR2.png")
        logo_img = logo_img.resize((170, 90))
        logo_tk = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(card, image=logo_tk, bg=COR_CARD)
        logo_label.image = logo_tk
        logo_label.pack(pady=(20, 10))
    except:
        pass

    tk.Label(card,
             text="Acesso ao Sistema",
             bg=COR_CARD,
             fg=COR_TEXTO,
             font=("Segoe UI", 16, "bold")
             ).pack(pady=(5, 15))

    # ===== USUÁRIO =====
    tk.Label(card, text="Usuário",
             bg=COR_CARD,
             fg=COR_SUBTEXTO).pack(anchor="w", padx=40)

    entry_user = tk.Entry(card, font=("Segoe UI", 11))
    entry_user.pack(fill="x", padx=40, pady=(0, 10), ipady=5)

    # ===== SENHA =====
    tk.Label(card, text="Senha",
             bg=COR_CARD,
             fg=COR_SUBTEXTO).pack(anchor="w", padx=40)

    entry_senha = tk.Entry(card, show="*", font=("Segoe UI", 11))
    entry_senha.pack(fill="x", padx=40, pady=(0, 20), ipady=5)

    def validar():
        usuario = entry_user.get().strip()
        senha_digitada = entry_senha.get().strip()

        if not usuario or not senha_digitada:
            messagebox.showwarning("Atenção", "Preencha usuário e senha")
            return

        senha_hash = hashlib.sha256(senha_digitada.encode()).hexdigest()

        cursor.execute(
            "SELECT usuario, nivel FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha_hash)
        )

        resultado = cursor.fetchone()

        if resultado:
            global usuario_logado, usuario_nivel

            usuario_logado = resultado[0]
            usuario_nivel = resultado[1]

            usuario_label_var.set(f"👤 {usuario_logado} ({usuario_nivel})")

            login.destroy()
            janela.deiconify()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    botao = tk.Button(card,
                      text="ENTRAR",
                      bg=COR_PRIMARIA,
                      fg="white",
                      activebackground="#1E40AF",
                      relief="flat",
                      font=("Segoe UI", 11, "bold"),
                      command=validar)

    botao.pack(fill="x", padx=40, ipady=8)

    entry_senha.bind("<Return>", lambda event: validar())
    entry_user.focus()


janela.protocol("WM_DELETE_WINDOW", fechar)
janela.after(200, login_inicial)
janela.mainloop()
