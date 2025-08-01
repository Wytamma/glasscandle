import pytest
from glasscandle.version_constraints import VersionConstraint


class TestVersionConstraint:
    """Test version constraint parsing and evaluation."""
    
    def test_parse_simple_constraints(self):
        """Test parsing of simple version constraints."""
        constraint = VersionConstraint(">=1.21")
        assert len(constraint.constraints) == 1
        assert constraint.constraints[0][0] == ">="
        
        constraint = VersionConstraint("<2.0")
        assert len(constraint.constraints) == 1
        assert constraint.constraints[0][0] == "<"
    
    def test_parse_multiple_constraints(self):
        """Test parsing of multiple comma-separated constraints."""
        constraint = VersionConstraint(">=1.21,<2.0")
        assert len(constraint.constraints) == 2
        assert constraint.constraints[0][0] == ">="
        assert constraint.constraints[1][0] == "<"
    
    def test_parse_compatible_release(self):
        """Test parsing of compatible release constraint."""
        constraint = VersionConstraint("~=1.21")
        assert len(constraint.constraints) == 1
        assert constraint.constraints[0][0] == "~="
    
    def test_parse_exact_version(self):
        """Test parsing of exact version constraint."""
        constraint = VersionConstraint("==1.21.0")
        assert len(constraint.constraints) == 1
        assert constraint.constraints[0][0] == "=="
    
    def test_parse_not_equal(self):
        """Test parsing of not-equal constraint."""
        constraint = VersionConstraint("!=2.0")
        assert len(constraint.constraints) == 1
        assert constraint.constraints[0][0] == "!="
    
    def test_parse_invalid_constraint(self):
        """Test that invalid constraints raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version constraint"):
            VersionConstraint("invalid")
        
        with pytest.raises(ValueError, match="Invalid version constraint"):
            VersionConstraint(">=")
    
    def test_parse_empty_constraint(self):
        """Test that empty constraint is handled."""
        constraint = VersionConstraint("")
        assert len(constraint.constraints) == 0
        assert constraint.matches("1.0.0") is True  # No constraints means all match
    
    def test_matches_greater_than_equal(self):
        """Test >= constraint matching."""
        constraint = VersionConstraint(">=1.21")
        
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.22.0") is True
        assert constraint.matches("2.0.0") is True
        assert constraint.matches("1.20.9") is False
    
    def test_matches_less_than(self):
        """Test < constraint matching."""
        constraint = VersionConstraint("<2.0")
        
        assert constraint.matches("1.99.9") is True
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("2.0.0") is False
        assert constraint.matches("2.1.0") is False
    
    def test_matches_range_constraint(self):
        """Test range constraint (>=x,<y) matching."""
        constraint = VersionConstraint(">=1.21,<2.0")
        
        assert constraint.matches("1.20.9") is False
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.21.5") is True
        assert constraint.matches("1.99.9") is True
        assert constraint.matches("2.0.0") is False
        assert constraint.matches("2.1.0") is False
    
    def test_matches_compatible_release(self):
        """Test ~= (compatible release) constraint matching."""
        constraint = VersionConstraint("~=1.21")
        
        assert constraint.matches("1.20.9") is False
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.21.5") is True
        assert constraint.matches("1.21.99") is True
        assert constraint.matches("1.22.0") is False
        assert constraint.matches("2.0.0") is False
    
    def test_matches_exact_version(self):
        """Test == (exact version) constraint matching."""
        constraint = VersionConstraint("==1.21.0")
        
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.21.1") is False
        assert constraint.matches("1.20.0") is False
        assert constraint.matches("2.21.0") is False
    
    def test_matches_not_equal(self):
        """Test != (not equal) constraint matching."""
        constraint = VersionConstraint("!=2.0.0")
        
        assert constraint.matches("1.99.9") is True
        assert constraint.matches("2.0.0") is False
        assert constraint.matches("2.0.1") is True
        assert constraint.matches("2.1.0") is True
    
    def test_matches_invalid_version(self):
        """Test that invalid version strings don't match."""
        constraint = VersionConstraint(">=1.21")
        
        assert constraint.matches("invalid") is False
        assert constraint.matches("") is False
        assert constraint.matches("1.21.x") is False
    
    def test_filter_versions(self):
        """Test filtering a list of versions."""
        constraint = VersionConstraint(">=1.21,<2.0")
        versions = ["1.20.0", "1.21.0", "1.21.5", "1.22.0", "2.0.0", "2.1.0"]
        
        filtered = constraint.filter_versions(versions)
        expected = ["1.21.0", "1.21.5", "1.22.0"]
        assert filtered == expected
    
    def test_filter_versions_with_invalid(self):
        """Test filtering versions with some invalid version strings."""
        constraint = VersionConstraint(">=1.21")
        versions = ["1.20.0", "invalid", "1.21.0", "", "1.22.0", "1.21.x"]
        
        filtered = constraint.filter_versions(versions)
        expected = ["1.21.0", "1.22.0"]
        assert filtered == expected
    
    def test_get_latest_valid(self):
        """Test getting the latest valid version."""
        constraint = VersionConstraint(">=1.21,<2.0")
        versions = ["1.20.0", "1.21.0", "1.21.5", "1.22.0", "2.0.0", "2.1.0"]
        
        latest = constraint.get_latest_valid(versions)
        assert latest == "1.22.0"
    
    def test_get_latest_valid_no_matches(self):
        """Test getting latest valid when no versions match."""
        constraint = VersionConstraint(">=3.0")
        versions = ["1.20.0", "1.21.0", "1.21.5", "1.22.0", "2.0.0", "2.1.0"]
        
        latest = constraint.get_latest_valid(versions)
        assert latest is None
    
    def test_get_latest_valid_empty_list(self):
        """Test getting latest valid from empty version list."""
        constraint = VersionConstraint(">=1.21")
        versions = []
        
        latest = constraint.get_latest_valid(versions)
        assert latest is None
    
    def test_get_latest_valid_sorting_edge_cases(self):
        """Test latest valid with versions that might not sort correctly as strings."""
        constraint = VersionConstraint(">=1.9")
        versions = ["1.9", "1.10", "1.2", "2.0"]  # String sort would give wrong order
        
        latest = constraint.get_latest_valid(versions)
        assert latest == "2.0"
    
    def test_string_representation(self):
        """Test string representations of constraints."""
        constraint = VersionConstraint(">=1.21,<2.0")
        assert str(constraint) == ">=1.21,<2.0"
        assert "VersionConstraint" in repr(constraint)
        assert ">=1.21,<2.0" in repr(constraint)
    
    def test_complex_version_patterns(self):
        """Test with more complex version patterns."""
        constraint = VersionConstraint(">=1.21.0,!=1.21.5,<2.0.0")
        
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.21.4") is True
        assert constraint.matches("1.21.5") is False  # Excluded by !=
        assert constraint.matches("1.21.6") is True
        assert constraint.matches("1.99.0") is True
        assert constraint.matches("2.0.0") is False
    
    def test_pre_release_versions(self):
        """Test handling of pre-release versions."""
        constraint = VersionConstraint(">=1.21.0")
        
        # The packaging library should handle these correctly
        assert constraint.matches("1.21.0a1") is False  # Pre-release is less than release
        assert constraint.matches("1.21.0rc1") is False
        assert constraint.matches("1.21.0") is True
        assert constraint.matches("1.21.1") is True
