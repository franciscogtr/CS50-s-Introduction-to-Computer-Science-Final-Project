from flask import Flask, request, render_template, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from datetime import datetime
import database as db
from helpers import login_required

# Inicializar a conexão com o banco de dados e criar tabelas se não existirem
db_instance = db.Database()
db_instance.initialize_db()
db_instance.create_tables()
db_instance.close_connection(None)

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Rotas da aplicação

# Home route
# A rota home deve ser sobrecarregada com o username da barbearia para mostrar os serviços fornecidos
# Padrão: /?barbearia=barbearia_username 
#exemplo: /?barbearia=cabra.macho_bs

@app.route("/")
def home():

    barbearia = request.args.get("barbearia")
    # print(barbearia)
    
    if barbearia:

        #Armazena a barbearia atual na sessão
        session["current_barber_shop"] = barbearia
        # Buscar serviços da barbearia no banco de dados
        db_instance.initialize_db()
        cursor = db_instance.execute("SELECT * FROM barbearia WHERE username = ?", (barbearia,))
        barbearia = cursor.fetchone()
        if not barbearia:
            db_instance.close_connection(None)
            mensagem = "Barbearia não encontrada"
            erro = "Por favor, verifique o link"
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        # print(barbearia)
        barbearia_id = barbearia[0]
        servicos = db_instance.execute("SELECT * FROM servicos WHERE barbeariaId = ? ORDER BY nome", (barbearia_id,))
        servicos = servicos.fetchall()

        db_instance.close_connection(None)
    else:
        
        mensagem = "Barbearia não especificada"
        erro = "Por favor, verifique o link ou registre uma barbearia"
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    

    return render_template("index.html", barbearia=barbearia, servicos=servicos)

# Add Barber route
@app.route("/adicionar_barbeiro", methods=["GET", "POST"])
def adicionar_barbeiro():
    if request.method == "GET":
        if not session.get("user_type") == "barbearia":
            mensagem = "Acesso negado."
            erro = "Apenas barbearias podem adicionar barbeiros."
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        return render_template("adicionar_barbeiro.html")
    
    # Se for POST, processar o formulário de adição de barbeiro
    else:
        # Obter dados do formulário
        nome = request.form.get("nome")
        sobrenome = request.form.get("sobrenome")
        cpf = request.form.get("cpf")
        username = request.form.get("username")
        password = request.form.get("password")
        hash_password = generate_password_hash(password)
        barbearia_id = session.get("user_id")
        nome_completo = f"{nome} {sobrenome}"

        # Cria a sintaxe do registro no banco de dados
        query = '''
        INSERT INTO barbeiros (nome, cpf, username, hash, barbeariaId)
        VALUES (?, ?, ?, ?, ?)
        '''

        # Inicializa, executa a inserção no banco de dados, e fecha a conexão
        db_instance.initialize_db()
        try:
            db_instance.execute(query, (nome_completo, cpf, username, hash_password, barbearia_id))
        except Exception as e:
            db_instance.close_connection(None)
            mensagem = "Erro ao adicionar barbeiro"
            erro = e
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        db_instance.close_connection(None)

        return redirect("/gerenciar_barbeiros")

@app.route("/adicionar_servico", methods=["GET", "POST"])
def adicionar_servico():
    if request.method == "GET":
        if not session.get("user_type") == "barbearia":
            mensagem = "Acesso negado."
            erro = "Apenas barbearias podem adicionar serviços."
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        return render_template("adicionar_servico.html")
    
    # Se for POST, processar o formulário de adição de serviço
    else:
        # Obter dados do formulário
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        barbearia_id = session.get("user_id")

        try:
            preco = float(preco)
        except ValueError as e:
            mensagem = "Valor inválido"
            erro = "Insira um valor válido para preço"
            return render_template("exception.html", mensagem=mensagem,erro=erro)

        # Cria a sintaxe do registro no banco de dados
        query = '''
        INSERT INTO servicos (nome, preco, barbeariaId)
        VALUES (?, ?, ?)
        '''

        # Inicializa, executa a inserção no banco de dados, e fecha a conexão
        db_instance.initialize_db()
        try:
            db_instance.execute(query, (nome, preco, barbearia_id))
        except Exception as e:
            db_instance.close_connection(None)
            mensagem = "Erro ao adicionar serviço"
            erro = e
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        db_instance.close_connection(None)

        return redirect("/gerenciar_servicos")

@app.route("/agenda_barbeiros", methods=["GET", "POST"])
@login_required
def agenda_barbeiros():
    if session.get("user_type") != "barbearia":
        mensagem = "Acesso negado"
        erro = "Apenas barbearias podem visualizar a agenda dos barbeiros."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    # Buscar agenda dos barbeiros associados à barbearia logada
    barbearia_id = session.get("user_id")
    db_instance.initialize_db()
    try:
        cursor = db_instance.execute("SELECT * FROM barbeiros WHERE barbeariaId = ?", (barbearia_id,))
        barbeiros = cursor.fetchall()
    except Exception as e:
        db_instance.close_connection()
        erro = e
        mensagem = "Não foi possível recuperar barbeiros à barbearia associada"
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    db_instance.close_connection(None)

    # print(barbeiros)
    return render_template("agenda_barbeiros.html", barbeiros=barbeiros)

# Update Barber route
@app.route("/atualizar_barbeiro", methods=["POST"])
@login_required
def atualizar_barbeiro():
    if session.get("user_type") != "barbearia":
        mensagem = "Acesso negado"
        erro = "Apenas barbearias podem atualizar barbeiros."
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    # Obter dados do formulário
    barbeiro_id = request.form.get("barbeiro_id")
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    username = request.form.get("username")
    password = request.form.get("password")
    hash_password = generate_password_hash(password)

    # Atualizar dados do barbeiro no banco de dados
    query = '''
    UPDATE barbeiros
    SET nome = ?, cpf = ?, username = ?, hash = ?
    WHERE id = ?
    '''

    db_instance.initialize_db()
    try:
        db_instance.execute(query, (nome, cpf, username, hash_password, barbeiro_id))
    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao atualizar barbeiro"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    db_instance.close_connection(None)

    return redirect("/gerenciar_barbeiros")

# Update Service route
@app.route("/atualizar_servico", methods=["POST"])
@login_required
def atualizar_servico():
    if session.get("user_type") != "barbearia":
        mensagem = "Acesso negado"
        erro = "Apenas barbearias podem atualizar serviços."
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    # Obter dados do formulário
    servico_id = request.form.get("servico_id")
    nome = request.form.get("nome")
    preco = request.form.get("preco")

    # print(servico_id, nome, preco)

    try:
        preco = float(preco)
    except ValueError:
        mensagem = "Preço Inválido"
        erro = "Por favor, insira um número válido para preço"
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    # Atualizar dados do serviço no banco de dados
    query = '''
    UPDATE servicos
    SET nome = ?, preco = ?
    WHERE id = ?
    '''

    db_instance.initialize_db()
    try:
        db_instance.execute(query, (nome, preco, servico_id))
    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao atualizar serviço"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    db_instance.close_connection(None)

    return redirect("/gerenciar_servicos")

@app.route("/confirmar_agendamento", methods=["POST"])
def confirmar_agendamento():

    # Obter dados do formulário
    horario = request.form.get("horario")
    data = request.form.get("data")
    barbeiro_id = request.form.get("barbeiro_id")
    servico_id = request.form.get("servico_id")
    barbearia_id = request.form.get("barbearia_id")
    data_agendada = f"{data} {horario}"
    data_agendada_obj = datetime.strptime(data_agendada, "%Y-%m-%d %H:%M")
    # data_agendamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Recuperar os dados referentes aos IDs fornecidos
    db_instance.initialize_db()
    try:

        cursor = db_instance.execute("SELECT * FROM barbeiros WHERE id = ?", (barbeiro_id,))
        barbeiro = cursor.fetchone()
        cursor = db_instance.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
        servico = cursor.fetchone()
        cursor = db_instance.execute("SELECT * FROM barbearia WHERE id = ?", (barbearia_id,))
        barbearia = cursor.fetchone()

    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao recuperar os IDs associados"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    db_instance.close_connection(None)

    return render_template("confirmar_agendamento.html", horario=horario, data=data, barbeiro=barbeiro, servico=servico, barbearia=barbearia, data_agendada=data_agendada_obj)

# Dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    if request.method == "GET":
        return render_template("dashboard.html")

# Deletar Barbearia
@app.route("/deletar_barbearia", methods=["GET", "POST"])
@login_required
def deletar_barbearia():
    if request.method == "GET":
        if session.get("user_type") != "barbearia":
            mensagem = "Acesso negado"
            erro =  "Apenas barbearias podem deletar barbearias"
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        # Obtém o nome da barbearia que será usado no template
        db_instance.initialize_db()
        try:
            cursor = db_instance.execute("SELECT nome_fantasia FROM barbearia WHERE id = ?", (session.get("user_id"),))
            nome_barbearia = cursor.fetchone()[0]
        except Exception as e:
            db_instance.close_connection(None)
            mensagem = "Erro ao buscar o nome da barbearia"
            erro = e
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        db_instance.close_connection(None)
        # print(nome_barbearia)
        return render_template("delete_barbearia.html", nome_barbearia=nome_barbearia)
    
    else:
        
        barbeariaId = session.get("user_id")
        print(barbeariaId)

        #Recupera as credenciais salvas no BD
        db_instance.initialize_db()
        
        try:
            cursor = db_instance.execute("SELECT username, hash FROM barbearia WHERE id = ?", (barbeariaId,))
            barbearia = cursor.fetchone()
            # print(barbearia)
            username = barbearia[0]
            passhash = barbearia[1]
            # print(username,passhash)

        except Exception as e:
            db_instance.close_connection(None)
            mensagem = "Barbearia não encontrada"
            erro = e
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        db_instance.close_connection(None)
        
        # Obtém os dados do formulário
        formUser = request.form.get("username")
        formPass = request.form.get("password")

        # Compara o formulário com o BD
        if username == formUser and check_password_hash(passhash, formPass):

            # Deletar todos os dados realcionados a Barbbearia cujo o id está na sessão
            db_instance.initialize_db()

            try:
                # DELETA OS AGENDAMENTOS ASSOCIADOS
                db_instance.execute("DELETE FROM agenda WHERE barbeariaId = ?", (barbeariaId,))
                # DELETA OS SERVICOS ASSOCIADOS
                db_instance.execute("DELETE FROM servicos WHERE barbeariaId = ?", (barbeariaId,))
                # DELETA OS BARBEIROS ASSOCIADOS
                db_instance.execute("DELETE FROM barbeiros WHERE barbeariaId = ?", (barbeariaId,))
                # DELETA A BARBEARIA
                db_instance.execute("DELETE FROM barbearia WHERE id = ?", (barbeariaId,))

            except Exception as e:
                mensagem = "Erro ao deletar as dependencias da Barbearia"
                erro = e
                return render_template("exception.html", mensagem=mensagem,erro=erro)
        else:
            mensagem = "Dados Inválidos"
            erro = "Verifique os dados submetidos via formulário"
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        return redirect("/logout")
    
# Editar barbeiro route
@app.route("/editar_barbeiro", methods=["POST"])
@login_required
def editar_barbeiro():
    if session.get("user_type") != "barbearia":
        mensagem = "Acesso negado"
        erro = "Apenas barbearias podem editar barbeiros."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    # Obter dados do formulário
    barbeiro_id = request.form.get("barbeiro_id")

    # Buscar dados do barbeiro no banco de dados
    db_instance.initialize_db()
    cursor = db_instance.execute("SELECT * FROM barbeiros WHERE id = ?", (barbeiro_id,))
    barbeiro = cursor.fetchone()
    db_instance.close_connection(None)

    if not barbeiro:
        mensagem = "Barbeiro não encontrado"
        erro = "Verifique os dados submetidos"
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    return render_template("editar_barbeiro.html", barbeiro=barbeiro)

# Editar Serviço route
@app.route("/editar_servico", methods=["POST"])
@login_required
def editar_servico():
    if session.get("user_type") != "barbearia":
        mensagem = "Acesso negado"
        erro = "Apenas barbearias podem editar serviços."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    # Obter dados do formulário
    servico_id = request.form.get("servico_id")

    # Buscar dados do serviço no banco de dados
    db_instance.initialize_db()
    cursor = db_instance.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
    servico = cursor.fetchone()
    db_instance.close_connection(None)

    if not servico:
        mensagem = "Serviço não encontrado."
        erro = "Verifique os dados submetidos"
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    return render_template("editar_servico.html", servico=servico)
    
# Login route
@app.route("/enter", methods=["GET", "POST"])
def entrar():

    if request.method == "GET":
        return render_template("enter.html")
    
    # Se for POST, processar o formulário de login
    else:

        # Obter dados do formulário
        username = request.form.get("username")
        password = request.form.get("password")
        print(username,password)

        # Cria as concultas e inicializa o banco de dados
        query1 = "SELECT * FROM barbearia WHERE username = ?"
        query2 = "SELECT * FROM barbeiros WHERE username = ?"
        query3 = "SELECT username FROM barbearia WHERE id = ?"

        db_instance.initialize_db()

        cursor = db_instance.execute(query1, (username,))

        # Retorna a primeira linha da consulta ou None se não houver resultados
        barbearia = cursor.fetchone()
        # print(barbearia)

        # Verificar se a barbearia existe e se a senha está correta
        if barbearia and check_password_hash(barbearia[5], password):
            session["user_id"] = barbearia[0]
            session["current_barber_shop"] = barbearia[4]
            session["user_type"] = "barbearia"
            db_instance.close_connection(None)
            return redirect("/dashboard")
        else:
            cursor = db_instance.execute(query2, (username,))
            barbeiro = cursor.fetchone()
            print(barbeiro)
            
            # Verificar se o barbeiro existe e se a senha está correta
            if barbeiro and check_password_hash(barbeiro[4], password):
                session["user_id"] = barbeiro[0]
                session["current_barber_shop"] = db_instance.execute(query3, (barbeiro[5],)).fetchone()[0]
                session["user_type"] = "barbeiro"
                db_instance.close_connection(None)
                return redirect("/dashboard")
            else:
                db_instance.close_connection(None)
                mensagem = "Nome de usuário ou senha incorretos."
                erro = "Verifique as credenciais submetidas"
                return render_template("exception.html", mensagem=mensagem,erro=erro)

# Agendar Barbeiro route
@app.route("/escolher_barbeiro", methods=["GET", "POST"])
def escolher_barbeiro():
    if request.method == "GET":
        return redirect("/?barbearia=" + session.get("current_barber_shop"))
    
    # Obter dados do formulário
    servico_id = request.form.get("servico_id")
    barbearia_id = request.form.get("barbearia_id")

    # Buscar barbeiros associados à barbearia logada
    db_instance.initialize_db()

    try:
        cursor = db_instance.execute("SELECT * FROM barbeiros WHERE barbeariaId = ? ORDER BY nome ASC", (barbearia_id,))
        barbeiros = cursor.fetchall()
    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao buscar barbeiros"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    db_instance.close_connection(None)

    # print(servico_id)
    # print(barbeiros)
    return render_template("escolher_barbeiro.html", barbeiros=barbeiros, servico_id=servico_id)

# Escolher Data route
@app.route("/escolher_data", methods=["POST", "GET"])
def escolher_data():
    if request.method == "GET":
        return redirect("/?barbearia=" + session.get("current_barber_shop"))
    
    # Obter dados do formulário
    servico_id = request.form.get("servico_id")
    barbeiro_id = request.form.get("barbeiro_id")
    barbearia_id = request.form.get("barbearia_id")
    hoje = datetime.now().date()
    limite = hoje.replace(day=hoje.day + 6)

    print(servico_id)
    print(barbeiro_id)
    return render_template("escolher_data.html", servico_id=servico_id, barbeiro_id=barbeiro_id, barbearia_id=barbearia_id, hoje=hoje, limite=limite)

@app.route("/escolher_horario", methods=["POST"])
def escolher_horario():
    # Obter dados do formulário
    servico_id = request.form.get("servico_id")
    barbeiro_id = request.form.get("barbeiro_id")
    data = request.form.get("data")
    barbearia_id = request.form.get("barbearia_id")

    # Validar a data
    data = datetime.strptime(data, "%Y-%m-%d").date()

    if not data:
        mensagem = "Data inválida."
        erro = "Por favor, insira uma data válida."
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    if data < datetime.now().date():
        mensagem = "Data inválida."
        erro = "Por favor, escolha uma data futura."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    if data > datetime.now().date().replace(day=datetime.now().day + 6):
        mensagem = "Data inválida."
        erro = "Por favor, escolha uma data dentro de uma semana."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    if data.weekday() > 5:
        mensagem = "Data inválida."
        erro = "Por favor, escolha um dia dentro do funcionamento (segunda a sabado)."
        return render_template("exception.html", mensagem=mensagem,erro=erro)

    # print(f"Serviço ID: {servico_id}")
    # print(f"Barbeiro ID: {barbeiro_id}")
    # print(f"Data: {data}")
    # print(f"Barbearia ID: {barbearia_id}")

    # Obtem os horários disponíveis para o barbeiro na data selecionada
    db_instance.initialize_db()
    query = '''
    SELECT * FROM agenda WHERE barbeariaId = ? AND barbeiroId = ? AND dataAgendada LIKE ?
    '''

    cursor = db_instance.execute(query, (barbearia_id, barbeiro_id, f"{data}%"))
    horarios_agendados = cursor.fetchall()
    db_instance.close_connection(None)

    # Extrai apenas os horários agendados da consulta
    print(horarios_agendados)
    horarios_agendados = [registro[6] for registro in horarios_agendados]
    print(horarios_agendados)
    horarios_disponiveis = []
    horarios_formatados = [] # Lista para armazenar horários formatados
    
    for hora in range(8, 18 + 1):
        if data == datetime.now().date() and hora <= datetime.now().hour:
            continue  # Pula horários já passados no dia atual
        horario_1 = f"{data} {hora:02d}:00:00"
        horario_2 = f"{data} {hora:02d}:30:00"

        if horario_1 not in horarios_agendados:
            horarios_disponiveis.append(horario_1)
            horarios_formatados.append(f"{hora:02d}:00")  # Adiciona horário formatado  
        if horario_2 not in horarios_agendados and hora != 18:
            horarios_disponiveis.append(horario_2)
            horarios_formatados.append(f"{hora:02d}:30")  # Adiciona horário formatado


    # print(horarios_disponiveis)

    return render_template("escolher_horario.html", servico_id=servico_id, barbeiro_id=barbeiro_id, data=data, barbearia_id=barbearia_id, horarios_formatados=horarios_formatados)

@app.route("/finalizar_agendamento", methods=["POST"])
def finalizar_agendamento():
    #Obtem os dados do formulário
    barbearia_id = request.form.get("barbearia_id")
    barbeiro_id = request.form.get("barbeiro_id")
    servico_id = request.form.get("servico_id")
    data_agendada = request.form.get("data_agendada")
    data_agendamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nome_cliente = request.form.get("nome_cliente")

    if nome_cliente is None or nome_cliente.strip() == "":
        mensagem = "Informe seu nome"
        erro = "Nome do cliente não pode ser vazio."
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    # Insere o agendamento no banco de dados
    query = '''
    INSERT INTO agenda (nomeCliente, barbeariaId, barbeiroId, servicoId, dataAgendamento, dataAgendada)
    VALUES (?, ?, ?, ?, ?, ?)
    '''

    db_instance.initialize_db()
    try:
        db_instance.execute(query, (nome_cliente, barbearia_id, barbeiro_id, servico_id, data_agendamento, data_agendada))
    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao finalizar agendamento"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    db_instance.close_connection(None)

    return render_template("agendamento_finalizado.html", nome_cliente=nome_cliente)

# Gerenciar Barbeiros route
@app.route("/gerenciar_barbeiros", methods=["GET", "POST"])
@login_required
def gerenciar_barbeiros():
    if request.method == "GET":
        if session.get("user_type") != "barbearia":
            mensagem = "Acesso negado"
            erro = "Apenas barbearias podem gerenciar barbeiros."
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        # Buscar barbeiros associados à barbearia logada
        barbearia_id = session.get("user_id")
        db_instance.initialize_db()
        cursor = db_instance.execute("SELECT * FROM barbeiros WHERE barbeariaId = ? ORDER BY nome ASC", (barbearia_id,))
        barbeiros = cursor.fetchall()
        db_instance.close_connection(None)

        return render_template("gerenciar_barbeiros.html", barbeiros=barbeiros)
    
    # Se for POST, processar a edição ou remoção de barbeiros
    else:
        # TODO: Implementar lógica para editar ou remover barbeiros
        action = request.form.get("action")
        barbeiro_id = request.form.get("barbeiro_id")
        # print(action, barbeiro_id)
        
        if action == "deletar":
            # Deletar barbeiro do banco de dados
            db_instance.initialize_db()

            try:
                db_instance.execute("DELETE FROM agenda WHERE id = ?", (barbeiro_id,))
                db_instance.execute("DELETE FROM barbeiros WHERE id = ?", (barbeiro_id,))
            except Exception as e:
                db_instance.close_connection(None)
                mensagem = "Erro ao deletar barbeiro"
                erro = e
                return render_template("exception.html", mensagem=mensagem,erro=erro)
            db_instance.close_connection(None)

            return redirect("/gerenciar_barbeiros")
        else:
            mensagem = "Ação inválida"
            erro = "Submeta uma ação válida"
            return render_template("exception.html", mensagem=mensagem,erro=erro)

#Gerenciar Serviços route
@app.route("/gerenciar_servicos", methods=["GET", "POST"])
@login_required
def gerenciar_servicos():
    if request.method == "GET":
        if session.get("user_type") != "barbearia":
            mensagem = "Acesso negado"
            erro =  "Apenas barbearias podem gerenciar serviços."
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        # Buscar serviços associados à barbearia logada
        barbearia_id = session.get("user_id")
        db_instance.initialize_db()
        cursor = db_instance.execute("SELECT * FROM servicos WHERE barbeariaId = ? ORDER BY nome ASC", (barbearia_id,))
        servicos = cursor.fetchall()
        db_instance.close_connection(None)

        return render_template("gerenciar_servicos.html", servicos=servicos)
    
    # Se for POST, processar a adição, edição ou remoção de serviços
    else:
        action = request.form.get("action")
        servico_id = request.form.get("servico_id")
        
        if action == "deletar":
            # Deletar serviço do banco de dados
            db_instance.initialize_db()

            try:
                db_instance.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
            except Exception as e:
                db_instance.close_connection(None)
                return f"Erro ao deletar serviço: {e}"
            db_instance.close_connection(None)

            return redirect("/gerenciar_servicos")
        else:
            return "Ação inválida."        

# Logout route
@app.route("/logout")
def logout():
    barbearia = session.get("current_barber_shop")
    session.clear()
    return redirect(f"/?barbearia={barbearia}")

# Register Barbearia route
@app.route("/register", methods=["GET", "POST"])
def registrar():

    if request.method == "GET":
        return render_template("register.html")
    
    # Se for POST, processar o formulário de registro
    else:
        # Obter dados do formulário
        cnpj = request.form.get("cnpj")
        razao_social = request.form.get("razao_social")
        nome_fantasia = request.form.get("nome_fantasia")
        username = request.form.get("username")
        password = request.form.get("password")
        hash_password = generate_password_hash(password)
        
        # Cria o registro no banco de dados
        query = '''
        INSERT INTO barbearia (cnpj, razao_social, nome_fantasia, username, hash)
        VALUES (?, ?, ?, ?, ?)
        '''
        db_instance.initialize_db()
        
        try:
            db_instance.execute(query, (cnpj, razao_social, nome_fantasia, username, hash_password))
        except Exception as e:
            db_instance.close_connection(None)
            mensagem = "Erro ao registrar"
            erro = e
            return render_template("exception.html", mensagem=mensagem,erro=erro)
        
        db_instance.close_connection(None)

        return redirect("/dashboard")
    
    
@app.route("/ver_agenda", methods=["POST"])
@login_required
def ver_agenda():
    barbeiroId = request.form.get("barbeiro_id")
    # print(barbeiroId)
    query = "SELECT * FROM agenda WHERE barbeiroId = ? ORDER BY dataAgendada"
    query2 = "SELECT nome FROM barbeiros WHERE id = ?"
    query3 = "SELECT nome FROM servicos WHERE id = ?"
    # Busca a agenda desse barbeiro no BD
    db_instance.initialize_db()

    try:
        cursor = db_instance.execute(query,(barbeiroId,))
        agendaBarbeiro = cursor.fetchall()
        cursor = db_instance.execute(query2,(barbeiroId,))
        nomeBarbeiro = cursor.fetchone()[0]
        
    except Exception as e:
        db_instance.close_connection(None)
        mensagem = "Erro ao buscar agendamentos"
        erro = e
        return render_template("exception.html", mensagem=mensagem,erro=erro)
    
    
    db_instance.close_connection(None)
    # Tupla que mantem os dias aa semana
    enumSemana = ("Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado")
    horariosAgendados = []

    db_instance.initialize_db()

    for registro in agendaBarbeiro:
        # Extrai a data e a converte em string
        data = datetime.strptime(registro[6], "%Y-%m-%d %H:%M:%S").date()
        horario = datetime.strptime(registro[6], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        servicoId = int(registro[4])
        cursor = db_instance.execute(query3,(servicoId,))
        servico = cursor.fetchone()[0]
        # Coleta apenas agendamentos a partir do dia atual
        if data < datetime.now().date():
            continue
        diaSemana = data.isoweekday()
        # print(diaSemana)
        # print(horario)
        dict = {
            "nome_cliente": registro[1],
            "servico": servico,
            "dia_da_semana": enumSemana[diaSemana],
            "data_agendada": data.strftime("%d/%m/%Y"),
            "horario_agendado": horario
        }

        
        horariosAgendados.append(dict)
        # print(nomeBarbeiro)
    db_instance.close_connection(None)
    print(horariosAgendados)

    return render_template("ver_agenda.html", horariosAgendados=horariosAgendados, nomeBarbeiro=nomeBarbeiro)