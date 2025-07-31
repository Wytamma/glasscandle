"""Provider pool for managing collections of different provider types."""

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional
import requests

from .providers import BiocondaProvider, CondaProvider, PyPIProvider, URLProvider


# Custom function type for legacy custom parsers
CustomFunc = Callable[[requests.Response], str]
OnChangeFunc = Callable[[str, str, str], None]


@dataclass
class Pool:
    """Collection of all registered providers by type."""
    bioconda: Dict[str, BiocondaProvider] = field(default_factory=dict)
    conda: Dict[str, CondaProvider] = field(default_factory=dict)
    pypi: Dict[str, PyPIProvider] = field(default_factory=dict)
    url: Dict[str, URLProvider] = field(default_factory=dict)
    custom: Dict[str, CustomFunc] = field(default_factory=dict)
    custom_callbacks: Dict[str, Optional[OnChangeFunc]] = field(default_factory=dict)
