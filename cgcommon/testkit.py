"""A tiny, dependency-free test + grading backend.

Every assignment ships a ``tests/checks.py`` module that exposes a function
``get_checks()`` returning a list of :class:`Check` objects. Each check
exercises one student-implemented function (matching the marking scheme one
file = one check) and raises ``AssertionError`` on failure.

Students run::

    python run_tests.py            # friendly table + "Validated X/Y"
    python run_tests.py --json     # machine-readable, used by the grader

The same checks power the grader, so the student-facing tests and the grade a
student receives are computed by *identical* code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from dataclasses import dataclass
from typing import Callable, List, Optional


def fixture_path(default_path: str) -> str:
    """Resolve the golden-fixture path, honouring an instructor override.

    Students always get ``default_path`` (the public fixture that ships with
    the assignment). The grader sets ``CG_GOLDEN_PATH`` to point the *same*
    assertion code at the private fixture, which holds different inputs and
    expected outputs. That way one body of checks serves both suites and the
    two can never drift apart.
    """
    return os.environ.get("CG_GOLDEN_PATH") or default_path


def data_dir(default_dir: str) -> str:
    """Resolve an assignment's ``data/`` directory, honouring an override.

    Used by assignments whose fixtures are not a single ``.npz`` (A5 loads a
    rig from ``data/``). The grader sets ``CG_DATA_DIR`` to swap in the
    private rig/scene assets.
    """
    return os.environ.get("CG_DATA_DIR") or default_dir


@dataclass
class Check:
    """One graded unit: a named function that raises on failure.

    Parameters
    ----------
    name:
        Identifier, conventionally the student source file stem
        (e.g. ``"rgb_to_gray"``). Used to look up points in the marking scheme.
    points:
        Marks awarded when this check passes (informational for students,
        authoritative for the grader's marking scheme override).
    fn:
        Zero-argument callable that imports the student's function and asserts
        on its behaviour. Raises ``AssertionError`` (or any exception) to fail.
    description:
        Short human-readable summary shown in the results table.
    """

    name: str
    points: float
    fn: Callable[[], None]
    description: str = ""


def run_checks(checks: List[Check]) -> List[dict]:
    """Run every check, capturing pass/fail and any error message."""
    results = []
    for c in checks:
        entry = {
            "name": c.name,
            "points": c.points,
            "description": c.description,
            "passed": False,
            "error": None,
        }
        try:
            c.fn()
            entry["passed"] = True
        except AssertionError as exc:
            entry["error"] = str(exc) or "assertion failed"
        except Exception as exc:  # noqa: BLE001 - report any failure cleanly
            entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["traceback"] = traceback.format_exc()
        results.append(entry)
    return results


def _print_hints(results: List[dict], hints: Optional[dict]) -> None:
    """Print a remediation hint for each failing check that has one.

    Assignments register hints for checks whose failure has a good debugging
    route (e.g. A2 can render the shading model one term at a time), so the
    test output points at the next thing to try rather than just saying "no".
    Checks sharing a hint are grouped, so the advice is printed once.
    """
    if not hints:
        return
    grouped = {}
    for r in results:
        if r["passed"]:
            continue
        hint = hints.get(r["name"])
        if hint:
            grouped.setdefault(hint.strip(), []).append(r["name"])
    if not grouped:
        return
    print("  Debugging help:")
    for hint, names in grouped.items():
        print(f"    for {', '.join(names)}:")
        for line in hint.splitlines():
            print("      " + line)
        print()


def _print_table(results: List[dict]) -> None:
    name_w = max((len(r["name"]) for r in results), default=4)
    name_w = max(name_w, 8)
    print()
    print(f"  {'STATUS':<6}  {'FUNCTION':<{name_w}}  DETAIL")
    print(f"  {'-'*6}  {'-'*name_w}  {'-'*40}")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        detail = r["description"] if r["passed"] else (r["error"] or "")
        if len(detail) > 60:
            detail = detail[:57] + "..."
        print(f"  {status:<6}  {r['name']:<{name_w}}  {detail}")
    print()


PUBLIC_WEIGHT = 0.3   # share of each function's marks decided by these tests


def practice_main(checks: List[Check], argv: Optional[List[str]] = None,
                  hints: Optional[dict] = None) -> int:
    """Entry point for an assignment's ``check_my_work.py``.

    This is the grader's scoring loop run against the **public** fixture only:
    the same checks, the same per-function marks, presented as a mark sheet so
    you can see where you stand before submitting. Your real mark also includes
    a private suite that runs these same checks against *different* inputs, so
    treat a full score here as "nothing is obviously wrong", not as a
    guarantee.
    """
    parser = argparse.ArgumentParser(
        description="Score your work against the public tests, grader-style."
    )
    parser.add_argument(
        "--only", metavar="NAME", default=None,
        help="score only the check with this name (e.g. --only rgb_to_gray)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="print the full failure message for each function that failed",
    )
    args = parser.parse_args(argv)

    selected = checks
    if args.only is not None:
        selected = [c for c in checks if c.name == args.only]
        if not selected:
            print(f"No check named {args.only!r}", file=sys.stderr)
            return 2

    results = run_checks(selected)
    possible = sum(r["points"] for r in results)
    earned = sum(r["points"] for r in results if r["passed"])
    name_w = max(max((len(r["name"]) for r in results), default=8), 8)

    print()
    print("  Practice mark sheet — public tests only")
    print(f"  {'FUNCTION':<{name_w}}  {'MARKS':>9}  RESULT")
    print(f"  {'-' * name_w}  {'-' * 9}  {'-' * 44}")
    for r in results:
        got = r["points"] if r["passed"] else 0
        marks = f"{got:g}/{r['points']:g}"
        detail = r["description"] if r["passed"] else (r["error"] or "failed")
        if not args.verbose and len(detail) > 44:
            detail = detail[:41] + "..."
        print(f"  {r['name']:<{name_w}}  {marks:>9}  {detail}")
    print(f"  {'-' * name_w}  {'-' * 9}  {'-' * 44}")
    print(f"  {'TOTAL':<{name_w}}  {f'{earned:g}/{possible:g}':>9}")
    print()

    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"  {len(failed)} function(s) still to fix: "
              f"{', '.join(r['name'] for r in failed)}")
        print("  Run  python run_tests.py --only <name>  to focus on one.")
        print()
        _print_hints(results, hints)
    else:
        print("  All public tests pass.")
    print()
    print(f"  Note: these public tests are worth {PUBLIC_WEIGHT:.0%} of the mark for")
    print("  each function. The remaining share comes from a private set of tests")
    print("  that calls the SAME functions with different inputs, so make sure your")
    print("  code solves the problem in general rather than matching these numbers.")
    print()

    return 0 if not failed else 1


def main(checks: List[Check], argv: Optional[List[str]] = None,
         hints: Optional[dict] = None) -> int:
    """Entry point for an assignment's ``run_tests.py``.

    Returns a process exit code: 0 if every check passed, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Run the unit checks for this assignment."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of a table (used by the grader)",
    )
    parser.add_argument(
        "--only",
        metavar="NAME",
        default=None,
        help="run only the check with this name (e.g. --only rgb_to_gray)",
    )
    args = parser.parse_args(argv)

    if args.only is not None:
        checks = [c for c in checks if c.name == args.only]
        if not checks:
            print(f"No check named {args.only!r}", file=sys.stderr)
            return 2

    results = run_checks(checks)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    earned = sum(r["points"] for r in results if r["passed"])
    possible = sum(r["points"] for r in results)

    # Grader mode: when CG_RESULTS_PATH is set (by Solutions/grade.py), write
    # the machine-readable results to that file and terminate immediately with
    # os._exit. The hard exit skips any atexit handlers that student code may
    # have registered, so the file the grader reads is exactly what this
    # function wrote (student stdout is ignored by the grader entirely).
    results_path = os.environ.get("CG_RESULTS_PATH")
    if results_path:
        payload = {
            "results": results,
            "passed": passed,
            "total": total,
            "points_earned": earned,
            "points_possible": possible,
        }
        with open(results_path, "w") as f:
            json.dump(payload, f)
            f.flush()
            os.fsync(f.fileno())
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0 if passed == total else 1)

    if args.json:
        print(
            json.dumps(
                {
                    "results": results,
                    "passed": passed,
                    "total": total,
                    "points_earned": earned,
                    "points_possible": possible,
                }
            )
        )
    else:
        _print_table(results)
        print(f"  Validated {passed}/{total} functions "
              f"({earned:g}/{possible:g} marks by the unit checks).")
        if passed != total:
            print("  Re-run after fixing the FAIL rows above. "
                  "Use --only <name> to focus on one function.")
        print()
        _print_hints(results, hints)

    return 0 if passed == total else 1
