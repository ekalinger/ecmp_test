import pytest
from fixtures.packets import TraffGenerate, Sniff

@pytest.fixture
def pcaps():
    return TraffGenerate()

@pytest.fixture
def sniff(request):
    sniff = Sniff(3)
    
    def fin():
        sniff.stop()
    request.addfinalizer(fin)
    return sniff
