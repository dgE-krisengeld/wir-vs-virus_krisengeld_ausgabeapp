import shutil
import secrets
from pathlib import PosixPath

import pytest

from dge_ausgabeapp.qrcode import QRGenerator, derive_private_key_hash


def make_private_key():
    return secrets.token_bytes(32)


@pytest.fixture
def qr_generator():
    return QRGenerator()


@pytest.fixture
def output_directory():
    dir = PosixPath('./test_output')
    dir.mkdir()
    yield dir
    shutil.rmtree(dir)


def test_qr_code_generation(output_directory, qr_generator):
    priv_key = make_private_key()
    qr_generator.generate(output_directory, priv_key)
    
    file_name = f"{derive_private_key_hash(priv_key)}.jpg"
    path = output_directory / PosixPath(file_name)
    assert path.exists()
    # TODO read in qrcode and privkey again (if easily possible)





