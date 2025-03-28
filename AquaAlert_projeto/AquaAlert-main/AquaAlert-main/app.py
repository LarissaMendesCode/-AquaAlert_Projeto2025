from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from Calculadora import calcular_consumo, calcular_esgoto_fatura, calcular_esgoto, calcular_consumo_chuveiro, calcular_consumo_torneira, calcular_consumo_descarga

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('cadastro.db')

# Criação do banco de dados e tabela
def create_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            tempobanho REAL,
            qtdebanho INTEGER,
            tempo_torneira_maos REAL,
            qtdeusotorneiramaos INTEGER,
            tempo_torneira_escovardentes REAL,
            qtdeusotorneiradentes INTEGER,
            tempo_torneira_lavarlouça REAL,
            qtdeusotorneiralouça INTEGER,
            qtdedescarga INTEGER,
            volume REAL,
            categoria INTEGER,
            consumo_total REAL,
            fatura_total REAL
        )
    ''')
    conn.commit()
    conn.close()

# Função para armazenar os dados e cálculos no banco
def salvar_usuario(dados, consumo_total, fatura_total):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nome, tempobanho, qtdebanho, tempo_torneira_maos, 
        qtdeusotorneiramaos, tempo_torneira_escovardentes, qtdeusotorneiradentes, 
        tempo_torneira_lavarlouça, qtdeusotorneiralouça, qtdedescarga, volume, categoria, consumo_total, fatura_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dados['nome'], 
        dados['tempobanho'], 
        dados['qtdebanho'], 
        dados['tempo_torneira_maos'], 
        dados['qtdeusotorneiramaos'], 
        dados['tempo_torneira_escovardentes'], 
        dados['qtdeusotorneiradentes'], 
        dados['tempo_torneira_lavarlouça'], 
        dados['qtdeusotorneiralouça'], 
        dados['qtdedescarga'], 
        dados['volume'], 
        dados['categoria'], 
        consumo_total, 
        fatura_total
    ))
    conn.commit()
    conn.close()

# Página inicial (carrega o formulário)
@app.route('/')
def index():
    return render_template('cadastro.html')

# Processamento do cadastro – aceita GET (para exibir o formulário) e POST (para processar os dados)
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Coleta os dados do formulário
        dados = {
            'nome': request.form['nome'],
            'tempobanho': float(request.form['tempobanho']),
            'qtdebanho': int(request.form['qtdebanho']),
            'tempo_torneira_maos': float(request.form['tempo_torneira_maos']),
            'qtdeusotorneiramaos': int(request.form['qtdeusotorneiramaos']),
            'tempo_torneira_escovardentes': float(request.form['tempo_torneira_escovardentes']),
            'qtdeusotorneiradentes': int(request.form['qtdeusotorneiradentes']),
            'tempo_torneira_lavarlouça': float(request.form['tempo_torneira_lavarlouça']),
            'qtdeusotorneiralouça': int(request.form['qtdeusotorneiralouça']),
            'qtdedescarga': int(request.form['qtdedescarga']),
            'volume': float(request.form['volume']),
            'categoria': int(request.form['categoria'])
        }

        # Cálculo do consumo total
        consumo_chuveiro = calcular_consumo_chuveiro(dados['tempobanho'], dados['qtdebanho'])
        consumo_torneira = calcular_consumo_torneira(
            dados['tempo_torneira_maos'], 
            dados['qtdeusotorneiramaos'], 
            dados['tempo_torneira_escovardentes'], 
            dados['qtdeusotorneiradentes'], 
            dados['tempo_torneira_lavarlouça'], 
            dados['qtdeusotorneiralouça'], 
            1
        )
        consumo_descarga = calcular_consumo_descarga(dados['qtdedescarga'])
        consumo_total = consumo_chuveiro + consumo_torneira + consumo_descarga
        
        # Cálculo da fatura
        fatura_total = calcular_consumo(dados['categoria'], dados['volume']) + \
                       calcular_esgoto_fatura(dados['categoria'], calcular_esgoto(dados['volume']))
        
        # Salvar no banco de dados
        salvar_usuario(dados, consumo_total, fatura_total)
        
        # Redireciona para a página que exibe o resultado
        return redirect(url_for('resultado'))

    # Quando o método for GET, renderiza o formulário
    return render_template('cadastro.html')

# Página para exibir os resultados (último usuário cadastrado)
@app.route('/tabela')
def resultado():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY id DESC LIMIT 1")
    usuario = cursor.fetchone()
    conn.close()
    return render_template('tabela.html', usuario=usuario)

if __name__ == '__main__':
    create_db()
    app.run(debug=True, port=5001)

