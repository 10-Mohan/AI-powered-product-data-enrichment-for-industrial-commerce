from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=15)
pdf.cell(200, 10, txt="Sample PDF Document", ln=1, align='C')
pdf.cell(200, 10, txt="This is a test PDF for extraction.", ln=2, align='C')
pdf.output("data/samples/sample.pdf")
