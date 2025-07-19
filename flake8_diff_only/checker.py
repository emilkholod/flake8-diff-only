import ast
from typing import Any, ClassVar


class Flake8DiffOnlyChecker:
    name = "flake8-diff-only"
    version = "0.1.7"

    enabled: ClassVar[bool] = False

    def __init__(self, tree: ast.AST, filename: str):
        pass

    @classmethod
    def add_options(cls, parser: Any) -> None:
        parser.add_option(
            "--diff-only",
            action="store_true",
            default=False,
            help=(
                "Enable flake8-diff-only filtering"
                " (only show errors in changed lines)."
            ),
        )

    @classmethod
    def parse_options(cls, options: Any) -> None:
        cls.enabled = options.diff_only

    def run(self):  # type: ignore[no-untyped-def]
        return []
