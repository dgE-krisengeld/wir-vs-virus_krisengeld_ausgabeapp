from pathlib import Path

import qrcode


def render_paper_wallet(keystore_json: str, target_file: Path) -> None:
    generate_qr(target_file, keystore_json)


def generate_qr(file_path: Path, private_key: str) -> None:
    qr = make_qr()
    qr.add_data(private_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)


def make_qr() -> "qrcode.QRCode":
    # FIXME do we have to create an object every time?
    #   remove effects of the .add_data() after every write and reuse one object
    return qrcode.QRCode(
        version=27,  # can encode 5,024  bit with H error correct (125x125 modules)
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
