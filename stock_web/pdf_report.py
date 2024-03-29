import datetime
import math
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    BaseDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Frame,
    PageTemplate,
)
from .version import __version__


def fake_for_pages(body, title, httpresponse, user):
    styles = getSampleStyleSheet()
    styleNormal = styles["Normal"]
    styleHeading = styles["Heading1"]
    styleHeading.alignment = 1

    def head_footer(canvas, doc):
        canvas.saveState()
        P = Paragraph(
            "BROKEN - Contact GeneticsLabsBioinformatics@oxnet.nhs.uk", styleNormal
        )
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        P = Paragraph("Page BUGGED of BROKEN", styleNormal)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.width + doc.leftMargin, h)

        P = Paragraph(
            "BUGGED - Contact GeneticsLabsBioinformatics@oxnet.nhs.uk", styleHeading
        )
        w, h = P.wrap(doc.width + doc.leftMargin + doc.rightMargin, doc.topMargin)
        P.drawOn(canvas, 0, doc.height + doc.topMargin)
        canvas.restoreState()

    new_body = []
    for b in body:
        temp = []
        if len(b) > 12:
            limit = 10
        else:
            limit = 40
        for part in b:
            try:
                if len(part) > limit:
                    t = part.split(" ")
                    if len(t[0]) == len(part):
                        t = part.split("-")
                    if len(t[0]) == len(part):
                        t = part.split("_")
                    if len(t[0]) == len(part):
                        t = part.split(".")
                    a = " ".join(t[0 : math.ceil(len(t) / 2)])
                    b = " ".join(t[len(t) - math.floor(len(t) / 2) :])
                    temp += ["\n".join([a, b])]
                else:
                    temp += [part]
            except:
                temp += [part]
        new_body += [temp]
    TABLE = Table(data=new_body, repeatRows=1)
    TABLE.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )
    table = []
    table.append(TABLE)
    doc = BaseDocTemplate(
        httpresponse, topMargin=12, bottomMargin=20, pagesize=landscape(A4)
    )

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="table", frames=frame, onPage=head_footer)
    doc.addPageTemplates([template])

    doc.build(table)
    return doc.page


def report_gen(body, title, httpresponse, user, shade=False):
    styles = getSampleStyleSheet()
    styleNormal = styles["Normal"]
    styleHeading = styles["Heading1"]
    styleHeading.alignment = 1
    total_pages = fake_for_pages(body, title, httpresponse, user)

    def head_footer(canvas, doc):
        canvas.saveState()
        P = Paragraph(
            "Report Generated: {}    By: {} - Stock Database V{}".format(
                datetime.datetime.today().strftime("%d/%m/%Y"), user, __version__
            ),
            styleNormal,
        )
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        P = Paragraph(
            "Page {} of {}".format(canvas.getPageNumber(), total_pages), styleNormal
        )
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.width + doc.leftMargin, h)

        P = Paragraph("{}".format(title), styleHeading)
        w, h = P.wrap(doc.width + doc.leftMargin + doc.rightMargin, doc.topMargin)
        P.drawOn(canvas, 0, doc.height + doc.topMargin)

        canvas.restoreState()

    i = 0
    hash_rows = []
    new_body = []
    for b in body:
        temp = []
        if len(b) > 12:
            limit = 10
        else:
            limit = 40
        for part in b:
            try:
                if "#" in part:
                    hash_rows.append(i)
            except:
                pass
            try:
                if len(part) > limit:
                    t = part.split(" ")
                    if len(t[0]) == len(part):
                        t = part.split("-")
                    if len(t[0]) == len(part):
                        t = part.split("_")
                    if len(t[0]) == len(part):
                        t = part.split(".")
                    a = " ".join(t[0 : math.ceil(len(t) / 2)])
                    b = " ".join(t[len(t) - math.floor(len(t) / 2) :])
                    temp += ["\n".join([a, b])]
                else:
                    temp += [part]
            except:
                temp += [part]
        i += 1
        new_body += [temp]
    TABLE = Table(data=new_body, repeatRows=1)
    TABLE.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )
    if shade == True:
        for each in set(hash_rows):
            bg_color = colors.red
            TABLE.setStyle(
                TableStyle([("BACKGROUND", (0, each), (-1, each), bg_color)])
            )
    table = []
    table.append(TABLE)
    doc = BaseDocTemplate(
        httpresponse, topMargin=12, bottomMargin=20, pagesize=landscape(A4)
    )

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    template = PageTemplate(id="table", frames=frame, onPage=head_footer)
    doc.addPageTemplates([template])

    doc.build(table)
    return doc
