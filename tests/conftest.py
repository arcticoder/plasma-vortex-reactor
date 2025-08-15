import sys, pathlib, pytest
root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))


def pytest_configure(config):
	config.addinivalue_line("markers", "slow: marks tests as slow (deselect with -m 'not slow')")
