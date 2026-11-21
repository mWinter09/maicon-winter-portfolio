import json,csv
from pathlib import Path
from datetime import date
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from pptx import Presentation
from pptx.util import Inches as I,Pt as P
from pptx.dml.color import RGBColor as C
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
p=Path(__file__).resolve().parent.parent
w=p/'build'
w.mkdir(exist_ok=True)
d=json.loads((p/'dados.json').read_text())
def n(x,places=0):return f'{x:,.{places}f}'.replace(',','@').replace('.',',').replace('@','.')
def br(x):return 'R$ '+n(x,2)
def dt(s):return date.fromisoformat(s).strftime('%d/%m/%Y')
def pct(x):return n(100*x,1)+'%'
red='#a93624';green='#286052';ink='#241d1a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':ink,'axes.labelcolor':ink,'axes.spines.top':False,'axes.spines.right':False,'axes.axisbelow':True})
fig,ax=plt.subplots(figsize=(9,3.5),layout='constrained')
rows=d['meses']
ax.bar(range(len(rows)),[r['receita']/1000 for r in rows],color=[red]*(len(rows)-1)+['#8b766e'])
ax.set_ylabel('Receita registrada (R$ mil)')
ticks=[0,3,6,9,12,15,18,19]
ax.set_xticks(ticks,[r['mes'][5:]+'/'+r['mes'][2:4] for r in [rows[i] for i in ticks]],rotation=25)
ax.grid(axis='y',alpha=.2)
fig.savefig(w/'mensal.png',dpi=190)
fig,ax=plt.subplots(figsize=(9,3.5),layout='constrained')
h=d['semanal'][-20:]; f=d['previsao']; x=len(h)
ax.plot(range(x),[r['pedidos'] for r in h],'-o',color=red,ms=3,label='Observado')
ax.plot(range(x-1,x+4),[h[-1]['pedidos']]+[r['estimativa'] for r in f],'--o',color=green,ms=4,label='Previsão')
ax.fill_between(range(x,x+4),[r['inferior'] for r in f],[r['superior'] for r in f],color=green,alpha=.18,label='Faixa empírica de 80%')
ax.axvline(x-.5,color='#888',lw=1,ls=':')
week=h+f
ticks=[0,4,8,12,16,19,23]
ax.set_xticks(ticks,[dt(week[i]['fim'])[:5] for i in ticks]);ax.set_ylabel('Pedidos na semana');ax.set_xlabel('Domingo de encerramento da semana');ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.16))
fig.savefig(w/'semanal.png',dpi=190)
doc=Document()
normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(11)
for key in ['Title','Heading 1','Heading 2']: doc.styles[key].font.color.rgb=RGBColor.from_string('A93624')
doc.sections[0].header.paragraphs[0].text='PIZZARIA DO VITTO  /  ANÁLISE DE VENDAS'
doc.sections[0].footer.paragraphs[0].text='Fonte primária  •  Dados da pizzaria do vitto.csv'
def heading(t):doc.add_heading(t,level=1)
def para(t):doc.add_paragraph(t)
def tab(head,rows):
    t=doc.add_table(rows=1,cols=len(head));t.style='Light Shading Accent 2'
    for c,k in zip(t.rows[0].cells,head):c.text=k
    for row in rows:
        for c,v in zip(t.add_row().cells,row):c.text=str(v)
def picture(path):doc.add_picture(str(w/path),width=Inches(6.4))
doc.add_heading('Relatório estatístico',0)
para('Vendas registradas de 1º de janeiro de 2025 a 3 de agosto de 2026')
heading('Resultados principais')
tab(['Indicador','Valor'],[('Receita registrada',br(d['receita'])),('Pedidos distintos',n(d['pedidos'])),('Pizzas vendidas',n(d['pizzas'])),('Ticket médio por pedido',br(d['ticket'])),('Ticket mediano por pedido',br(d['ticketMed'])),('Datas com registros','358 de 580'),('Sabores e variantes','32 sabores e 90 códigos de sabor/tamanho')])
ticket_se=d['ticketDP']/(d['pedidos']**.5)
ticket_ci=(d['ticket']-1.96*ticket_se,d['ticket']+1.96*ticket_se)
tab(['Estimativa','Intervalo de confiança aproximado de 95%'],[('Média do ticket por pedido',br(ticket_ci[0])+' a '+br(ticket_ci[1]))])
para('O tamanho G concentrou 45,9% da receita. A pizza Frango Tailandesa liderou em receita, e Especial da Casa liderou em unidades (2.453). O modelo semanal estimou 248,6 pedidos registrados por semana, com erro absoluto médio de 52,2 pedidos no teste de um passo.')
heading('Base e tratamento')
para('O CSV contém 48.620 linhas de itens e 21.350 identificadores distintos de pedido. A leitura usou ponto e vírgula como separador, vírgula decimal e datas no formato dia/mês/ano. Os valores foram apresentados em reais, assumindo BRL a partir do contexto brasileiro.')
para('Não houve linhas duplicadas, identificadores de venda repetidos nem pedidos distribuídos entre datas distintas. Na venda 5, a quantidade ausente foi inferida como 1, pois 80 ÷ 80 = 1. Nas demais linhas, quantidade × preço unitário coincide com o valor total. Um pedido tinha horários diferentes entre itens. Na análise por hora, foi usado o horário mais cedo de cada pedido.')
para('A receita é a soma do campo preco_total. O ticket é essa soma por pedido. A base não inclui custos, despesas, impostos, pagamentos ou informação suficiente para apurar margem, lucro ou caixa. Há 222 datas sem registros e não há indicação do motivo. Agosto de 2026 é parcial.')
heading('Evolução mensal e distribuição do ticket')
picture('mensal.png')
para('Entre os meses completos, outubro de 2025 registrou a maior receita (R$ 237.146,75, com 1.249 pedidos), e julho de 2026 registrou a menor (R$ 186.143,00, com 975 pedidos). A cobertura mensal e o número de datas com registros podem afetar a comparação.')
para('O ticket médio foi de R$ 191,54 e o mediano, R$ 162,50. Os quartis 25% e 75% foram R$ 89,75 e R$ 247,50. O desvio-padrão amostral foi R$ 153,24, indicando dispersão elevada entre pedidos. O intervalo de confiança aproximado de 95% para a média vai de R$ 189,48 a R$ 193,59, calculado como média ± 1,96 erros-padrão em 21.350 pedidos. Ele descreve a incerteza da média sob a hipótese de pedidos independentes e comparáveis; não é uma faixa para tickets individuais. Foram vendidas 2,32 pizzas por pedido, em média.')
heading('Cardápio')
tab(['Tamanho','Pizzas','Receita','Participação'],[(r['tamanho'],n(r['pizzas']),br(r['receita']),pct(r['receita']/d['receita'])) for r in d['tamanhos']])
para('A categoria Clássica liderou em receita (R$ 1.100.265,50, cerca de 26,9%) e em unidades (14.888). Cada pedido pode conter itens de várias categorias e tamanhos.')
tab(['Cinco sabores por receita','Pizzas','Receita'],[(r['nome_pizza_simp'],n(r['pizzas']),br(r['receita'])) for r in d['produtos'][:5]])
heading('Distribuição dos pedidos no calendário')
para('Quarta-feira teve 61,2 pedidos por data com registros, seguida de segunda-feira com 60,9. Por volume acumulado, segunda-feira liderou com 3.473 pedidos em 57 datas registradas. Às 12h foram registrados 2.520 pedidos (11,8% do total), o maior volume dentre as faixas de uma hora.')
tab(['Dia','Pedidos','Datas com registros','Pedidos por data'],[(name,n(r['pedidos']),r['dias'],n(r['pedidos']/r['dias'],1)) for name,r in zip(['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'],d['diasSemana'])])
heading('Previsão semanal de pedidos registrados')
para('A série tem 82 semanas completas de segunda a domingo, entre 06/01/2025 e 02/08/2026. Cada ponto soma os pedidos distintos registrados na semana. Datas ausentes contribuem com zero pedidos registrados. As semanas parciais das pontas foram excluídas do ajuste.')
para('Foram usadas 16 semanas iniciais para começar as previsões, 54 origens cronológicas para selecionar pelo menor MAE e 12 semanas finais para testar de 11/05 a 02/08/2026. No teste de um passo, cada nova previsão usa apenas observações anteriores à semana prevista.')
tab(['Modelo','MAE validação','MAE teste','RMSE teste','WAPE teste'],[(k,n(d['validacao'][k],1),n(r['mae'],1),n(r['rmse'],1),pct(r['wape'])) for k,r in d['teste'].items()])
para('MAE é a média dos erros absolutos em pedidos. RMSE é a raiz da média dos erros ao quadrado. WAPE é a soma dos erros absolutos dividida pela soma dos pedidos observados. A média móvel de oito semanas teve MAE de teste 30,1% menor que a referência da última semana.')
picture('semanal.png')
tab(['Semana projetada','Estimativa','Faixa empírica'],[(dt(r['ini'])+' a '+dt(r['fim']),n(r['estimativa'],1),f"{r['inferior']} a {r['superior']}") for r in f])
para('A média móvel usa o nível das últimas oito semanas completas em todos os horizontes. A faixa soma à estimativa os percentis 10 e 90 dos erros de validação calculados para cada horizonte. A cobertura futura pode variar, e o teste informado mede apenas o horizonte de uma semana.')
para('A projeção é retrospectiva: parte do corte de 02/08/2026, e o CSV já contém registros parciais da semana seguinte, em 03/08. A previsão descreve o volume registrado sob padrões de cobertura semelhantes aos históricos.')
heading('Implicações operacionais')
for item in ['Conciliar as 222 datas sem registros com o calendário de funcionamento antes de interpretar as lacunas como ausência de demanda.','Usar a faixa semanal para planejar cenários de escala. Combinar a série de pedidos com a quantidade por sabor, ficha técnica e perdas para planejar compras.','Cruzar receita por sabor e tamanho com custo variável por item para medir margem de contribuição.']:
    doc.add_paragraph(item,style='List Bullet')
doc.save(p/'relatorio-vitto.docx')
prs=Presentation();prs.slide_width=I(13.33);prs.slide_height=I(7.5)
def textbox(s,x,y,width,height,t,size,color='241D1A',bold=False):
    tf=s.shapes.add_textbox(I(x),I(y),I(width),I(height)).text_frame;tf.word_wrap=True
    for i,line in enumerate(t.split('\n')):
        q=tf.paragraphs[0] if i==0 else tf.add_paragraph();q.text=line;q.font.name='Calibri';q.font.size=P(size);q.font.bold=bold;q.font.color.rgb=C.from_string(color);q.space_after=P(12)
def slide(label,title,sub=''):
    s=prs.slides.add_slide(prs.slide_layouts[6]);fill=s.background.fill;fill.solid();fill.fore_color.rgb=C.from_string('FCF8F5')
    textbox(s,.65,.35,12,.4,label,16,'A93624',True);textbox(s,.65,.9,12,1.0,title,38,bold=True)
    if sub:textbox(s,.67,1.83,12,.6,sub,18,'695950')
    textbox(s,.66,7.02,11,.3,'Fonte: Dados da pizzaria do vitto.csv',11,'695950')
    return s
s=slide('PIZZARIA DO VITTO','Vendas, cardápio e previsão','Dados registrados de 01/01/2025 a 03/08/2026')
for i,(val,label) in enumerate([('R$ 4,09 mi','receita registrada'),('21.350','pedidos'),('49.574','pizzas')]):
    x=.7+i*4.2;textbox(s,x,3.04,3.9,.8,val,38,'A93624',True);textbox(s,x,3.9,3.9,.7,label,21,'695950')
textbox(s,.7,5.38,11.9,1.25,'Ticket médio: R$ 191,54 · IC 95%: R$ 189,48 a R$ 193,59\nTicket mediano: R$ 162,50',22)
s=slide('QUALIDADE DA BASE','358 datas com vendas registradas','580 dias corridos e 48.620 linhas de itens')
textbox(s,.7,2.65,11.8,3.65,'222 datas sem registros. O CSV não informa as causas.\nUma quantidade foi completada com a razão entre valor total e preço unitário.\nA receita corresponde aos valores de venda registrados. Custos e pagamentos estão fora da base.',25)
s=slide('EVOLUÇÃO MENSAL','Outubro de 2025 teve a maior receita','R$ 237,1 mil em outubro de 2025 · R$ 186,1 mil em julho de 2026')
s.shapes.add_picture(str(w/'mensal.png'),I(1.05),I(2.38),width=I(11.15))
s=slide('CARDÁPIO','O tamanho G responde por 45,9% da receita','A categoria Clássica lidera em receita e em unidades.')
textbox(s,.7,2.65,6.2,3.6,'Receita por tamanho\nG  ·  R$ 1,88 mi\nM  ·  R$ 1,25 mi\nP  ·  R$ 890 mil\nGG  ·  R$ 75 mil',25)
textbox(s,7.05,2.65,5.6,3.6,'Frango Tailandesa\nR$ 217,2 mil, líder em receita\nEspecial da Casa\n2.453 pizzas, líder em unidades',23)
s=slide('CALENDÁRIO','12h foi o horário com mais pedidos','2.520 pedidos às 12h, seguidos de 2.455 às 13h.')
textbox(s,.7,2.7,11.8,3.6,'Segunda-feira teve o maior total, com 3.473 pedidos em 57 datas registradas.\nQuarta-feira teve a maior média por data com registros, com 61,2 pedidos.\nOs totais por dia da semana variam com o número de datas registradas.',24)
s=slide('SÉRIE TEMPORAL','Previsão de cerca de 249 pedidos por semana','Projeção retrospectiva a partir de 02/08/2026, com média móvel de oito semanas.')
s.shapes.add_picture(str(w/'semanal.png'),I(1.1),I(2.39),width=I(11.05))
s=slide('VALIDAÇÃO','Erro médio de 52 pedidos por semana','Teste cronológico de um passo nas últimas 12 semanas completas.')
textbox(s,.7,2.65,11.8,3.55,'Média móvel de oito semanas: MAE de 52,2 e WAPE de 21,2%.\nÚltima semana: MAE de 74,7 e WAPE de 30,4%.\nA faixa da primeira semana projetada vai de 212 a 294 pedidos, com base nos erros históricos por horizonte.',24)
s=slide('OPERAÇÃO','O que os dados permitem decidir')
textbox(s,.7,2.25,11.8,4,'Conferir as datas sem registro com o calendário real de funcionamento.\nUsar as faixas semanais para planejar cenários de equipe.\nCruzar volumes com ficha técnica para estimar compras e custos variáveis para calcular margem.',25)
prs.save(p/'apresentacao-vitto.pptx')
with (p/'previsao-vitto.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    writer=csv.writer(stream,delimiter=';')
    writer.writerow(['inicio_semana','fim_semana','pedidos_estimados','limite_inferior_80_empirico','limite_superior_80_empirico'])
    writer.writerows((r['ini'],r['fim'],n(r['estimativa'],1),r['inferior'],r['superior']) for r in f)
