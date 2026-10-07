"""Tests for project_config.py — central configuration module."""
from pathlib import Path

import pytest


@pytest.fixture
def fake_repo(tmp_path):
    """Create a minimal repo structure with .claude/ and template/conventions.md."""
    (tmp_path / ".claude").mkdir()
    template_dir = tmp_path / ".claude" / "references" / "template"
    template_dir.mkdir(parents=True, exist_ok=True)
    conventions = template_dir / "conventions.md"
    conventions.write_text(
        "# TEMPLATE - PROJECT CONVENTIONS\n\n"
        "| Variable | Value | Description |\n"
        "|----------|-------|-------------|\n"
        "| `OUTPUT_DIR` | `_output` | Root output |\n"
        "| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plans folder |\n"
        "| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Scripts folder |\n",
        encoding="utf-8",
    )
    return tmp_path


def test_parse_config_extracts_variables(fake_repo):
    """project_config._parse_config should extract and resolve variables."""
    import project_config

    # Monkeypatch REPO_ROOT and reset cache
    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = fake_repo
        project_config._config = None
        project_config._warned_missing = False

        config = project_config._parse_config()
        assert "OUTPUT_DIR" in config
        assert config["OUTPUT_DIR"] == "_output"
        assert config["PLANS_DIR"] == "_output/plans"
        assert config["SCRIPTS_DIR"] == "_output/generated-scripts"
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_get_returns_value(fake_repo):
    """get() should return the resolved value for a known key."""
    import project_config

    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = fake_repo
        project_config._config = None
        project_config._warned_missing = False

        assert project_config.get("OUTPUT_DIR") == "_output"
        assert project_config.get("NONEXISTENT") is None
        assert project_config.get("NONEXISTENT", "fallback") == "fallback"
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_get_path_returns_absolute(fake_repo):
    """get_path() should return a Path relative to REPO_ROOT."""
    import project_config

    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = fake_repo
        project_config._config = None
        project_config._warned_missing = False

        result = project_config.get_path("OUTPUT_DIR")
        assert result == fake_repo / "_output"
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_get_path_allows_absolute_values(fake_repo, tmp_path):
    """get_path() must return absolute paths as-is (workspace mode: codebase outside REPO_ROOT)."""
    import project_config

    # Write a conventions file whose BACKEND_DIR is an absolute path to a sibling dir.
    sibling = tmp_path / "my-codebase" / "backend"
    sibling.mkdir(parents=True)
    conventions = fake_repo / "product-design" / "conventions.md"
    conventions.parent.mkdir(parents=True, exist_ok=True)
    conventions.write_text(
        "| Variable | Value | Description |\n"
        "|----------|-------|-------------|\n"
        f"| `BACKEND_DIR` | `{sibling.as_posix()}` | Backend root |\n",
        encoding="utf-8",
    )

    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = fake_repo
        project_config._config = None
        project_config._warned_missing = False

        result = project_config.get_path("BACKEND_DIR")
        assert result == sibling.resolve(), (
            "Absolute BACKEND_DIR must pass through get_path() unchanged "
            "(workspace mode sibling codebase)"
        )
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_get_path_rejects_traversal(fake_repo):
    """get_path() must still reject relative paths that escape REPO_ROOT."""
    import project_config

    conventions = fake_repo / "product-design" / "conventions.md"
    conventions.parent.mkdir(parents=True, exist_ok=True)
    conventions.write_text(
        "| Variable | Value | Description |\n"
        "|----------|-------|-------------|\n"
        "| `EVIL` | `../../etc/passwd` | evil traversal |\n",
        encoding="utf-8",
    )

    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = fake_repo
        project_config._config = None
        project_config._warned_missing = False

        result = project_config.get_path("EVIL")
        assert result is None, "Relative traversal paths must be rejected"
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_missing_conventions_returns_empty(tmp_path):
    """When neither conventions file exists, config should be empty."""
    import project_config

    original_root = project_config.REPO_ROOT
    original_config = project_config._config
    try:
        project_config.REPO_ROOT = tmp_path
        project_config._config = None
        project_config._warned_missing = False

        config = project_config._parse_config()
        assert config == {}
    finally:
        project_config.REPO_ROOT = original_root
        project_config._config = original_config


def test_diff_conventions(tmp_path):
    """diff_conventions should detect differences between two files."""
    import project_config

    project = tmp_path / "project.md"
    template = tmp_path / "template.md"

    project.write_text(
        "| `VAR_A` | `value1` | desc |\n"
        "| `VAR_B` | `changed` | desc |\n",
        encoding="utf-8",
    )
    template.write_text(
        "| `VAR_A` | `value1` | desc |\n"
        "| `VAR_B` | `original` | desc |\n"
        "| `VAR_C` | `new` | desc |\n",
        encoding="utf-8",
    )

    diff = project_config.diff_conventions(project, template)
    assert "VAR_C" in diff["missing_in_project"]
    assert len(diff["extra_in_project"]) == 0
    assert len(diff["value_differences"]) == 1
    assert diff["value_differences"][0]["key"] == "VAR_B"


# ---------------------------------------------------------------------------
# specify_default (plan-000022 Step 4, D-011)
# ---------------------------------------------------------------------------

_SPECIFY_TABLE_HEAD = (
    "# PROJECT CONVENTIONS\n\n"
    "## Review Configuration\n\n"
    "| Variable | Value | Description |\n"
    "|----------|-------|-------------|\n"
    "| `MINIMUM_REVIEW_DEPTH` | `light` | Review floor |\n"
)


def _write_conventions(root: Path, row: str | None, folder: str = "product-design") -> Path:
    """Write a minimal conventions.md under root/<folder>/, optionally with a SPECIFY_DEFAULT row."""
    target_dir = root / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    text = _SPECIFY_TABLE_HEAD + (row + "\n" if row is not None else "")
    path = target_dir / "conventions.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_specify_default_file_absent_is_on(tmp_path):
    import project_config

    assert project_config.specify_default(tmp_path) == "on"


def test_specify_default_does_not_fall_back_to_template(tmp_path):
    """No product-design/conventions.md: the template placeholder must not be read."""
    import project_config

    template_dir = tmp_path / ".claude" / "references" / "template"
    template_dir.mkdir(parents=True)
    (template_dir / "conventions.md").write_text(
        _SPECIFY_TABLE_HEAD + "| `SPECIFY_DEFAULT` | `off` | x |\n", encoding="utf-8"
    )
    assert project_config.specify_default(tmp_path) == "on"


def test_specify_default_line_absent_is_on(tmp_path):
    import project_config

    _write_conventions(tmp_path, None)
    assert project_config.specify_default(tmp_path) == "on"


@pytest.mark.parametrize(
    "row",
    [
        "| `SPECIFY_DEFAULT` |  | Specify switch |",
        "| `SPECIFY_DEFAULT` | `` | Specify switch |",
    ],
)
def test_specify_default_empty_value_is_on(tmp_path, row):
    import project_config

    _write_conventions(tmp_path, row)
    assert project_config.specify_default(tmp_path) == "on"


def test_specify_default_placeholder_is_on(tmp_path):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `{{SPECIFY_DEFAULT}}` | Specify switch |")
    assert project_config.specify_default(tmp_path) == "on"


def test_specify_default_on(tmp_path):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `on` | Specify switch |")
    assert project_config.specify_default(tmp_path) == "on"


def test_specify_default_off(tmp_path):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `off` | Specify switch |")
    assert project_config.specify_default(tmp_path) == "off"


def test_specify_default_off_without_backticks(tmp_path):
    """An `off` without backticks must not silently become `on`."""
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | off | Specify switch |")
    assert project_config.specify_default(tmp_path) == "off"


def test_specify_default_invalid_raises(tmp_path):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `talvez` | Specify switch |")
    with pytest.raises(ValueError, match="talvez"):
        project_config.specify_default(tmp_path)


def test_specify_default_reads_legacy_folder(tmp_path):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `off` | Specify switch |", folder="project-design")
    assert project_config.specify_default(tmp_path) == "off"


def test_specify_default_uses_given_root_not_repo_root(tmp_path):
    """A fixture root different from REPO_ROOT is read directly, without the module cache."""
    import project_config

    assert tmp_path.resolve() != project_config.REPO_ROOT.resolve()
    original_config = project_config._config
    try:
        project_config._config = {"SPECIFY_DEFAULT": "on"}
        _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `off` | Specify switch |")
        assert project_config.specify_default(tmp_path) == "off"
        assert project_config.specify_default(Path(tmp_path)) == "off"
    finally:
        project_config._config = original_config


def test_specify_default_without_root_reads_repo_root(tmp_path, monkeypatch):
    import project_config

    _write_conventions(tmp_path, "| `SPECIFY_DEFAULT` | `off` | Specify switch |")
    monkeypatch.setattr(project_config, "REPO_ROOT", tmp_path)
    assert project_config.specify_default() == "off"
