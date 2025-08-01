"""Provider modules for different version checking sources."""

from .base import Provider
from .bioconda import BiocondaProvider
from .conda import CondaProvider
from .condaforge import CondaForgeProvider
from .pypi import PyPIProvider
from .url import URLProvider

__all__ = ["Provider", "BiocondaProvider", "CondaProvider", "CondaForgeProvider", "PyPIProvider", "URLProvider"]
