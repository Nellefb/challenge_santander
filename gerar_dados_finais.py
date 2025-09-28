# --------------------------------------------------------------------------
# PROGRAMA BACK-END V4 (FINAL) - CHALLENGE FIAP SANTANDER
# Time: Data Wave
# Finalidade: Gerar dados com ALTA VARIÂNCIA E SAZONALIDADE para um
#             dashboard com aparência e comportamento realistas.
# --------------------------------------------------------------------------

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, date, timedelta

def executar_backend_final():
    """
    Função principal que gera os dados e aplica a lógica de classificação e variância avançada.
    """
    print("--- INICIANDO EXECUÇÃO DO BACK-END COM VARIÂNCIA E SAZONALIDADE ---")

    # --- 1. CONFIGURAÇÕES GERAIS ---
    fake = Faker('pt_BR')
    NUM_CLIENTES = 6633
    NUM_TRANSACOES = 60720
    DATA_INICIO = date(2015, 1, 1)
    DATA_FIM = date(2023, 12, 31) # Aumentando o período para o gráfico de tempo

    # --- NOVOS PESOS PARA MÁXIMA VARIÂNCIA ---

    # 1. Pesos por Setor (CNAE) - alguns são muito maiores que outros
    pesos_cnae = {
        'Comércio': 3.0, 'Fabril': 4.0, 'Serviços': 2.5, 'Telecomunicações': 1.8,
        'Saúde': 1.2, 'Agro': 0.7, 'Outro': 0.5
    }

    # 2. Pesos por Tipo de Transação (Popularidade e Valor)
    # PIX é muito frequente, Boleto tem valores maiores
    pesos_tipo_transacao = {
        'populacao': ['PIX', 'TED', 'BOLETO', 'SISTEMCO'],
        'pesos_popularidade': [0.65, 0.10, 0.20, 0.05], # 65% das transações serão PIX
        'multiplicador_valor': {'PIX': 0.8, 'TED': 1.2, 'BOLETO': 1.5, 'SISTEMCO': 1.0}
    }

    # 3. Pesos por Mês (Sazonalidade) - picos no meio e fim do ano
    pesos_sazonalidade = {
        1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2,
        7: 1.1, 8: 1.0, 9: 1.1, 10: 1.3, 11: 1.4, 12: 1.6
    }
    
    # --- GERAÇÃO DAS TABELAS (código similar, mas usando os pesos) ---
    print(f"-> Gerando dados para {NUM_CLIENTES} clientes (Tabela 1)...")
    # (O restante do código abaixo é a lógica que aplica todos esses pesos)
    
    lista_clientes = []
    for i in range(NUM_CLIENTES):
        cnae_cliente = random.choices(list(pesos_cnae.keys()), weights=list(pesos_cnae.values()), k=1)[0]
        peso_c = pesos_cnae[cnae_cliente]
        data_abertura = fake.date_between(start_date='-10y', end_date='-1y')
        saldo = round(random.uniform(-50000, 500000) * peso_c, 2)
        faturamento = abs(saldo * random.uniform(1.5, 10)) if saldo > 0 else random.uniform(10000, 2000000) * peso_c
        lista_clientes.append({'ID': i + 1, 'VL_FATU': round(faturamento, 2), 'VL_SLDO': saldo, 'DT_ABRT': data_abertura, 'DS_CNAE': cnae_cliente, 'DT_REFE': date(2023, 12, 31)})
    tabela1_df = pd.DataFrame(lista_clientes)
    
    print(f"-> Gerando {NUM_TRANSACOES} transações com variância...")
    lista_transacoes = []
    lista_ids_clientes = tabela1_df['ID'].tolist()
    total_dias = (DATA_FIM - DATA_INICIO).days
    
    tipos_de_transacao_gerados = random.choices(
        pesos_tipo_transacao['populacao'], 
        weights=pesos_tipo_transacao['pesos_popularidade'], 
        k=NUM_TRANSACOES
    )
    
    for i in range(NUM_TRANSACOES):
        id_pagador = random.choice(lista_ids_clientes)
        id_recebedor = random.choice(lista_ids_clientes)
        while id_pagador == id_recebedor:
            id_recebedor = random.choice(lista_ids_clientes)

        cnae_pagador = tabela1_df.loc[tabela1_df['ID'] == id_pagador, 'DS_CNAE'].iloc[0]
        
        data_transacao = DATA_INICIO + timedelta(days=random.randint(0, total_dias))
        tipo_transacao = tipos_de_transacao_gerados[i]

        # Aplicando todos os pesos para um valor final realista
        peso_c = pesos_cnae.get(cnae_pagador, 1.0)
        multiplicador_v = pesos_tipo_transacao['multiplicador_valor'].get(tipo_transacao, 1.0)
        peso_s = pesos_sazonalidade.get(data_transacao.month, 1.0)

        valor_base = random.uniform(50.0, 10000.0)
        valor_final = round(valor_base * peso_c * multiplicador_v * peso_s, 2)
        
        lista_transacoes.append({'ID_PGTO': id_pagador, 'ID_RCBE': id_recebedor, 'VL': valor_final, 'DS_TRAN': tipo_transacao, 'DT_REFE': data_transacao})
        
    tabela2_df = pd.DataFrame(lista_transacoes)

    # --- DATA SCIENCE E SALVAMENTO (sem alterações) ---
    print("-> Aplicando modelos de classificação...")
    def classificar_momento(row):
        anos_empresa = (date.today() - row['DT_ABRT']).days / 365.25
        if anos_empresa <= 2 and row['VL_FATU'] < 500000: return 'Início'
        if row['VL_FATU'] > 1500000 and row['VL_SLDO'] < 0: return 'Expansão'
        if anos_empresa > 5 and row['VL_FATU'] > 1000000 and row['VL_SLDO'] > 100000: return 'Maturidade'
        if row['VL_SLDO'] < -50000 and row['VL_FATU'] < 400000: return 'Declínio'
        return 'Maturidade'
    tabela1_df['Momento_Vida'] = tabela1_df.apply(classificar_momento, axis=1)
    pagadores_por_cliente = tabela2_df.groupby('ID_RCBE')['ID_PGTO'].nunique().reset_index()
    pagadores_por_cliente.rename(columns={'ID_PGTO': 'Qtd_Pagadores_Unicos'}, inplace=True)
    tabela1_df = pd.merge(tabela1_df, pagadores_por_cliente, left_on='ID', right_on='ID_RCBE', how='left').fillna(0)
    def classificar_dependencia(qtd_pagadores):
        if qtd_pagadores <= 2: return 'Alta Dependência'
        elif qtd_pagadores <= 5: return 'Média Dependência'
        else: return 'Baixa Dependência'
    tabela1_df['Nivel_Dependencia'] = tabela1_df['Qtd_Pagadores_Unicos'].apply(classificar_dependencia)
    tabela1_df.to_csv('base1_id.csv', index=False, encoding='utf-8-sig')
    tabela2_df.to_csv('base2_transacoes.csv', index=False, encoding='utf-8-sig')
    print("   ... Arquivos finais com alta variância e insights foram gerados.")
    print("\n--- EXECUÇÃO DO BACK-END FINALIZADA ---")

if __name__ == "__main__":
    executar_backend_final()