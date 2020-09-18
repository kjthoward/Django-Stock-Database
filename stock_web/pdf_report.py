import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import  BaseDocTemplate, Paragraph, Table, TableStyle, Frame, PageTemplate
from .version import __version__

def fake_for_pages(body, title, httpresponse, user):
    styles = getSampleStyleSheet()
    styleNormal = styles['Normal']
    styleHeading = styles['Heading1']
    styleHeading.alignment = 1
    def head_footer(canvas, doc):
        canvas.saveState()
        P = Paragraph("BROKEN - Contact kieran.howard@ouh.nhs.uk",
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        P = Paragraph("Page BUGGED of BROKEN",
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.width+doc.leftMargin, h)

        P = Paragraph("BUGGED - Contact kieran.howard@ouh.nhs.uk",styleHeading)
        w, h = P.wrap(doc.width+doc.leftMargin+doc.rightMargin, doc.topMargin)
        P.drawOn(canvas, 0, doc.height + doc.topMargin)
        #canvas.drawCentredString((doc.width+doc.leftMargin+doc.rightMargin)/2.0, doc.height+doc.topMargin, title)
        #pdb.set_trace()
        canvas.restoreState()
    new_body=[]
    for b in body:
        temp=[]
        for part in b:
            if len(part)>40:
                t=part.split(' ')
                a=" ".join(t[0:round(len(t)/2)])
                b=" ".join(t[len(t)-round(len(t)/2):])
                temp+=["\n".join([a,b])]
            else:
                temp+=[part]
        new_body+=[temp]
    TABLE=Table(data=new_body, repeatRows=1)
    TABLE.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('ALIGN', (0, 0), (-1, -1), "LEFT")]))
    table=[]
    table.append(TABLE)
    doc = BaseDocTemplate(httpresponse, topMargin=12, bottomMargin=20, pagesize=landscape(A4))

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
           id='normal')
    template = PageTemplate(id='table', frames=frame, onPage=head_footer)
    doc.addPageTemplates([template])

    doc.build(table)
    return doc.page


def report_gen(body, title, httpresponse, user):
    styles = getSampleStyleSheet()
    styleNormal = styles['Normal']
    styleHeading = styles['Heading1']
    styleHeading.alignment = 1
    total_pages=fake_for_pages(body, title, httpresponse, user)
    def head_footer(canvas, doc):
        canvas.saveState()
        P = Paragraph("Report Generated: {}    By: {} - Stock Database V{}".format(datetime.datetime.today().strftime("%d/%m/%Y"), user, __version__),
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        P = Paragraph("Page {} of {}".format(canvas.getPageNumber(), total_pages),
                      styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.width+doc.leftMargin, h)

        P = Paragraph("{}".format(title),styleHeading)
        w, h = P.wrap(doc.width+doc.leftMargin+doc.rightMargin, doc.topMargin)
        P.drawOn(canvas, 0, doc.height + doc.topMargin)
        #canvas.drawCentredString((doc.width+doc.leftMargin+doc.rightMargin)/2.0, doc.height+doc.topMargin, title)
        #pdb.set_trace()
        canvas.restoreState()
    new_body=[]
    for b in body:
        temp=[]
        for part in b:
            if len(part)>40:
                t=part.split(' ')
                a=" ".join(t[0:round(len(t)/2)])
                b=" ".join(t[len(t)-round(len(t)/2):])
                temp+=["\n".join([a,b])]
            else:
                temp+=[part]
        new_body+=[temp]
    TABLE=Table(data=new_body, repeatRows=1)
    TABLE.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('ALIGN', (0, 0), (-1, -1), "LEFT")]))
    table=[]
    table.append(TABLE)
    doc = BaseDocTemplate(httpresponse, topMargin=12, bottomMargin=20, pagesize=landscape(A4))

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
           id='normal')
    template = PageTemplate(id='table', frames=frame, onPage=head_footer)
    doc.addPageTemplates([template])

    doc.build(table)
    # import pdb; pdb.set_trace()
    # #if total pages are 0 rebuild the document but with correct page numbers (builds it once to get page numbers)
    # if total_pages==0:
    #     report_gen(body, title, httpresponse, user, total_pages=doc.page)
    return doc
