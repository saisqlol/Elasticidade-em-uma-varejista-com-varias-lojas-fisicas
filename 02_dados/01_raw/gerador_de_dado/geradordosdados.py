import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import warnings
warnings.filterwarnings('ignore')

# Inicializar Faker para dados realistas
fake = Faker('pt_BR')

# Configurações
np.random.seed(42)
random.seed(42)

# Parâmetros do dataset
n_transacoes = 100000  # Número total de transações
n_produtos = 50
n_lojas = 150
data_inicio = datetime(2024, 1, 1)
data_fim = datetime(2026, 2, 2)

# Categorias de produtos
categorias = {
    'Eletrônicos': 10,
    'Vestuário': 12,
    'Alimentos': 10,
    'Casa e Decoração': 10,
    'Esportes e Lazer': 8
}

# Criar lista de produtos
produtos = []
prod_id = 1
for categoria, quantidade in categorias.items():
    for i in range(quantidade):
        produtos.append({
            'ID_Produto': f'PROD{prod_id:03d}',
            'Categoria': categoria,
            'Preco_Base': np.random.uniform(10, 3000)
        })
        prod_id += 1

# Criar lista de lojas
lojas = [f'LOJA{i:03d}' for i in range(1, n_lojas + 1)]

# Estados das lojas (Sudeste)
estados = ['SP'] * 50 + ['RJ'] * 40 + ['MG'] * 40 + ['ES'] * 20

# Datas comemorativas com multiplicadores de vendas
datas_comemorativas = {
    # (mês, dia): (multiplicador, categorias_afetadas)
    (1, 1): (1.5, ['Todos']),  # Ano Novo
    (1, 15): (2.0, ['Eletrônicos', 'Vestuário']),  # Volta às Aulas
    (1, 20): (2.0, ['Eletrônicos', 'Vestuário']),
    (2, 14): (1.8, ['Vestuário', 'Casa e Decoração']),  # Dia dos Namorados (BR)
    (3, 29): (2.5, ['Alimentos']),  # Páscoa 2024
    (4, 20): (1.3, ['Todos']),  # Tiradentes
    (5, 12): (1.8, ['Vestuário', 'Casa e Decoração']),  # Dia das Mães
    (6, 12): (1.5, ['Todos']),  # Dia dos Namorados
    (9, 7): (1.2, ['Todos']),  # Independência
    (10, 12): (2.2, ['Esportes e Lazer']),  # Dia das Crianças
    (11, 29): (4.0, ['Eletrônicos', 'Vestuário']),  # Black Friday 2024
    (11, 28): (3.5, ['Todos']),  # Black Friday 2025
    (12, 24): (3.0, ['Todos']),  # Véspera de Natal
    (12, 25): (2.5, ['Todos']),  # Natal
    (12, 31): (1.8, ['Alimentos', 'Bebidas'])  # Reveillon
}

# Função para verificar se é data comemorativa
def get_multiplicador_data(data, categoria):
    mes_dia = (data.month, data.day)
    if mes_dia in datas_comemorativas:
        multiplicador, categorias_afetadas = datas_comemorativas[mes_dia]
        if 'Todos' in categorias_afetadas or categoria in categorias_afetadas:
            return multiplicador
    return 1.0

# Função para gerar desconto baseado em vários fatores
def gerar_desconto(data, categoria, loja_idx):
    # Desconto base
    desconto_base = np.random.uniform(0, 0.3)
    
    # Aumentar desconto em datas comemorativas
    if get_multiplicador_data(data, categoria) > 1.5:
        desconto_base += np.random.uniform(0.1, 0.3)
    
    # Descontos maiores em lojas de SP (mais competitivo)
    if estados[loja_idx] == 'SP':
        desconto_base += np.random.uniform(0.05, 0.1)
    
    # Limitar desconto máximo
    desconto_base = min(desconto_base, 0.6)
    
    return round(desconto_base, 4)

# Função para gerar quantidade baseada em vários fatores
def gerar_quantidade(data, categoria, multiplicador):
    quantidade_base = np.random.poisson(2) + 1
    
    # Ajustar por categoria
    if categoria == 'Alimentos':
        quantidade_base = np.random.poisson(3) + 1
    elif categoria == 'Eletrônicos':
        quantidade_base = np.random.poisson(1.5) + 1
    
    # Aplicar multiplicador de datas comemorativas
    quantidade = int(quantidade_base * multiplicador)
    
    # Adicionar outliers em 0.1% das transações
    if np.random.random() < 0.001:
        quantidade = np.random.randint(20, 101)
    
    return max(1, quantidade)

# Gerar transações
transacoes = []
cliente_counter = 1

print("Gerando dados fictícios...")
for i in range(n_transacoes):
    if i % 10000 == 0:
        print(f"Progresso: {i}/{n_transacoes}")
    
    # Selecionar produto aleatório
    produto_idx = np.random.randint(0, len(produtos))
    produto = produtos[produto_idx]
    
    # Selecionar loja aleatória
    loja_idx = np.random.randint(0, len(lojas))
    loja = lojas[loja_idx]
    
    # Gerar data aleatória no período
    dias_diferenca = (data_fim - data_inicio).days
    dias_aleatorios = np.random.randint(0, dias_diferenca)
    data = data_inicio + timedelta(days=dias_aleatorios)
    
    # Gerar hora aleatória (mais vendas durante o dia)
    hora = np.random.normal(14, 4)  # Distribuição normal centrada em 14h
    hora = max(8, min(22, hora))  # Limitar entre 8h e 22h
    minuto = np.random.randint(0, 60)
    segundo = np.random.randint(0, 60)
    
    data_hora = data.replace(hour=int(hora), minute=minuto, second=segundo)
    
    # Verificar multiplicador por data comemorativa
    multiplicador = get_multiplicador_data(data, produto['Categoria'])
    
    # Ajustar por dia da semana (finais de semana têm mais vendas)
    if data.weekday() >= 5:  # Sábado ou Domingo
        multiplicador *= 1.3
    
    # Gerar desconto
    desconto = gerar_desconto(data, produto['Categoria'], loja_idx)
    
    # Calcular preços
    preco_base = produto['Preco_Base']
    preco_de = round(preco_base * np.random.uniform(1.1, 1.3), 2)
    preco_por = round(preco_de * (1 - desconto), 2)
    
    # Gerar quantidade
    quantidade = gerar_quantidade(data, produto['Categoria'], multiplicador)
    
    # Calcular valor total
    valor_venda = round(preco_por * quantidade, 2)
    
    # Gerar ID de cliente (alguns clientes são recorrentes)
    if np.random.random() < 0.7:  # 70% clientes novos
        id_cliente = f'CLI{cliente_counter:06d}'
        cliente_counter += 1
    else:  # 30% clientes recorrentes
        id_cliente = f'CLI{np.random.randint(1, cliente_counter):06d}'
    
    # Criar transação
    transacao = {
        'ID_Transacao': f'{data.strftime("%Y%m%d")}{i:06d}',
        'Data_Hora_Transacao': data_hora.strftime('%Y-%m-%d %H:%M:%S'),
        'ID_Produto': produto['ID_Produto'],
        'Categoria_Produto': produto['Categoria'],
        'ID_Loja': loja,
        'Preco_De': preco_de,
        'Preco_Por': preco_por,
        'Valor_Venda': valor_venda,
        'Quantidade_Vendida': quantidade,
        'ID_Cliente': id_cliente,
        'Desconto': f"{desconto*100:.2f}%"
    }
    
    transacoes.append(transacao)

# Converter para DataFrame
df = pd.DataFrame(transacoes)

# Ordenar por data
df['Data_Hora_Transacao'] = pd.to_datetime(df['Data_Hora_Transacao'])
df = df.sort_values('Data_Hora_Transacao')

# Adicionar algumas transações de outliers extremos manualmente
outliers_extremos = [
    {
        'ID_Transacao': '20241129000001',
        'Data_Hora_Transacao': '2024-11-29 08:01:00',
        'ID_Produto': 'PROD005',
        'Categoria_Produto': 'Eletrônicos',
        'ID_Loja': 'LOJA015',
        'Preco_De': 1999.99,
        'Preco_Por': 1199.99,
        'Valor_Venda': 29999.75,
        'Quantidade_Vendida': 25,
        'ID_Cliente': 'CLI045672',
        'Desconto': '40.00%'
    },
    {
        'ID_Transacao': '20241224120050',
        'Data_Hora_Transacao': '2024-12-24 12:00:00',
        'ID_Produto': 'PROD042',
        'Categoria_Produto': 'Esportes e Lazer',
        'ID_Loja': 'LOJA067',
        'Preco_De': 349.90,
        'Preco_Por': 279.90,
        'Valor_Venda': 11196.00,
        'Quantidade_Vendida': 40,
        'ID_Cliente': 'CLI023489',
        'Desconto': '20.00%'
    },
    {
        'ID_Transacao': '20250115004500',
        'Data_Hora_Transacao': '2025-01-15 09:30:00',
        'ID_Produto': 'PROD012',
        'Categoria_Produto': 'Vestuário',
        'ID_Loja': 'LOJA034',
        'Preco_De': 49.90,
        'Preco_Por': 39.90,
        'Valor_Venda': 3990.00,
        'Quantidade_Vendida': 100,
        'ID_Cliente': 'CLI078901',
        'Desconto': '20.04%'
    }
]

# Adicionar outliers ao DataFrame
df_outliers = pd.DataFrame(outliers_extremos)
df = pd.concat([df, df_outliers], ignore_index=True)

# Salvar como CSV
print("Salvando arquivo CSV...")
df.to_csv('02_dados\\02_processed\\limpos\\vendas_ficticias_2024_2026.csv', index=False, encoding='utf-8-sig')

# Gerar arquivo de metadados
metadata = {
    'total_transacoes': len(df),
    'periodo_inicio': data_inicio.strftime('%Y-%m-%d'),
    'periodo_fim': data_fim.strftime('%Y-%m-%d'),
    'produtos_unicos': df['ID_Produto'].nunique(),
    'lojas_unicas': df['ID_Loja'].nunique(),
    'clientes_unicos': df['ID_Cliente'].nunique(),
    'valor_total_vendas': df['Valor_Venda'].sum(),
    'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

with open('02_dados\\02_processed\\limpos\\metadata_vendas.txt', 'w', encoding='utf-8') as f:
    for key, value in metadata.items():
        f.write(f"{key}: {value}\n")

print(f"\n Dataset gerado com sucesso!")
print(f" Total de transações: {len(df):,}")
print(f" Arquivo: vendas_ficticias_2024_2026.csv")
print(f" Metadados: metadata_vendas.txt")
print(f"\n Estatísticas básicas:")
print(f"   • Produtos únicos: {df['ID_Produto'].nunique()}")
print(f"   • Lojas únicas: {df['ID_Loja'].nunique()}")
print(f"   • Valor total de vendas: R$ {df['Valor_Venda'].sum():,.2f}")
print(f"   • Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
print(f"\n Características incluídas:")
print(f"   • Variações sazonais (datas comemorativas)")
print(f"   • Outliers em Black Friday, Natal, etc.")
print(f"   • Descontos variáveis por região")
print(f"   • Padrões de compra por categoria")
print(f"   • Clientes recorrentes e únicos")