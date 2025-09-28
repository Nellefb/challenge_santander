# Challenge FIAP 2025 - Santander | Solução do Time Data Wave

**Integrantes:** Ellen Ferreira, Gabriel Paterra, Gabriel Valls, Gustavo Rosa, Kaio Valls

## 1. Visão Geral do Projeto

Este repositório contém a solução completa desenvolvida pelo time **Data Wave** para o Challenge FIAP 2025 em parceria com o **Santander**. O projeto consiste em uma solução de ponta a ponta, com back-end e front-end, que transforma dados transacionais de clientes Pessoa Jurídica (PJ) em insights acionáveis para a tomada de decisão estratégica no banco.

## 2. O Problema de Negócio

No cenário financeiro competitivo, o Santander busca compreender profundamente o comportamento e o momento de vida de seus clientes PJ para oferecer produtos e serviços mais alinhados às suas necessidades. O desafio foi dividido em duas frentes principais:

* **Desafio 1: Momento de Vida da Empresa:** Classificar as empresas em estágios como Início, Expansão, Maturidade e Declínio, a partir de seu comportamento financeiro transacional.
* **Desafio 2: Cadeias de Valor e Análise de Redes:** Analisar as redes de relacionamento entre empresas com base em pagamentos e recebimentos para encontrar padrões, riscos (como alta dependência de poucos clientes) e oportunidades de negócio (Social Network Analysis - SNA).

## 3. A Nossa Solução

Desenvolvemos uma arquitetura que separa a inteligência de dados (back-end) da ferramenta de visualização e decisão (front-end).

### Back-end (O Cérebro em Python)

O script `gerar_dados_finais.py` atua como o motor de Data Science da solução. Ele executa as seguintes tarefas:
* **Geração de Dados Realistas:** Simula um ambiente de dados real, criando duas bases (`base1_id` e `base2_transacoes`) que seguem fielmente o dicionário de dados fornecido.
* **Classificação (Solução para o Case 1):** Aplica um modelo de regras de negócio para analisar o perfil de cada cliente (faturamento, saldo, idade da empresa) e atribuir uma classificação de **"Momento de Vida"**.
* **Análise de Dependência (Solução para o Case 2):** Realiza uma análise simplificada da rede de transações para calcular o **"Nível de Dependência"** de cada empresa, identificando clientes que possuem alta concentração de pagamentos recebidos de poucas fontes.
* **Enriquecimento dos Dados:** Adiciona variância e sazonalidade aos dados para que os padrões visualizados no dashboard sejam mais próximos da realidade.

### Front-end (O Painel de Decisão em Power BI)

O arquivo `.pbix` é a interface visual e interativa da nossa solução, projetada para um gestor de negócios do Santander. Suas principais características são:
* **Dashboard Prescritivo:** Foco em ir além da simples descrição de dados. O painel foi desenhado para gerar insights e recomendar ações.
* **Visualização dos Insights:** Permite que o usuário filtre e analise os clientes com base nas classificações geradas pelo back-end (Momento de Vida e Nível de Dependência).
* **Ação Recomendada:** Utilizando medidas DAX, o dashboard sugere a melhor abordagem comercial para cada segmento de cliente, transformando a análise em uma ferramenta de vendas e gestão de risco.
* **Interatividade:** Possui filtros dinâmicos que permitem a exploração dos dados por data, tipo de transação e setor (CNAE).

## 4. Tecnologias Utilizadas

Para a construção desta solução, utilizamos as seguintes tecnologias:
* **Power BI:** Para a construção do dashboard interativo e front-end da solução.
* **Python:** Para o desenvolvimento do back-end, incluindo a geração, tratamento e análise de dados. (Bibliotecas: Pandas, NumPy, Faker).
* **SQL:** Conceitos de modelagem de dados utilizados para estruturar as tabelas.
* **Gemini (Google AI):** Utilizado como assistente de IA para apoio na estruturação do código, depuração, criação de lógicas de negócio e elaboração da documentação do projeto.
* **ChatGPT:** Utilizado como ferramenta de apoio para a geração de ideias.
* **Excel:** Utilizado como base para o entendimento da estrutura de dados inicial.

## 5. Como Executar a Solução

Siga os passos abaixo para rodar a demonstração 100% funcional.

### Pré-requisitos
1.  **Python 3** instalado na máquina.
2.  **Power BI Desktop** instalado.
3.  **Instalar bibliotecas Python:** Abra um terminal e execute o comando:
    ```bash
    pip install pandas numpy faker
    ```

### Passo 1: Executar o Back-end
Navegue até a pasta do projeto no seu terminal e execute o script Python para gerar os arquivos de dados enriquecidos.

```bash
python gerar_dados_finais.py
```
*Este comando criará os arquivos `base1_id.csv` e `base2_transacoes.csv`.*

### Passo 2: Abrir o Front-end
1.  Abra o arquivo `.pbix` do projeto no Power BI Desktop.
2.  Clique no botão **"Atualizar"** na guia "Página Inicial" para carregar os dados gerados.
3.  O dashboard estará 100% funcional e pronto para a análise.