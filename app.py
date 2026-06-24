import streamlit as st
import pandas as pd
import sqlite3

# Configuração do banco de dados local (não depende do Google!)
def init_db():
    conn = sqlite3.connect('deposito.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, quantidade INTEGER, preco REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER, quantidade INTEGER, data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.title("🏗️ Gestão de Depósito de Construção")

# Menu Lateral
menu = st.sidebar.selectbox("Menu", ["Cadastrar Produto", "Registrar Venda", "Relatórios"])

if menu == "Cadastrar Produto":
    st.subheader("Novo Produto")
    nome = st.text_input("Nome do Material")
    qtd = st.number_input("Quantidade Inicial", min_value=0, value=10)
    preco = st.number_input("Preço de Venda (R$)", min_value=0.0, value=10.0)
    
    if st.button("Salvar Produto"):
        conn = sqlite3.connect('deposito.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, qtd, preco))
        conn.commit()
        conn.close()
        st.success(f"{nome} cadastrado com sucesso!")

elif menu == "Registrar Venda":
    st.subheader("Nova Venda")
    conn = sqlite3.connect('deposito.db')
    produtos = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    
    if not produtos.empty:
        prod_selecionado = st.selectbox("Selecione o Produto", produtos['nome'].tolist())
        qtd_venda = st.number_input("Quantidade Vendida", min_value=1, value=1)
        
        if st.button("Confirmar Venda"):
            prod_id = produtos[produtos['nome'] == prod_selecionado]['id'].values[0]
            qtd_atual = produtos[produtos['nome'] == prod_selecionado]['quantidade'].values[0]
            
            if qtd_atual >= qtd_venda:
                conn = sqlite3.connect('deposito.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd_venda, prod_id))
                cursor.execute("INSERT INTO vendas (produto_id, quantidade, data) VALUES (?, ?, date('now'))", (prod_id, qtd_venda))
                conn.commit()
                conn.close()
                st.success("Venda realizada com sucesso!")
            else:
                st.error("Estoque insuficiente!")
    else:
        st.warning("Nenhum produto cadastrado ainda.")

elif menu == "Relatórios":
    st.subheader("Histórico de Estoque e Vendas")
    conn = sqlite3.connect('deposito.db')
    st.write("### Produtos em Estoque")
    st.dataframe(pd.read_sql_query("SELECT nome, quantidade, preco FROM produtos", conn))
    
    st.write("### Histórico de Vendas")
    st.dataframe(pd.read_sql_query("""
        SELECT v.id, p.nome, v.quantidade, v.data 
        FROM vendas v 
        JOIN produtos p ON v.produto_id = p.id
    """, conn))
    conn.close()