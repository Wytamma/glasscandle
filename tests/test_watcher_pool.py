import pytest
from glasscandle.pool import Pool
from glasscandle.providers import BiocondaProvider, PyPIProvider, URLProvider


@pytest.fixture
def pool():
    return Pool()


def test_initialization(pool):
    assert len(pool.bioconda) == 0
    assert len(pool.pypi) == 0
    assert len(pool.url) == 0
    assert len(pool.custom) == 0
    assert len(pool.custom_callbacks) == 0


def test_add_provider(pool):
    pool.bioconda["test_bioconda"] = BiocondaProvider()
    assert len(pool.bioconda) == 1

    pool.pypi["test_pypi"] = PyPIProvider()
    assert len(pool.pypi) == 1

    pool.url["test_url"] = URLProvider()
    assert len(pool.url) == 1


def test_add_custom_function(pool):
    def custom_func(response):
        return response.text

    pool.custom["test_custom"] = custom_func
    assert len(pool.custom) == 1


def test_add_custom_callback(pool):
    def on_change_func(old_value, new_value, provider):
        print(f"Value changed from {old_value} to {new_value} for provider {provider}")

    pool.custom_callbacks["test_callback"] = on_change_func
    assert len(pool.custom_callbacks) == 1
