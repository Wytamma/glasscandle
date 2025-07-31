"""Response parsing functions for various types of content."""

import re
from hashlib import sha256 as _sha256
from typing import Callable
import requests


def etag(res: requests.Response) -> str:
    """Extract and normalize ETag header."""
    val = res.headers.get("ETag")
    if not val:
        raise ValueError("No ETag header")
    # normalize: strip weak prefix and surrounding quotes
    v = val.strip()
    if v.startswith("W/"):
        v = v[2:]
    v = v.strip('"').strip()
    if not v:
        raise ValueError("Empty ETag after normalization")
    return v


def last_modified(res: requests.Response) -> str:
    """Extract Last-Modified header."""
    lm = res.headers.get("Last-Modified", "")
    if not lm:
        raise ValueError("No Last-Modified header")
    return lm


def sha256_of_body(res: requests.Response) -> str:
    """Calculate SHA256 hash of response body."""
    # Warning: URLProvider should HEAD‑check size before calling this.
    return _sha256(res.content).hexdigest()


def regex(pattern: str, group: int = 1) -> Callable[[requests.Response], str]:
    """Create a regex parser for response content."""
    rx = re.compile(pattern, re.M | re.S)
    
    def _parse(res: requests.Response) -> str:
        """
    Parses the response content using the provided parsing function.

    Args:
      response (requests.Response): The response object to parse.
      parse_func (Callable): The parsing function to use.

    Returns:
      Any: The parsed content.

    Examples:
      >>> _parse(response, json.loads)
      {'key': 'value'}
    """
        ctype = res.headers.get("Content-Type", "")
        # Optional guard: only attempt text or json
        if ("text" not in ctype) and ("json" not in ctype):
            # still attempt decode, but signal that this might be wrong
            pass
        text = res.text  # requests decodes using apparent encoding
        m = rx.search(text)
        if not m:
            raise ValueError(f"Pattern {pattern!r} not found")
        try:
            out = m.group(group)
        except IndexError:
            raise ValueError(f"Group {group} not present in match")
        out = out.strip()
        if not out:
            raise ValueError("Empty capture")
        return out
    
    return _parse


def jsonpath(path: str) -> Callable[[requests.Response], str]:
    """Create a JSONPath parser for JSON response content.
    
    Args:
        path: JSONPath expression to extract the value (e.g., "$.version", "$.data[0].tag_name")
    
    Returns:
        Parser function that extracts the value using the JSONPath expression
    """
    def _parse(res: requests.Response) -> str:
        """
    Parses the response content using the provided parsing function.

    Args:
      response (requests.Response): The response object to parse.
      parse_func (Callable): The parsing function to use.

    Returns:
      Any: The parsed content.

    Examples:
      >>> _parse(response, json.loads)
      {'key': 'value'}
    """
        try:
            data = res.json()
        except ValueError as e:
            raise ValueError(f"Invalid JSON response: {e}")
        
        # Simple JSONPath implementation for basic expressions
        # Supports: $.key, $.key.subkey, $.array[0], $.array[0].key
        value = data
        parts = path.strip("$").strip(".").split(".")
        
        for part in parts:
            if not part:
                continue
                
            # Handle array indexing like "array[0]"
            if "[" in part and "]" in part:
                key, bracket = part.split("[", 1)
                index = int(bracket.rstrip("]"))
                if key:
                    value = value[key]
                value = value[index]
            else:
                value = value[part]
        
        result = str(value).strip()
        if not result:
            raise ValueError(f"JSONPath {path!r} returned empty value")
        return result
    
    return _parse
