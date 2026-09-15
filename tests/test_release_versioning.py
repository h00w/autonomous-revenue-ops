from scripts.release_evidence import ROOT, service_version
from scripts.release_version_check import release_version_errors


def test_release_version_is_aligned_across_runtime_manifests():
    version = service_version(ROOT)
    assert release_version_errors(ROOT, f"v{version}") == []


def test_release_tag_must_exactly_match_service_version():
    errors = release_version_errors(ROOT, "v999.0.0")
    assert errors == ["tag_version_mismatch:expected=v0.9.0:actual=v999.0.0"]
