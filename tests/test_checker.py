import pytest
from flake8.checker import FileChecker

from flake8_diff_only import patch
from flake8_diff_only.checker import Flake8DiffOnlyChecker


@pytest.fixture
def run_patched_checker(monkeypatch: pytest.MonkeyPatch):
    filename = "test_file.py"

    # Подменяем diff: только строка 2 в файле test_file.py изменена
    monkeypatch.setattr(patch, "get_changed_lines", lambda filename: {2})

    monkeypatch.setattr(Flake8DiffOnlyChecker, "enabled", True)

    def make_checker(fake_errors: list[tuple[str, int, int, str, str | None]]):

        # Подменим _original_errors на заглушку
        checker = FileChecker(filename=filename, plugins=None, options=None)
        monkeypatch.setattr(
            patch, "_original_run_checks", lambda self: (filename, fake_errors, [])
        )

        return list(checker.run_checks())

    return make_checker


def test_error_on_changed_line(run_patched_checker):
    fake_errors = [("T100", 2, 0, "Fake error", None)]
    results = run_patched_checker(fake_errors)

    assert results[1] == fake_errors, "Ошибка должна быть показана на изменённой строке"


def test_no_error_on_unchanged_line(run_patched_checker):
    fake_errors = [("T100", 1, 0, "Fake error", None)]
    results = run_patched_checker(fake_errors)

    assert results[1] == [], "Ошибка на неизменённой строке должна быть отфильтрована"


def test_multiple_errors_some_filtered(run_patched_checker):
    fake_errors = [
        ("T100", 1, 0, "Fake error", None),
        ("T100", 2, 0, "Fake error", None),
        ("T100", 3, 0, "Fake error", None),
    ]
    results = run_patched_checker(fake_errors)

    assert results[1] == [fake_errors[1]], "Ожидалась только ошибка на строке 2"
