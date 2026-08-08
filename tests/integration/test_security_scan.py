from ai_governance.infrastructure.security_scan import scan_obvious_secrets


def test_secret_scanner_reports_text_file_and_ignores_binary_suffix(tmp_path):
    fake_secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    (tmp_path / "sample.txt").write_text(fake_secret, encoding="utf-8")
    (tmp_path / "sample.bin").write_text(fake_secret, encoding="utf-8")

    findings = scan_obvious_secrets(tmp_path)

    assert len(findings) == 1
    assert findings[0].code == "INV-008"
    assert findings[0].message == "possible secret in sample.txt"
    assert findings[0].source == "sample.txt"


def test_secret_scanner_ignores_git_directory(tmp_path):
    fake_secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config.txt").write_text(fake_secret, encoding="utf-8")

    assert scan_obvious_secrets(tmp_path) == []
