import flet as ft
import sqlite3
import csv

# Criar banco de dados e tabela
def criar_banco():
    with sqlite3.connect("estudos.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                categoria TEXT,
                status TEXT,
                modalidade TEXT
            )
        """)
        conn.commit()

# Cores para status
def cor_status(status):
    from flet import Colors
    if status == "Pendente":
        return Colors.RED_400
    elif status == "Em andamento":
        return Colors.AMBER_400
    elif status == "Concluído":
        return Colors.GREEN_400
    return Colors.GREY_400

# Inserir item
def inserir_item(nome, categoria, status, modalidade):
    with sqlite3.connect("estudos.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO estudos (nome, categoria, status, modalidade) VALUES (?, ?, ?, ?)",
                       (nome, categoria, status, modalidade))
        conn.commit()

# Listar todos
def listar_itens():
    with sqlite3.connect("estudos.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudos")
        return cursor.fetchall()

# Deletar
def delete_item(item_id):
    with sqlite3.connect("estudos.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estudos WHERE id = ?", (item_id,))
        conn.commit()

# Editar
def update_item(item_id, nome, categoria, status, modalidade):
    with sqlite3.connect("estudos.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE estudos SET nome=?, categoria=?, status=?, modalidade=? WHERE id=?
        """, (nome, categoria, status, modalidade, item_id))
        conn.commit()

# Exportar para CSV
def exportar_csv():
    dados = listar_itens()
    with open("estudos_export.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Nome", "Categoria", "Status", "Modalidade"])
        writer.writerows(dados)

# App
def main(page: ft.Page):
    from flet import Icons, Colors

    page.title = "Controle de Estudos"
    criar_banco()

    nome = ft.TextField(label="Nome")
    categoria = ft.Dropdown(label="Categoria", options=[
        ft.dropdown.Option("Curso"),
        ft.dropdown.Option("Vídeo"),
        ft.dropdown.Option("Livro"),
        ft.dropdown.Option("Artigo"),
    ])
    status = ft.Dropdown(label="Status", options=[
        ft.dropdown.Option("Pendente"),
        ft.dropdown.Option("Em andamento"),
        ft.dropdown.Option("Concluído"),
    ])
    modalidade = ft.Dropdown(label="Modalidade", options=[
        ft.dropdown.Option("Presencial"),
        ft.dropdown.Option("Online"),
        ft.dropdown.Option("Youtube"),
        ft.dropdown.Option("Udemy"),
    ])

    filtro_categoria = ft.Dropdown(label="Filtrar por Categoria", options=[
        ft.dropdown.Option("Todos"),
        ft.dropdown.Option("Curso"),
        ft.dropdown.Option("Vídeo"),
        ft.dropdown.Option("Livro"),
        ft.dropdown.Option("Artigo"),
    ], value="Todos")

    filtro_status = ft.Dropdown(label="Filtrar por Status", options=[
        ft.dropdown.Option("Todos"),
        ft.dropdown.Option("Pendente"),
        ft.dropdown.Option("Em andamento"),
        ft.dropdown.Option("Concluído"),
    ], value="Todos")

    video_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=20,
        auto_scroll=True
    )

    def render_video_cards():
        video_list.controls.clear()
        itens = listar_itens()  # ou fetch_videos() se estiver usando essa função
        
        for item in itens:
            id_, titulo, categoria, status, modalidade = item
            
            # Aplique filtros se necessário
            if (filtro_categoria.value != "Todos" and categoria != filtro_categoria.value):
                continue
            if (filtro_status.value != "Todos" and status != filtro_status.value):
                continue
                
            video_list.controls.append(
                ft.Container(
                    bgcolor=cor_status(status),
                    border_radius=10,
                    padding=10,
                    content=ft.Row([
                        ft.Text(f"{titulo} ({categoria}, {status}, {modalidade})", expand=True),
                        ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, i=id_, t=titulo, c=categoria, s=status, m=modalidade: editar_item(i, t, c, s, m)),
                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, i=id_: deletar_item(i))
                    ])
                )
            )
        page.update()

    def adicionar_item(e):
        if not nome.value:
            return
        inserir_item(nome.value, categoria.value, status.value, modalidade.value)
        nome.value = ""
        render_video_cards()

    def deletar_item(item_id):
        delete_item(item_id)
        render_video_cards()

    def editar_item(item_id, n, c, s, m):
        nome.value = n
        categoria.value = c
        status.value = s
        modalidade.value = m

        def salvar(e):
            update_item(item_id, nome.value, categoria.value, status.value, modalidade.value)
            nome.value = ""
            botao_salvar.visible = False
            botao_adicionar.visible = True
            render_video_cards()

        botao_salvar.on_click = salvar
        botao_salvar.visible = True
        botao_adicionar.visible = False
        page.update()

    botao_adicionar = ft.ElevatedButton("Adicionar", on_click=adicionar_item)
    botao_salvar = ft.ElevatedButton("Salvar edição", visible=False)

    filtro_categoria.on_change = lambda e: render_video_cards()
    filtro_status.on_change = lambda e: render_video_cards()

    botao_exportar = ft.ElevatedButton("Exportar CSV", on_click=lambda e: exportar_csv())

    page.add(
        ft.Text("📚 Controle de Estudos", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([nome, categoria, status, modalidade]),
        ft.Row([botao_adicionar, botao_salvar, botao_exportar]),
        ft.Row([filtro_categoria, filtro_status]),
        ft.Container(
            content=video_list,
            height=400,  # Defina a altura desejada para a área de rolagem
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=10,
            padding=10,
            expand=True
        )
    )

    render_video_cards()

ft.app(target=main)
