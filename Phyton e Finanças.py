import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import yfinance as yfin

# Analisando o IBOV
yfin.pdr_override()
cotacao_ibov = web.get_data_yahoo('^BVSP', start='2022-1-1', end='2022-12-31')
print(cotacao_ibov)

# Retorno do IBOV
retorno_ibov = cotacao_ibov['Adj Close'][-1] / cotacao_ibov['Adj Close'][0] - 1
print('Retorno de {:.2%}'.format(retorno_ibov))

# Analisando o Gráfico com Média Móvel
cotacao_ibov['Adj Close'].plot(figsize=(10, 5), label='IBOV')
cotacao_ibov['Adj Close'].rolling(21).mean().plot(label='MM21')
#cotacao_ibov['Adj Close'].rolling(34).mean().plot(label='MM34')
plt.legend()
plt.show()