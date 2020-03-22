from pathlib import Path

import qrcode
from pdfrw import PageMerge, PdfReader, PdfWriter
from qrcode.image.pil import PilImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

PDF_TEMPLATE_PATH = Path(__file__).parent.joinpath("template.pdf")


def render_paper_wallet(
    qr_data: str, target_file_path: Path, _pdf_template_path: Path = PDF_TEMPLATE_PATH
) -> None:
    qr_image = generate_qr(qr_data=qr_data)
    generate_pdf_with_qr(
        pdf_template_path=_pdf_template_path, qr_image=qr_image, target_pdf_path=target_file_path
    )


def generate_pdf_with_qr(
    pdf_template_path: Path, qr_image: PilImage, target_pdf_path: Path
) -> None:
    pdf_qr = Canvas("qr.pdf", pagesize=A4)
    img_reader = ImageReader(qr_image.get_image())
    pdf_qr.drawImage(img_reader, 6 * cm, 8 * cm, 8.5 * cm, 8.5 * cm)
    merge_qr = PageMerge().add(PdfReader(fdata=pdf_qr.getpdfdata()).pages[0])[0]
    pdf_target = PdfReader(fdata=pdf_template_path.read_bytes())
    for page in pdf_target.pages:
        PageMerge(page).add(merge_qr).render()
    PdfWriter(target_pdf_path, trailer=pdf_target).write()


def generate_qr(qr_data: str) -> PilImage:
    qr = make_qr()
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def make_qr() -> qrcode.QRCode:
    # FIXME do we have to create an object every time?
    #   remove effects of the .add_data() after every write and reuse one object
    return qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=4,)
