from pathlib import PosixPath

import xxhash
import qrcode


def derive_private_key_hash(private_key):
    x = xxhash.xxh32()
    x.update(private_key)
    return x.hexdigest()[:16]


class QRGenerator:

    @staticmethod
    def make_qr():
        # FIXME do we have to create an object every time?
        #   remove effects of the .add_data() after every write and reuse one object
        return qrcode.QRCode(
            version=4, # can encode 288 bit with H error correct (33x33 modules)
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

    def generate(self, directory: PosixPath, private_key: bytes):
        if not directory.is_dir():
            raise NotADirectoryError("Provided path has to be a directory")

        qr = self.make_qr()
        qr.add_data(private_key)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"{derive_private_key_hash(private_key)}.jpg"
        img.save(directory / filename)
