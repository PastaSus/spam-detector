"""Machine-checkable Definition-of-Done gates (story 4.3, bmad-plan DoD).

Static gates that eyeballing cannot prove: no circular imports, type hints
on public APIs, docstrings on public functions, no print debugging outside
the CLI (where print is user-facing output), and append-only PROMPTS_LOG.md
ID hygiene (AD-5).
"""
from __future__ import annotations

import ast
import importlib
import py_compile
import re
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = sorted(p.stem for p in ROOT.glob("*.py"))
UI_MODULES = {"cli"}  # print() is user-facing output only here
COMPILE_TARGETS = [f"{module}.py" for module in MODULES] + ["tests"]

PROMPT_ID = re.compile(r"^(INIT|PM|ARCH|DEV|QA)-(\d{3})$")
PROMPT_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PROMPT_STATUSES = {"Done", "In progress"}


def _tree(module: str) -> ast.Module:
    return ast.parse((ROOT / f"{module}.py").read_text(encoding="utf-8"))


def _first_party_imports(tree: ast.Module) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in MODULES:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in MODULES:
                    found.add(alias.name.split(".")[0])
    return found


def _public_functions(tree: ast.Module) -> list[tuple[str, ast.FunctionDef]]:
    found: list[tuple[str, ast.FunctionDef]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                found.append((node.name, node))
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not child.name.startswith("_"):
                        found.append((f"{node.name}.{child.name}", child))
    return found


def _resolve(name: str, module: str) -> object:
    target = importlib.import_module(module)
    for part in name.split("."):
        target = getattr(target, part)
    if isinstance(target, property):
        target = target.fget
    return target


def test_no_circular_imports() -> None:
    graph = {module: _first_party_imports(_tree(module)) for module in MODULES}
    visited: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        state = visited.get(node, 0)
        if state == 2:
            return
        if state == 1:
            raise AssertionError(f"circular import: {' -> '.join([*stack, node])}")
        visited[node] = 1
        for dependency in sorted(graph[node]):
            visit(dependency, [*stack, node])
        visited[node] = 2

    for module in MODULES:
        visit(module, [])


def test_public_functions_have_docstrings() -> None:
    missing = [
        f"{module}.{name}"
        for module in MODULES
        for name, node in _public_functions(_tree(module))
        if ast.get_docstring(node) is None
    ]

    assert not missing, f"public functions without docstrings: {missing}"


def test_public_functions_are_typed() -> None:
    untyped = []
    for module in MODULES:
        for name, node in _public_functions(_tree(module)):
            args = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg is not None:
                args.append(node.args.vararg)
            if node.args.kwarg is not None:
                args.append(node.args.kwarg)
            if args and args[0].arg in {"self", "cls"}:
                args = args[1:]
            if any(arg.annotation is None for arg in args):
                untyped.append(f"{module}.{name} (params)")
            if node.returns is None:
                untyped.append(f"{module}.{name} (returns)")
            try:
                typing.get_type_hints(_resolve(name, module))
            except Exception as exc:
                untyped.append(f"{module}.{name} (unresolvable: {exc})")

    assert not untyped, f"public functions without type hints: {untyped}"


def test_modules_and_classes_have_docstrings() -> None:
    missing = []
    for module in MODULES:
        tree = _tree(module)
        if ast.get_docstring(tree) is None:
            missing.append(f"{module} (module)")
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is None:
                missing.append(f"{module}.{node.name} (class)")

    assert not missing, f"modules/classes without docstrings: {missing}"


def _is_banned_output(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id in {"print", "pprint", "breakpoint"}:
        return True
    if isinstance(func, ast.Attribute) and func.attr in {"pprint", "write"}:
        target = func.value
        while isinstance(target, ast.Attribute):
            target = target.value
        return isinstance(target, ast.Name) and target.id in {"pprint", "sys"}
    return False


def test_no_print_debugging() -> None:
    offenders = []
    for module in MODULES:
        if module in UI_MODULES:
            continue
        for node in ast.walk(_tree(module)):
            if _is_banned_output(node):
                offenders.append(f"{module}.py:{node.lineno}")

    assert not offenders, f"print-style output outside the CLI: {offenders}"


def test_compile_targets_exist_and_compile() -> None:
    targets: list[Path] = []
    for entry in COMPILE_TARGETS:
        path = ROOT / entry
        if path.is_dir():
            targets.extend(sorted(path.glob("*.py")))
        else:
            targets.append(path)

    assert targets, "no compile targets found"
    for path in targets:
        assert path.is_file(), f"DoD compile target missing: {path}"
        py_compile.compile(str(path), doraise=True)


def test_prompts_log_ids() -> None:
    rows = []
    for line in (ROOT / "PROMPTS_LOG.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if not cells or cells[0] in {"ID", "---"}:
            continue
        assert len(cells) == 6, f"prompt-log row without 6 cells: {line!r}"
        rows.append(cells)

    assert rows, "no prompt-log rows found"

    seen: set[str] = set()
    last_number: dict[str, int] = {}
    for cells in rows:
        prompt_id, date, persona, prompt, artifacts, status = cells
        match = PROMPT_ID.fullmatch(prompt_id)
        assert match is not None, f"malformed prompt ID: {prompt_id!r}"
        assert prompt_id not in seen, f"duplicate prompt ID: {prompt_id}"
        seen.add(prompt_id)
        phase, number = match.group(1), int(match.group(2))
        assert number >= last_number.get(phase, 0), f"out-of-order ID: {prompt_id}"
        last_number[phase] = number
        assert PROMPT_DATE.fullmatch(date), f"malformed date: {date!r}"
        assert persona, f"empty persona: {prompt_id}"
        assert prompt, f"empty prompt: {prompt_id}"
        assert status in PROMPT_STATUSES, f"unexpected status: {status!r}"
