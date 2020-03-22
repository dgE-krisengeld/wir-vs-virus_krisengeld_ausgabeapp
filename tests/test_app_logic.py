from datetime import datetime

import pytest
from stdnum.exceptions import ValidationError

from dge_ausgabeapp.app import tax_id_to_filename_stem, tax_id_to_password


@pytest.mark.parametrize(
    ("tax_id", "valid"),
    [("36 574 261 809", True), ("36574261809", True), ("36 574 261 808", False), ("12", False)],
)
def test_tax_id_to_password(tax_id: str, valid: bool) -> None:
    if not valid:
        with pytest.raises(ValidationError):
            tax_id_to_password(tax_id)
        return

    password = tax_id_to_password(tax_id)
    assert len(password) == 11
    assert password == tax_id.replace(" ", "").encode()


def test_tax_id_to_filename_stem() -> None:
    filename_stem = tax_id_to_filename_stem(
        "36 574 261 809", lambda: datetime(2020, 1, 2, 3, 4, 5)
    )
    assert filename_stem == "wallet_36-574-261-809_2020-01-02T03-04-05"
