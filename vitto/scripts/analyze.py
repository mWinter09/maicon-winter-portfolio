import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
parser=argparse.ArgumentParser(description='Gera os agregados e a previsão para o dashboard.')
parser.add_argument('csv',type=Path,help='CSV original de transações')
args=parser.parse_args()
out=Path(__file__).resolve().parent.parent
d=pd.read_csv(args.csv,sep=';',decimal=',')
d['data']=pd.to_datetime(d.data_pedido,format='%d/%m/%Y')
d['mes']=d.data.dt.strftime('%Y-%m')
d['hora']=d.hora_pedido.str[:2]
missing=int(d.quantidade.isna().sum())
d['quantidade']=d.quantidade.fillna(d.preco_total/d.preco_unitario).astype(int)
orders=d.groupby('id_pedido').agg(data=('data','first'),hora=('hora','min'),valor=('preco_total','sum'))
orders['dia']=orders.data.dt.dayofweek
days=pd.date_range(d.data.min(),d.data.max())
daily=d.groupby('data').agg(receita=('preco_total','sum'),pedidos=('id_pedido','nunique'),pizzas=('quantidade','sum')).reindex(days,fill_value=0)
weekly=daily.resample('W-SUN').sum().iloc[1:-1]
assert weekly.index[0]-pd.Timedelta(days=6)>=days[0] and weekly.index[-1]<=days[-1]
y=weekly.pedidos.to_numpy()
def pred(name,a):
    if name=='Última semana': return a[-1]
    if name=='Média móvel (4 semanas)': return np.mean(a[-4:])
    if name=='Média móvel (8 semanas)': return np.mean(a[-8:])
    level=np.mean(a[:8])
    for x in a[8:]: level=.25*x+.75*level
    return level
names=['Última semana','Média móvel (4 semanas)','Média móvel (8 semanas)','Suavização exponencial (α = 0,25)']
def errors(name,indices,h=1):
    return np.array([y[i+h-1]-pred(name,y[:i]) for i in indices],float)
cut=len(y)-12
valid={n:float(np.mean(abs(errors(n,range(16,cut))))) for n in names}
chosen=min(valid,key=valid.get)
test={n:dict(mae=float(np.mean(abs(e))),rmse=float(np.sqrt(np.mean(e**2))),wape=float(np.sum(abs(e))/np.sum(y[cut:]))) for n in names for e in [errors(n,range(cut,len(y)))]}
forecast=[]
for h in range(1,5):
    e=errors(chosen,range(16,cut-h+1),h)
    q=np.quantile(e,[.1,.9])
    p=float(pred(chosen,y))
    date=weekly.index[-1]+pd.Timedelta(weeks=h)
    forecast.append(dict(ini=(date-pd.Timedelta(days=6)).strftime('%Y-%m-%d'),fim=date.strftime('%Y-%m-%d'),estimativa=round(p,1),inferior=round(max(0,p+q[0])),superior=round(p+q[1])))
def group(keys):
    return d.groupby(keys).agg(receita=('preco_total','sum'),pizzas=('quantidade','sum'),pedidos=('id_pedido','nunique')).reset_index().sort_values('receita',ascending=False).to_dict('records')
result=dict(inicio=str(days[0].date()),fim=str(days[-1].date()),dias=len(days),diasComRegistro=int((daily.pedidos>0).sum()),linhas=len(d),faltantes=missing,receita=float(d.preco_total.sum()),pedidos=len(orders),pizzas=int(d.quantidade.sum()),
 ticket=float(orders.valor.mean()),ticketMed=float(orders.valor.median()),ticketDP=float(orders.valor.std()),ticketQ=[float(orders.valor.quantile(x)) for x in [.25,.75]],
 sabores=d.nome_pizza_simp.nunique(),variantes=d.sabor_pizza.nunique(),meses=sorted(group('mes'),key=lambda r:r['mes']),cardapio=group(['mes','categoria','tamanho','nome_pizza_simp']),categorias=group('categoria'),tamanhos=group('tamanho'),produtos=group('nome_pizza_simp'),
 diasSemana=[dict(dia=i,pedidos=int((orders.dia==i).sum()),dias=int(((daily.index.dayofweek==i)&(daily.pedidos>0)).sum())) for i in range(7)],
 horas=orders.hora.value_counts().sort_index().to_dict(),horariosDivergentes=int((d.groupby('id_pedido').hora_pedido.nunique()>1).sum()),
 semanal=[dict(fim=str(i.date()),pedidos=int(r.pedidos),fase='teste' if j>=cut else 'histórico') for j,(i,r) in enumerate(weekly.iterrows())],
 previsao=forecast,modelo=chosen,validacao=valid,teste=test,nSemanas=len(y),nValid=cut-16,nTeste=12,testeInicio=str((weekly.index[cut]-pd.Timedelta(days=6)).date()))
(out/'dados.json').write_text(json.dumps(result,ensure_ascii=False))
print({k:v for k,v in result.items() if k not in ('semanal','cardapio','produtos','meses')})
print(result['produtos'][:5])
