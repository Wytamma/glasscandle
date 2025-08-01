"""Version constraint utilities for filtering package versions."""

import re
from typing import Optional, List
from packaging import version


class VersionConstraint:
    """
    Parse and evaluate version constraints.
    
    Supports constraints like:
    - ">=1.21,<2" (greater than or equal to 1.21, less than 2)
    - "~=1.21" (compatible release, equivalent to ">=1.21,<1.22")
    - "==1.21.0" (exact version)
    - ">1.20" (greater than 1.20)
    - "!=2.0" (not equal to 2.0)
    """
    
    def __init__(self, constraint_string: str):
        """
        Initialize version constraint from string.
        
        Args:
            constraint_string: Version constraint string (e.g., ">=1.21,<2")
        """
        self.constraint_string = constraint_string.strip()
        self.constraints = self._parse_constraints()
    
    def _parse_constraints(self) -> List[tuple]:
        """Parse constraint string into list of (operator, version) tuples."""
        if not self.constraint_string or self.constraint_string == "*":
            return []
        
        constraints = []
        # Split by comma and parse each constraint
        parts = [part.strip() for part in self.constraint_string.split(',')]
        
        for part in parts:
            if not part:
                continue
                
            # Match operator and version with improved regex
            # Prevent operator characters in version part to avoid partial matches
            match = re.match(r'^(~=|==|!=|<=|>=|<|>)\s*([^<>=!~\s].*)$', part)
            if not match:
                raise ValueError(f"Invalid version constraint: {part}")
            
            operator, version_str = match.groups()
            version_str = version_str.strip()
            
            try:
                parsed_version = version.parse(version_str)
                constraints.append((operator, parsed_version))
            except Exception as e:
                raise ValueError(f"Invalid version in constraint '{part}': {e}")
        
        return constraints
    
    def matches(self, version_string: str) -> bool:
        """
        Check if a version string satisfies all constraints.
        
        Args:
            version_string: Version string to check
            
        Returns:
            True if version satisfies all constraints, False otherwise
        """
        if not self.constraints:
            return True  # No constraints means all versions are valid
        
        try:
            ver = version.parse(version_string)
        except Exception:
            # If we can't parse the version, assume it doesn't match
            return False
        
        for operator, constraint_version in self.constraints:
            if not self._evaluate_constraint(ver, operator, constraint_version):
                return False
        
        return True
    
    def _evaluate_constraint(self, ver: version.Version, operator: str, constraint_version: version.Version) -> bool:
        """Evaluate a single constraint against a version."""
        if operator == "==":
            return ver == constraint_version
        elif operator == "!=":
            return ver != constraint_version
        elif operator == ">":
            return ver > constraint_version
        elif operator == ">=":
            return ver >= constraint_version
        elif operator == "<":
            return ver < constraint_version
        elif operator == "<=":
            return ver <= constraint_version
        elif operator == "~=":
            # Compatible release: same major.minor, but patch can be higher
            return (ver >= constraint_version and 
                    ver.release[:2] == constraint_version.release[:2])
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def filter_versions(self, versions: List[str]) -> List[str]:
        """
        Filter a list of versions to only those matching constraints.
        
        Args:
            versions: List of version strings
            
        Returns:
            Filtered list of versions that match constraints
        """
        return [v for v in versions if self.matches(v)]
    
    def get_latest_valid(self, versions: List[str]) -> Optional[str]:
        """
        Get the latest version that satisfies constraints.
        
        Args:
            versions: List of version strings
            
        Returns:
            Latest valid version or None if no versions match
        """
        valid_versions = self.filter_versions(versions)
        if not valid_versions:
            return None
        
        # Sort versions and return the latest
        try:
            sorted_versions = sorted(valid_versions, key=version.parse, reverse=True)
            return sorted_versions[0]
        except Exception:
            # If sorting fails, fall back to string max
            return max(valid_versions)
    
    def __str__(self) -> str:
        """String representation of constraints."""
        return self.constraint_string
    
    def __repr__(self) -> str:
        """Detailed representation of constraints."""
        return f"VersionConstraint('{self.constraint_string}')"
