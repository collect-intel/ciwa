# ciwa/tests/test_identifiable.py

import pytest
from ciwa.models.identifiable import Identifiable


def test_identifiable_initialization():
    identifiable = Identifiable()
    assert identifiable.uuid is not None
    assert isinstance(identifiable.uuid, str)


if __name__ == "__main__":
    pytest.main()
