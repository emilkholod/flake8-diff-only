import ast

import pytest

from flake8_diff_only.checker import Flake8DiffOnlyChecker


@pytest.fixture
def run_patched_checker(monkeypatch: pytest.MonkeyPatch):
    """
    Возвращает патченный класс Flake8DiffOnlyChecker,
    в котором _load_git_diff возвращает фиктивный diff.
    """

    # Подменяем diff: только строка 2 в файле test_file.py изменена
    monkeypatch.setattr(
        Flake8DiffOnlyChecker,
        "_load_git_diff",
        classmethod(lambda cls: {"test_file.py": {2}}),
    )

    def make_checker(code: str, fake_errors: list[tuple[int, int, str, type]]):
        tree = ast.parse(code)
        checker = Flake8DiffOnlyChecker(tree, filename="test_file.py")

        # Подменим _original_errors на заглушку
        monkeypatch.setattr(checker, "_original_errors", lambda: fake_errors)

        return list(checker.run())  # type: ignore[no-untyped-call]

    return make_checker


def test_error_on_changed_line(run_patched_checker):
    code = "x = 1\ny=2\nz = 3"
    fake_errors = [(2, 0, "T100 Fake error", Flake8DiffOnlyChecker)]
    results = run_patched_checker(code, fake_errors)

    assert results == fake_errors, "Ошибка должна быть показана на изменённой строке"


def test_no_error_on_unchanged_line(run_patched_checker):
    code = "x = 1\ny = 2\nz = 3"
    fake_errors = [(1, 0, "T100 Fake error", Flake8DiffOnlyChecker)]
    results = run_patched_checker(code, fake_errors)

    assert results == [], "Ошибка на неизменённой строке должна быть отфильтрована"


def test_multiple_errors_some_filtered(run_patched_checker):
    code = "x=1\ny = 2\nz = 3"
    fake_errors = [
        (1, 0, "T101 E1", Flake8DiffOnlyChecker),
        (2, 0, "T102 E2", Flake8DiffOnlyChecker),
        (3, 0, "T103 E3", Flake8DiffOnlyChecker),
    ]
    results = run_patched_checker(code, fake_errors)

    assert results == [fake_errors[1]], "Ожидалась только ошибка на строке 2"
