# --------------------------------------------------------------------------
# PROGRAMA BACK-END - CHALLENGE FIAP SANTANDER
# Time: Data Wave
# Finalidade: Gerar dados sintéticos com alta variância e sazonalidade
#             para um dashboard realista.
# --------------------------------------------------------------------------

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, date, timedelta

# Parâmetros centralizados para controlar a simulação
CONFIG = {
    'num_clientes': 6000,
    'num_transacoes': 60000,
    'data_inicio': date(2015, 1, 1),
    'data_fim': date(2023, 12, 31),
    'pesos_cnae': {
        'Comércio': 3.0, 'Fabril': 4.0, 'Serviços': 2.5, 'Telecomunicações': 1.8,
        'Saúde': 1.2, 'Agro': 0.7, 'Outro': 0.5
    },
    'pesos_tipo_transacao': {
        'populacao': ['PIX', 'TED', 'BOLETO', 'SISTEMCO'],
        'pesos_popularidade': [0.65, 0.10, 0.20, 0.05],
        'multiplicador_valor': {'PIX': 0.8, 'TED': 1.2, 'BOLETO': 1.5, 'SISTEMCO': 1.0}
    },
    'pesos_sazonalidade': {
        1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2,
        7: 1.1, 8: 1.0, 9: 1.1, 10: 1.3, 11: 1.4, 12: 1.6
    }
}

def executar_backend_final():
    """
    Função principal que orquestra a geração e o tratamento dos dados.
    """
    print("--- INICIANDO EXECUÇÃO DO BACK-END ---")

    fake = Faker('pt_BR')
    
    # Etapa 1: Geração das tabelas base
    print(f"-> Gerando dados para {CONFIG['num_clientes']} clientes...")
    
    lista_clientes = []
    for i in range(CONFIG['num_clientes']):
        cnae_cliente = random.choices(
            list(CONFIG['pesos_cnae'].keys()), 
            weights=list(CONFIG['pesos_cnae'].values()), 
            k=1
        )[0]
        peso_c = CONFIG['pesos_cnae'][cnae_cliente]
        data_abertura = fake.date_between(start_date='-10y', end_date='-1y')
        saldo = round(random.uniform(-50000, 500000) * peso_c, 2)
        faturamento = abs(saldo * random.uniform(1.5, 10)) if saldo > 0 else random.uniform(10000, 2000000) * peso_c
        lista_clientes.append({
            'ID': i + 1, 'VL_FATU': round(faturamento, 2), 'VL_SLDO': saldo, 
            'DT_ABRT': data_abertura, 'DS_CNAE': cnae_cliente, 'DT_REFE': CONFIG['data_fim']
        })
    tabela1_df = pd.DataFrame(lista_clientes)
    
    print(f"-> Gerando {CONFIG['num_transacoes']} transações...")
    lista_transacoes = []
    lista_ids_clientes = tabela1_df['ID'].tolist()
    total_dias = (CONFIG['data_fim'] - CONFIG['data_inicio']).days
    
    tipos_de_transacao_gerados = random.choices(
        CONFIG['pesos_tipo_transacao']['populacao'], 
        weights=CONFIG['pesos_tipo_transacao']['pesos_popularidade'], 
        k=CONFIG['num_transacoes']
    )
    
    for i in range(CONFIG['num_transacoes']):
        id_pagador = random.choice(lista_ids_clientes)
        id_recebedor = random.choice(lista_ids_clientes)
        while id_pagador == id_recebedor:
            id_recebedor = random.choice(lista_ids_clientes)

        cnae_pagador = tabela1_df.loc[tabela1_df['ID'] == id_pagador, 'DS_CNAE'].iloc[0]
        
        data_transacao = CONFIG['data_inicio'] + timedelta(days=random.randint(0, total_dias))
        tipo_transacao = tipos_de_transacao_gerados[i]

        # Aplica os pesos para gerar um valor de transação realista
        peso_c = CONFIG['pesos_cnae'].get(cnae_pagador, 1.0)
        multiplicador_v = CONFIG['pesos_tipo_transacao']['multiplicador_valor'].get(tipo_transacao, 1.0)
        peso_s = CONFIG['pesos_sazonalidade'].get(data_transacao.month, 1.0)

        valor_base = random.uniform(50.0, 10000.0)
        valor_final = round(valor_base * peso_c * multiplicador_v * peso_s, 2)
        
        lista_transacoes.append({
            'ID_PGTO': id_pagador, 'ID_RCBE': id_recebedor, 'VL': valor_final, 
            'DS_TRAN': tipo_transacao, 'DT_REFE': data_transacao
        })
        
    tabela2_df = pd.DataFrame(lista_transacoes)

    # Etapa 2: Análise e enriquecimento dos dados
    print("-> Aplicando regras de negócio e classificação...")

    # Classificação de Momento de Vida com base na idade, faturamento e saldo
    hoje = date.today()
    tabela1_df['IDADE_EMPRESA'] = (pd.Timestamp(hoje) - pd.to_datetime(tabela1_df['DT_ABRT'])).dt.days / 365.25
    
    def classificar_momento(row):
        anos_empresa = row['IDADE_EMPRESA']
        faturamento = row['VL_FATU']
        saldo = row['VL_SLDO']
        
        if anos_empresa <= 2 and faturamento < 500000:
            return 'Início'
        if anos_empresa <= 5 and faturamento > 1500000 and saldo < 0:
            return 'Expansão Agressiva'
        if anos_empresa > 5 and faturamento > 1000000 and saldo > 100000:
            return 'Maturidade'
        if saldo < -50000 and faturamento < 400000:
            return 'Declínio'
        return 'Crescimento Estável'

    tabela1_df['Momento_Vida'] = tabela1_df.apply(classificar_momento, axis=1)

    # Métrica de Dependência baseada na concentração de receita
    print("-> Calculando métrica de dependência de clientes...")
    receita_total_por_cliente = tabela2_df.groupby('ID_RCBE')['VL'].sum().reset_index().rename(columns={'VL': 'VL_TOTAL_RECEBIDO'})
    receita_maior_pagador = tabela2_df.groupby(['ID_RCBE', 'ID_PGTO'])['VL'].sum().groupby('ID_RCBE').max().reset_index().rename(columns={'VL': 'VL_MAIOR_PAGADOR'})

    tabela1_df = pd.merge(tabela1_df, receita_total_por_cliente, left_on='ID', right_on='ID_RCBE', how='left')
    tabela1_df = pd.merge(tabela1_df, receita_maior_pagador, on='ID_RCBE', how='left')
    tabela1_df.fillna(0, inplace=True)

    tabela1_df['CONCENTRACAO_RECEITA'] = 0.0
    tabela1_df.loc[tabela1_df['VL_TOTAL_RECEBIDO'] > 0, 'CONCENTRACAO_RECEITA'] = \
        (tabela1_df['VL_MAIOR_PAGADOR'] / tabela1_df['VL_TOTAL_RECEBIDO'])

    # FUNÇÃO CORRIGIDA AQUI 👇
    def classificar_dependencia(concentracao):
        if concentracao > 0.6: return 'Alta Dependência'
        elif concentracao > 0.3: return 'Média Dependência'
        else: return 'Baixa Dependência'

    tabela1_df['Nivel_Dependencia'] = tabela1_df['CONCENTRACAO_RECEITA'].apply(classificar_dependencia)

    # Etapa 3: Salvamento dos arquivos finais
    tabela1_df.to_csv('base1_id.csv', index=False, encoding='utf-8-sig')
    tabela2_df.to_csv('base2_transacoes.csv', index=False, encoding='utf-8-sig')
    print("   ... Arquivos finais gerados com sucesso.")
    
    print("\n--- EXECUÇÃO DO BACK-END FINALIZADA ---")

if __name__ == "__main__":
    executar_backend_final()