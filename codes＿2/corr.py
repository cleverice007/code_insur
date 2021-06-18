import pandas as pd

data = pd.read_csv('processed_data2.csv', encoding='big5')
data = data.filter(regex=("buy.*"))
cor = data.corr(method ='pearson')
cor.to_csv('cor.csv')
