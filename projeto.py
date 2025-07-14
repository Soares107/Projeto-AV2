import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib

conn = sqlite3.connect('usuarios.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )
''')
conn.commit()

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario():
    nome = entry_nome.get()
    email = entry_email.get()
    senha = entry_senha.get()

    if not nome or not email or not senha:
        messagebox.showwarning("Erro", "Preencha todos os campos.")
        return

    senha_hash = criptografar_senha(senha)

    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                       (nome, email, senha_hash))
        conn.commit()
        listar_usuarios()
        limpar_campos()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Email já cadastrado.")

def listar_usuarios():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT id, nome, email FROM usuarios")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_senha.delete(0, tk.END)

def excluir_usuario():
    item = tree.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um usuário.")
        return
    user_id = tree.item(item, "values")[0]
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    listar_usuarios()
    limpar_campos()
    messagebox.showinfo("Sucesso", "Usuário excluído.")

def preencher_campos(event):
    item = tree.selection()
    if item:
        user = tree.item(item, "values")
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, user[1])
        entry_email.delete(0, tk.END)
        entry_email.insert(0, user[2])
        entry_senha.delete(0, tk.END)

def editar_usuario():
    item = tree.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um usuário.")
        return

    user_id = tree.item(item, "values")[0]
    nome = entry_nome.get()
    email = entry_email.get()
    senha = entry_senha.get()

    if not nome or not email:
        messagebox.showwarning("Erro", "Preencha nome e email.")
        return

    if senha:
        senha_hash = criptografar_senha(senha)
        cursor.execute("UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id = ?",
                       (nome, email, senha_hash, user_id))
    else:
        cursor.execute("UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
                       (nome, email, user_id))

    conn.commit()
    listar_usuarios()
    limpar_campos()
    messagebox.showinfo("Sucesso", "Usuário atualizado.")

root = tk.Tk()
root.title("Cadastro de Usuários")
root.geometry("600x450")

tk.Label(root, text="Nome").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_nome = tk.Entry(root, width=40)
entry_nome.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Email").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_email = tk.Entry(root, width=40)
entry_email.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Senha").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_senha = tk.Entry(root, show="*", width=40)
entry_senha.grid(row=2, column=1, padx=10, pady=5)

frame_botoes = tk.Frame(root)
frame_botoes.grid(row=3, column=0, columnspan=2, pady=10)

tk.Button(frame_botoes, text="Cadastrar", command=cadastrar_usuario).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes, text="Editar", command=editar_usuario).grid(row=0, column=1, padx=5)
tk.Button(frame_botoes, text="Excluir", command=excluir_usuario).grid(row=0, column=2, padx=5)

columns = ("ID", "Nome", "Email")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
tree.bind("<<TreeviewSelect>>", preencher_campos)

listar_usuarios()

root.mainloop()