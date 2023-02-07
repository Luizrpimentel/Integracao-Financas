import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import yfinance as yf
from IPython.display import display


#Importando a carteira e transformando em gráfico
carteira = pd.read_excel('Carteira.xlsx')
display(carteira)

fig, (ax1, ax2) = plt.subplots(1, 2)
fig.set_size_inches(15, 5)
grafico1 = carteira.plot.pie(ax=ax1, labels=carteira['Ativos'], y='Valor Investido', legend=False, title='Distribuição de Ativos da Carteira', figsize=(15, 5), autopct="%.1f%%").set_ylabel('')
grafico2 = carteira.groupby('Tipo').sum().plot.pie(ax=ax2, y='Valor Investido', legend=False, title='Distribuição de Classe de Ativos da Carteira', figsize=(15, 5), autopct="%.1f%%").set_ylabel('')

#Pegando as Cotações ao Longo de 2022 do IBOV
yf.pdr_override()
ibov_df = web.get_data_yahoo('^BVSP', start='2022-1-1', end='2022-12-31')
ibov_df.reset_index(inplace = True)
ibov_df['Date'] = pd.to_datetime(ibov_df['Date'])
ibov_df['Date'] = ibov_df['Date'].dt.strftime('%Y-%m-%d')
ibov_df = ibov_df.set_index('Date')
display(ibov_df)
ibov_df['Adj Close'].plot(figsize=(15, 5))


#Pegando as Cotações ao Longo de 2022 da minha carteira de ações
carteira_df = pd.DataFrame()
for ativo in carteira['Ativos']:
    if 'Tesouro' not in ativo:
        carteira_df[ativo] = web.DataReader('{}.SA'.format(ativo), start='2022-1-1', end='2022-12-31')['Adj Close']

carteira_df.reset_index(inplace=True)
carteira_df['Date'] = pd.to_datetime(carteira_df['Date']).astype('datetime64[ns]')
carteira_df['Date'] = carteira_df['Date'].dt.strftime('%Y-%m-%d').astype('datetime64[ns]')
carteira_df = carteira_df.set_index('Date')

carteira_df = carteira_df.ffill()
display(carteira_df)

#Pegando as Cotações ao Longo de 2022 do Tesouro Selic e juntando o tesouro selic na nossa carteira
link = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'
tesouro_df = pd.read_csv(link, sep=';', decimal=',')
tesouro_df['Data Base'] = pd.to_datetime(tesouro_df['Data Base'], format='%d/%m/%Y').astype('datetime64[ns]')

tesouro_df = tesouro_df.loc[tesouro_df['Tipo Titulo']=='Tesouro Selic', :]
tesouro_df = tesouro_df.rename(columns={'Data Base': 'Date'})

carteira_df = carteira_df.merge(tesouro_df[['Date', 'PU Base Manha']], on='Date', how='left')
carteira_df = carteira_df.rename(columns={'PU Base Manha': 'Tesouro Selic'})

carteira_df = carteira_df.ffill()
display(carteira_df)

#Calculando o valor investido  e comparando o crescimento da carteira com o do IBOV
valor_investido = carteira_df.copy()

for ativo in carteira['Ativos']:
    #print(carteira.loc[carteira['Ativos']==ativo, 'Qtde'].values[0])
    valor_investido[ativo] = valor_investido[ativo] * carteira.loc[carteira['Ativos']==ativo, 'Qtde'].values[0]

valor_investido = valor_investido.set_index('Date')
valor_investido['Total'] = valor_investido.sum(axis=1)
display(valor_investido)

valor_investido_norm = valor_investido / valor_investido.iloc[0]
ibov_df_norm = ibov_df / ibov_df.iloc[0]

valor_investido_norm['Total'].plot(figsize=(15, 5), label='Carteira')
ibov_df_norm['Adj Close'].plot(label='IBOV')
plt.legend()

rentabilidade_carteira = valor_investido_norm['Total'].iloc[-1] - 1
rentabilidade_ibov = ibov_df_norm['Adj Close'].iloc[-1] - 1
print('Rentabilidade da Carteira {:.1%}'.format(rentabilidade_carteira))
print('Rentabilidade do Ibovespa {:.1%}'.format(rentabilidade_ibov))