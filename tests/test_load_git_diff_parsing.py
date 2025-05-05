import subprocess

import pytest

from flake8_diff_only.checker import Flake8DiffOnlyChecker


@pytest.fixture
def patched_load_git_diff(monkeypatch: pytest.MonkeyPatch):

    def make_checker(diff_output: str):
        monkeypatch.setattr(
            subprocess, "check_output", lambda *args, **kwargs: diff_output.encode()
        )
        # Сброс Singleton, чтобы подхватить новый diff
        Flake8DiffOnlyChecker._instance = None

        return Flake8DiffOnlyChecker._load_git_diff()

    return make_checker


def test_load_git_diff_parsing(patched_load_git_diff):
    diff_output = """\
diff --git a/test_file.py b/test_file.py
index e69de29..4b825dc 100644
--- a/test_file.py
+++ b/test_file.py
@@ -0,0 +1,3 @@
+print("Hello")
+print("World")
+print("!")
"""
    result = patched_load_git_diff(diff_output)

    assert "test_file.py" in result, "Имя файла должно быть распознано"
    assert result["test_file.py"] == {1, 2, 3}, "Ожидались изменённые строки 1, 2 и 3"


def test_diff_single_line_no_comma(patched_load_git_diff):
    diff_output = """\
diff --git a/test.py b/test.py
index 123..456 100644
--- a/test.py
+++ b/test.py
@@ -4 +45 @@
+print("single")
"""
    result = patched_load_git_diff(diff_output)
    assert result["test.py"] == {45}, "Ожидалась только строка 45"


def test_diff_header_parse_error(patched_load_git_diff):
    diff_output = """\
diff --git a/f.py b/f.py
index 123..456 100644
--- a/f.py
+++ b/f.py
@@ nonsense header @@
+print("broken")
"""
    result = patched_load_git_diff(diff_output)
    assert result == {}, "Файл с некорректным заголовком не должен попадать"


def test_diff_missing_filename(patched_load_git_diff):
    diff_output = """\
@@ -1,2 +1,2 @@
+line 1
+line 2
"""
    result = patched_load_git_diff(diff_output)
    assert result == {}, "Без '+++ b/' строки файл должен быть проигнорирован"


def test_diff_empty(patched_load_git_diff):
    diff_output = ""
    result = patched_load_git_diff(diff_output)
    assert result == {}, "Пустой вывод 'git diff' должен вернуть пустой словарь"
