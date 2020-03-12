import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import  BaseDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate

def report_gen(body, title, httpresponse, user):
    styles = getSampleStyleSheet()
    styleNormal = styles['Normal']
    styleHeading = styles['Heading1']
    styleHeading.alignment = 1
    
    def head_footer(canvas, doc):
        canvas.saveState()
        P = Paragraph("Report Geneterated: {}    By: {} - Stock Database V0.1".format(datetime.datetime.today().strftime("%d/%m/%Y"), user),
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        P = Paragraph("Page {}".format(canvas.getPageNumber()),
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.width+doc.leftMargin, h)
        
        P = Paragraph("{}".format(title),styleHeading)
        w, h = P.wrap(doc.width, doc.topMargin)
        #P.drawOn(canvas, ((doc.width-stringWidth(title, "Times-Roman", 20))/2.0), doc.height + doc.topMargin)
        canvas.drawCentredString((doc.width+canvas.stringWidth(title))/2.0, doc.height+doc.topMargin, title)
        #pdb.set_trace()
        canvas.restoreState()
    TABLE=Table(data=body, repeatRows=1)
    TABLE.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('ALIGN', (0, 0), (-1, -1), "CENTER")]))
    table=[]
    table.append(TABLE)
    doc = BaseDocTemplate(httpresponse, topMargin=12, bottomMargin=20, pagesize=A4)

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
           id='normal')
    template = PageTemplate(id='table', frames=frame, onPage=head_footer)
    doc.addPageTemplates([template])
    doc.build(table)
