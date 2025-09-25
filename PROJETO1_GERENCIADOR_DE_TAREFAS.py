import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId

class GerenciadorTarefasApp:

    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Gerenciador de Tarefas")
        self.janela.geometry("950x700")
        self.janela.configure(bg="#f0f0f0")

        self.cliente = MongoClient("mongodb://localhost:27017/")
        self.bd = self.cliente["gerenciador_tarefas_db"]
        self.colecao = self.bd["tarefas"]

        estilo = ttk.Style()
        estilo.theme_use('default')

        estilo.configure("Treeview",
                         background="#ffffff",
                         foreground="black",
                         rowheight=25,
                         fieldbackground="#ffffff",
                         font=("Arial", 11))

        estilo.configure("Treeview.Heading",
                         font=("Arial", 12, "bold"))

        estilo.map("Treeview",
                   background=[("selected", "black")],
                   foreground=[("selected", "white")])

        quadro_entrada = tk.Frame(self.janela, bg="#f0f0f0")
        quadro_entrada.pack(pady=10, padx=10, fill='x')

        rotulo_titulo = tk.Label(quadro_entrada,
                                 text="Título da Tarefa:",
                                 font=("Arial", 12),
                                 bg="#f0f0f0")
        rotulo_titulo.grid(row=0, column=0, sticky='e', padx=5, pady=5)

        self.entrada_titulo = tk.Entry(quadro_entrada,
                                       width=55,
                                       font=("Arial", 11))
        self.entrada_titulo.grid(row=0, column=1, columnspan=3,
                                 sticky='w', pady=5, padx=5)

        rotulo_descricao = tk.Label(quadro_entrada,
                                    text="Descrição da Tarefa:",
                                    font=("Arial", 12),
                                    bg="#f0f0f0")
        rotulo_descricao.grid(row=1, column=0, sticky='ne', padx=5, pady=5)

        self.texto_descricao = tk.Text(quadro_entrada,
                                       width=53,
                                       height=5,
                                       font=("Arial", 11))
        self.texto_descricao.grid(row=1, column=1, columnspan=3,
                                  sticky='w', pady=5, padx=5)

        rotulo_status = tk.Label(quadro_entrada,
                                 text="Status:",
                                 font=("Arial", 12),
                                 bg="#f0f0f0")
        rotulo_status.grid(row=2, column=0, sticky='e', padx=5, pady=5)

        self.var_status = tk.StringVar()
        self.combo_status = ttk.Combobox(quadro_entrada,
                                         textvariable=self.var_status,
                                         values=["Pendente", "Concluída"],
                                         state='readonly',
                                         font=("Arial", 11))
        self.combo_status.grid(row=2, column=1, pady=5, padx=5)
        self.combo_status.current(0)

        quadro_botoes = tk.Frame(self.janela, bg="#f0f0f0")
        quadro_botoes.pack(pady=10)

        botao_adicionar = tk.Button(quadro_botoes,
                                    text="Adicionar Tarefa",
                                    command=self.adicionar_tarefa,
                                    bg="#a5d6a7",
                                    font=("Arial", 11, "bold"),
                                    width=18)
        botao_adicionar.grid(row=0, column=0, padx=10, pady=5)

        botao_atualizar = tk.Button(quadro_botoes,
                                    text="Atualizar Tarefa",
                                    command=self.atualizar_tarefa,
                                    bg="#fff59d",
                                    font=("Arial", 11, "bold"),
                                    width=18)
        botao_atualizar.grid(row=0, column=1, padx=10, pady=5)

        botao_excluir = tk.Button(quadro_botoes,
                                  text="Excluir Tarefa",
                                  command=self.excluir_tarefa,
                                  bg="#ef9a9a",
                                  font=("Arial", 11, "bold"),
                                  width=18)
        botao_excluir.grid(row=0, column=2, padx=10, pady=5)

        quadro_filtro = tk.Frame(self.janela, bg="#f0f0f0")
        quadro_filtro.pack(pady=10)

        rotulo_filtro = tk.Label(quadro_filtro,
                                 text="Filtrar por Status:",
                                 font=("Arial", 12),
                                 bg="#f0f0f0")
        rotulo_filtro.grid(row=0, column=0, padx=5)

        self.var_filtro = tk.StringVar()
        self.combo_filtro = ttk.Combobox(quadro_filtro,
                                         textvariable=self.var_filtro,
                                         values=["Todos", "Pendente", "Concluída"],
                                         state='readonly',
                                         font=("Arial", 11))
        self.combo_filtro.current(0)
        self.combo_filtro.grid(row=0, column=1, padx=5)

        botao_filtro = tk.Button(quadro_filtro,
                                 text="Aplicar Filtro",
                                 command=self.aplicar_filtro,
                                 bg="#81d4fa",
                                 font=("Arial", 11, "bold"),
                                 width=15)
        botao_filtro.grid(row=0, column=2, padx=5)

        quadro_arvore = tk.Frame(self.janela, bg="#f0f0f0")
        quadro_arvore.pack(pady=20, fill='both', expand=True)

        barra_rolagem = tk.Scrollbar(quadro_arvore, orient='vertical')
        barra_rolagem.pack(side=tk.RIGHT, fill=tk.Y)

        self.arvore_tarefas = ttk.Treeview(quadro_arvore,
                                           columns=("Título", "Descrição", "Status"),
                                           show="headings",
                                           height=15,
                                           yscrollcommand=barra_rolagem.set)

        self.arvore_tarefas.heading("Título", text="Título")
        self.arvore_tarefas.heading("Descrição", text="Descrição")
        self.arvore_tarefas.heading("Status", text="Status")

        self.arvore_tarefas.column("Título", width=220)
        self.arvore_tarefas.column("Descrição", width=480)
        self.arvore_tarefas.column("Status", width=120)

        self.arvore_tarefas.bind("<<TreeviewSelect>>", self.ao_selecionar_tarefa)
        self.arvore_tarefas.pack(pady=10, padx=10, fill='both', expand=True)

        barra_rolagem.config(command=self.arvore_tarefas.yview)

        self.id_tarefa_selecionada = None
        self.carregar_tarefas()

    def carregar_tarefas(self, filtro_status=None):
        for item in self.arvore_tarefas.get_children():
            self.arvore_tarefas.delete(item)

        consulta = {}
        if filtro_status and filtro_status in ["Pendente", "Concluída"]:
            consulta = {"status": filtro_status}

        tarefas = self.colecao.find(consulta)

        for tarefa in tarefas:
            self.arvore_tarefas.insert("", tk.END,
                                       values=(tarefa["titulo"], tarefa["descricao"], tarefa["status"]),
                                       iid=str(tarefa["_id"]))

    def adicionar_tarefa(self):
        titulo = self.entrada_titulo.get().strip()
        descricao = self.texto_descricao.get("1.0", tk.END).strip()
        status = self.var_status.get()

        if not titulo:
            messagebox.showwarning("Aviso", "O título da tarefa não pode estar vazio.")
            return

        nova_tarefa = {
            "titulo": titulo,
            "descricao": descricao,
            "status": status
        }

        self.colecao.insert_one(nova_tarefa)
        self.carregar_tarefas()
        self.limpar_campos_entrada()
        messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")

    def limpar_campos_entrada(self):
        self.entrada_titulo.delete(0, tk.END)
        self.texto_descricao.delete("1.0", tk.END)
        self.var_status.set("Pendente")

    def atualizar_tarefa(self):
        if not self.id_tarefa_selecionada:
            messagebox.showwarning("Aviso", "Nenhuma tarefa selecionada para atualizar.")
            return

        titulo = self.entrada_titulo.get().strip()
        descricao = self.texto_descricao.get("1.0", tk.END).strip()
        status = self.var_status.get()

        if not titulo:
            messagebox.showwarning("Aviso", "O título da tarefa não pode estar vazio.")
            return

        dados_atualizacao = {
            "$set": {
                "titulo": titulo,
                "descricao": descricao,
                "status": status
            }
        }

        self.colecao.update_one({"_id": ObjectId(self.id_tarefa_selecionada)}, dados_atualizacao)
        self.carregar_tarefas()
        self.limpar_campos_entrada()
        self.id_tarefa_selecionada = None
        messagebox.showinfo("Sucesso", "Tarefa atualizada com sucesso!")

    def excluir_tarefa(self):
        if not self.id_tarefa_selecionada:
            messagebox.showwarning("Aviso", "Nenhuma tarefa selecionada para excluir.")
            return

        confirmar = messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir esta tarefa?")
        if confirmar:
            self.colecao.delete_one({"_id": ObjectId(self.id_tarefa_selecionada)})
            self.carregar_tarefas()
            self.limpar_campos_entrada()
            self.id_tarefa_selecionada = None
            messagebox.showinfo("Sucesso", "Tarefa excluída com sucesso!")

    def aplicar_filtro(self):
        filtro_escolhido = self.var_filtro.get()
        if filtro_escolhido == "Todos":
            self.carregar_tarefas()
        else:
            self.carregar_tarefas(filtro_status=filtro_escolhido)

    def ao_selecionar_tarefa(self, event):
        selecionado = self.arvore_tarefas.selection()
        if selecionado:
            self.id_tarefa_selecionada = selecionado[0]
            dados_tarefa = self.colecao.find_one({"_id": ObjectId(self.id_tarefa_selecionada)})
            if dados_tarefa:
                self.entrada_titulo.delete(0, tk.END)
                self.entrada_titulo.insert(tk.END, dados_tarefa["titulo"])
                self.texto_descricao.delete("1.0", tk.END)
                self.texto_descricao.insert(tk.END, dados_tarefa["descricao"])
                self.var_status.set(dados_tarefa["status"])

janela_principal = tk.Tk()
app = GerenciadorTarefasApp(janela_principal)
janela_principal.mainloop()