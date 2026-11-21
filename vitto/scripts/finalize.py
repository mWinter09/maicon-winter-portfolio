from pathlib import Path

from docx import Document
from docx.shared import RGBColor
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Pt


root = Path(__file__).resolve().parent.parent
report = root / "relatorio-vitto.docx"
presentation = root / "apresentacao-vitto.pptx"

doc = Document(report)
title_style = doc.styles["Title"]
title_style.font.color.rgb = RGBColor(0, 0, 0)
title_style.font.underline = False
style_ppr = title_style._element.pPr
if style_ppr is not None:
    border = style_ppr.find(qn("w:pBdr"))
    if border is not None:
        style_ppr.remove(border)

for paragraph in doc.paragraphs:
    if paragraph.text.strip() == "Relatório estatístico":
        ppr = paragraph._p.get_or_add_pPr()
        border = ppr.find(qn("w:pBdr"))
        if border is not None:
            ppr.remove(border)
    if paragraph.text.startswith("O ticket médio foi de R$ 191,54"):
        paragraph.text = (
            "O ticket médio foi de R$ 191,54 e o mediano, R$ 162,50. Os quartis 25% e 75% "
            "foram R$ 89,75 e R$ 247,50. O desvio-padrão amostral foi R$ 153,24, indicando "
            "dispersão elevada entre pedidos. O intervalo de confiança aproximado de 95% para "
            "a média vai de R$ 189,48 a R$ 193,59, calculado como média ± 1,96 erros-padrão "
            "em 21.350 pedidos. Ele descreve a incerteza da média sob a hipótese de pedidos "
            "independentes e comparáveis; não é uma faixa para tickets individuais. Foram "
            "vendidas 2,32 pizzas por pedido, em média."
        )
if doc.tables and not any("IC 95%" in cell.text for cell in doc.tables[0].rows[-1].cells):
    row = doc.tables[0].add_row()
    row.cells[0].text = "IC 95% da média do ticket"
    row.cells[1].text = "R$ 189,48 a R$ 193,59"
doc.save(report)

prs = Presentation(presentation)
for shape in prs.slides[0].shapes:
    if shape.has_text_frame and shape.text.startswith("Ticket médio de R$ 191,54"):
        shape.text_frame.clear()
        shape.text_frame.word_wrap = True
        paragraph = shape.text_frame.paragraphs[0]
        paragraph.text = (
            "Ticket médio: R$ 191,54 · IC 95%: R$ 189,48 a R$ 193,59\n"
            "Ticket mediano: R$ 162,50"
        )
        for run in paragraph.runs:
            run.font.size = Pt(22)
        shape.height = Pt(90)
prs.save(presentation)
