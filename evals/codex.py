#!/usr/bin/env python3
"""The eval cases run in Codex, headless, as `make eval` runs them in Claude Code: each case's prompt, with the skill and
without, in a project of its own, graded by the case's graders; the delta is what the skill adds. Needs Codex signed in."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals"
SKILLS = ROOT / "skills"
RESULTS = CASES / "results"

# A grader's `tool` is a Claude Code tool; Codex reports what it did as items of these types.
ITEMS_FOR_TOOL = {
    "Bash": ("command_execution",),
    "Read": ("command_execution",),
    "Glob": ("command_execution",),
    "Grep": ("command_execution",),
    "Write": ("file_change",),
    "Edit": ("file_change",),
    "WebFetch": ("web_search", "command_execution"),
}

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {"verdict": {"type": "string", "enum": ["PASS", "FAIL"]}, "reason": {"type": "string"}},
    "required": ["verdict", "reason"],
    "additionalProperties": False,
}


def front_matter(text: str) -> tuple[dict[str, object], str]:
    """The `---` block a case or grader opens with, read as the flat YAML it is, and the body after it."""
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    fields: dict[str, object] = {}
    for line in head.splitlines():
        key, sep, raw = line.partition(":")
        if not sep or line.startswith((" ", "\t")):
            continue
        fields[key.strip()] = scalar(raw.strip())
    return fields, body.strip()


def scalar(raw: str) -> object:
    if raw.startswith("[") and raw.endswith("]"):
        return [scalar(part.strip()) for part in raw[1:-1].split(",") if part.strip()]
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def scaffold_script(case_dir: Path) -> Path | None:
    """`context.scaffold_script` of a `case.yaml`, where the case starts from a project."""
    case_yaml = case_dir / "case.yaml"
    if not case_yaml.is_file():
        return None
    in_context = False
    for line in case_yaml.read_text().splitlines():
        if not line.startswith((" ", "\t")):
            in_context = line.strip() == "context:"
            continue
        if in_context:
            key, sep, raw = line.partition(":")
            if sep and key.strip() == "scaffold_script":
                return case_dir / str(scalar(raw.strip()))
    return None


@dataclass
class Grader:
    name: str
    kind: str
    rubric: str
    fields: dict[str, object]

    @property
    def indicator(self) -> bool:
        """`tool_used: Skill` says whether the skill fired, as the harness reads it under an ablation; it is no score."""
        return self.kind == "tool_used" and self.fields.get("tool") == "Skill"


@dataclass
class Case:
    name: str
    path: Path
    prompt: str
    fields: dict[str, object]
    graders: list[Grader]
    scaffold: Path | None

    @property
    def timeout(self) -> int:
        return int(self.fields.get("timeout_seconds", 600))  # type: ignore[arg-type]

    @property
    def runs(self) -> int:
        return int(self.fields.get("runs", 3))  # type: ignore[arg-type]


def load_cases(pattern: str) -> list[Case]:
    cases = []
    for path in sorted(CASES.iterdir()):
        if not (path / "prompt.md").is_file() or not fnmatch.fnmatch(path.name, pattern):
            continue
        fields, prompt = front_matter((path / "prompt.md").read_text())
        graders = []
        for file in sorted((path / "graders").glob("*.md")):
            meta, rubric = front_matter(file.read_text())
            graders.append(Grader(file.stem, str(meta.get("type", "llm")), rubric, meta))
        cases.append(Case(path.name, path, prompt, fields, graders, scaffold_script(path)))
    return cases


@dataclass
class Run:
    events: list[dict[str, object]] = field(default_factory=list)
    last_message: str = ""
    exit_code: int | None = None
    timed_out: bool = False
    stderr: str = ""

    @property
    def items(self) -> list[dict[str, object]]:
        return [e["item"] for e in self.events if e.get("type") == "item.completed" and isinstance(e.get("item"), dict)]  # type: ignore[misc]


def codex_exec(prompt: str, cwd: Path, timeout: int, model: str | None, extra: list[str]) -> Run:
    """`codex exec` over `prompt` in `cwd`, its events read from the JSONL it prints; the prompt on stdin, never the command line."""
    out = cwd / ".codex-last-message.md"
    cmd = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "-C", str(cwd), "-o", str(out), *extra]
    if model:
        cmd += ["-m", model]
    cmd.append("-")
    run = Run()
    try:
        done = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, check=False)
        run.exit_code, stdout, run.stderr = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as expired:
        run.timed_out = True
        stdout = expired.stdout.decode() if isinstance(expired.stdout, bytes) else (expired.stdout or "")
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            run.events.append(event)
    if out.is_file():
        run.last_message = out.read_text()
        out.unlink()
    return run


def agent_run(case: Case, with_skill: bool, skill: Path, work: Path, model: str | None) -> Run:
    """One run of the case's prompt: a fresh project, scaffolded where the case says, the skill linked into it or not."""
    if case.scaffold is not None:
        subprocess.run(["bash", str(case.scaffold)], cwd=work, check=True, capture_output=True)
    if with_skill:
        skills = work / ".agents" / "skills"
        skills.mkdir(parents=True)
        (skills / skill.name).symlink_to(skill, target_is_directory=True)
    # Writes in the project and the network, which the skill's fetches need; approvals cannot be asked for.
    policy = ["--sandbox", "workspace-write", "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=true"]
    return codex_exec(case.prompt, work, case.timeout, model, policy)


def transcript(run: Run) -> str:
    """The run as a judge reads it: what Codex did and said, in order, its reasoning left out."""
    lines = []
    for item in run.items:
        kind = item.get("type")
        if kind == "agent_message":
            lines.append(f"[agent] {item.get('text', '')}")
        elif kind == "command_execution":
            lines.append(f"[command] {item.get('command', '')} -> exit {item.get('exit_code')}\n{str(item.get('aggregated_output', ''))[:4000]}")
        elif kind == "file_change":
            lines.append(f"[files] {json.dumps(item.get('changes', []))}")
        elif kind in ("mcp_tool_call", "web_search"):
            lines.append(f"[{kind}] {json.dumps({k: v for k, v in item.items() if k not in ('id', 'type')})[:2000]}")
    if run.timed_out:
        lines.append("[harness] the run hit its time limit")
    return "\n".join(lines)


def skill_fired(run: Run, skill: Path) -> int:
    """How many items read the skill: Codex opens a `SKILL.md` it selects with a command of its own, nothing marks it otherwise."""
    marker = f"/{skill.name}/SKILL.md"
    return sum(1 for item in run.items if marker in json.dumps(item))


def grade_tool_used(grader: Grader, run: Run, skill: Path) -> tuple[bool, str]:
    if grader.indicator:
        fired = skill_fired(run, skill)
        return fired > 0, f"the skill's SKILL.md read {fired} time(s)"
    tool = str(grader.fields.get("tool", ""))
    kinds = ITEMS_FOR_TOOL.get(tool, (tool,))
    pattern = grader.fields.get("input_match")
    regex = re.compile(str(pattern)) if pattern else None
    count = 0
    for item in run.items:
        if item.get("type") not in kinds:
            continue
        haystack = str(item.get("command", "")) if item.get("type") == "command_execution" else json.dumps(item)
        if regex is None or regex.search(haystack):
            count += 1
    low = int(grader.fields.get("min", 1 if "max" not in grader.fields else 0))  # type: ignore[arg-type]
    high = grader.fields.get("max")
    ok = count >= low and (high is None or count <= int(high))  # type: ignore[arg-type]
    return ok, f"{count} matching {'/'.join(kinds)} item(s); wanted {low}..{high if high is not None else '∞'}"


def grade_llm(grader: Grader, run: Run, judge_dir: Path, model: str | None) -> tuple[bool, str]:
    """The rubric put to Codex as a judge, over the reply or, where the grader says `focus: trace`, the whole run."""
    evidence = transcript(run) if grader.fields.get("focus") == "trace" else run.last_message
    prompt = (
        "You grade one run of a coding agent against a rubric. Answer with the verdict the rubric defines, PASS or FAIL, "
        "and one sentence of reason. Judge only what the evidence shows.\n\n"
        f"## Rubric\n{grader.rubric}\n\n## Evidence ({'the whole run' if grader.fields.get('focus') == 'trace' else 'the final reply'})\n{evidence}\n"
    )
    schema = judge_dir / "verdict.schema.json"
    schema.write_text(json.dumps(VERDICT_SCHEMA))
    judged = codex_exec(prompt, judge_dir, 300, model, ["--sandbox", "read-only", "--output-schema", str(schema)])
    try:
        verdict = json.loads(judged.last_message)
        return verdict["verdict"] == "PASS", str(verdict.get("reason", ""))
    except (json.JSONDecodeError, KeyError, TypeError):
        return False, f"the judge gave no verdict (exit {judged.exit_code})"


@dataclass
class Graded:
    arm: str
    index: int
    results: dict[str, tuple[bool, str]]
    fired: bool
    timed_out: bool

    @property
    def score(self) -> float:
        scored = [ok for name, (ok, _) in self.results.items() if name != "__indicator__"]
        return sum(scored) / len(scored) if scored else 1.0


def grade(case: Case, run: Run, skill: Path, judge_dir: Path, model: str | None, arm: str, index: int) -> Graded:
    results: dict[str, tuple[bool, str]] = {}
    fired = False
    for grader in case.graders:
        if grader.kind == "tool_used":
            ok, why = grade_tool_used(grader, run, skill)
            if grader.indicator:
                fired = ok
                results["__indicator__"] = (ok, why)
                continue
        elif grader.kind == "llm":
            ok, why = grade_llm(grader, run, judge_dir, model)
        else:
            ok, why = False, f"grader type {grader.kind!r} is not run here"
        results[grader.name] = (ok, why)
    return Graded(arm, index, results, fired, run.timed_out)


def preflight(skill: Path) -> None:
    if shutil.which("codex") is None:
        sys.exit("codex is not on the PATH: install Codex (npm install -g @openai/codex) and sign in (codex login)")
    status = subprocess.run(["codex", "login", "status"], capture_output=True, text=True, check=False)
    if "not logged in" in (status.stdout + status.stderr).lower():
        sys.exit("Codex is not signed in: run `codex login`")
    user_copy = Path.home() / ".agents" / "skills" / skill.name
    if user_copy.exists():
        sys.exit(f"{user_copy} exists, so the run without the skill would still see it: unlink it first")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default="*", help="a glob over the case names (default: every case)")
    parser.add_argument("--runs", type=int, default=None, help="runs per case and arm (default: the case's `runs`, else 3)")
    parser.add_argument("--skill", default=None, help="the skill under skills/ to test (default: the one there)")
    parser.add_argument("--ablation", choices=["with-without", "none"], default="with-without")
    parser.add_argument("--model", default=None, help="Codex's model for the runs and the judge")
    parser.add_argument("--threshold", type=float, default=1.0, help="exit 1 where a case's score with the skill is below this")
    parser.add_argument("--keep-temp", action="store_true", help="keep each run's project folder")
    parser.add_argument("--dry-run", action="store_true", help="print what would run, run nothing")
    args = parser.parse_args()

    skills = sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    skill = SKILLS / args.skill if args.skill else (skills[0] if len(skills) == 1 else None)
    if skill is None or not (skill / "SKILL.md").is_file():
        sys.exit(f"name the skill with --skill: {', '.join(p.name for p in skills)}")
    cases = load_cases(args.case)
    if not cases:
        sys.exit(f"no case matches {args.case!r}")
    arms = ["with", "without"] if args.ablation == "with-without" else ["with"]

    if args.dry_run:
        for case in cases:
            runs = args.runs or case.runs
            print(f"{case.name}: {runs} run(s) x {arms}, {case.timeout}s each, scaffold={case.scaffold.name if case.scaffold else None}, graders={[g.name for g in case.graders]}")
        return 0

    preflight(skill)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RESULTS / f"codex-{stamp}"
    out.mkdir(parents=True)
    report = [f"# Codex eval {stamp}", "", "| case | arm | run | score | skill fired | graders |", "|---|---|---|---|---|---|"]
    failed = False
    for case in cases:
        graded: list[Graded] = []
        for arm in arms:
            for index in range(1, (args.runs or case.runs) + 1):
                work = Path(tempfile.mkdtemp(prefix=f"telmoni-eval-{case.name}-{arm}-"))
                judge_dir = Path(tempfile.mkdtemp(prefix="telmoni-eval-judge-"))
                try:
                    run = agent_run(case, arm == "with", skill, work, args.model)
                    result = grade(case, run, skill, judge_dir, args.model, arm, index)
                finally:
                    if not args.keep_temp:
                        shutil.rmtree(work, ignore_errors=True)
                    shutil.rmtree(judge_dir, ignore_errors=True)
                folder = out / case.name / f"{arm}-{index}"
                folder.mkdir(parents=True)
                (folder / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in run.events))
                (folder / "last-message.md").write_text(run.last_message)
                (folder / "stderr.log").write_text(run.stderr)
                (folder / "grades.json").write_text(json.dumps({k: {"pass": ok, "why": why} for k, (ok, why) in result.results.items()}, indent=2))
                graded.append(result)
                marks = " ".join(f"{'✓' if ok else '✗'} {name}" for name, (ok, _) in result.results.items() if name != "__indicator__")
                report.append(f"| {case.name} | {arm} | {index} | {result.score:.2f} | {'yes' if result.fired else 'no'} | {marks}{' (timed out)' if result.timed_out else ''} |")
                print(report[-1], flush=True)
        mean = lambda arm: (lambda xs: sum(xs) / len(xs) if xs else 0.0)([g.score for g in graded if g.arm == arm])  # noqa: E731
        with_mean = mean("with")
        line = f"{case.name}: with {with_mean:.2f}" + (f", without {mean('without'):.2f}, Δ {with_mean - mean('without'):+.2f}" if "without" in arms else "")
        report += ["", line]
        print(line, flush=True)
        failed |= with_mean < args.threshold
    (out / "report.md").write_text("\n".join(report) + "\n")
    print(f"\nreport: {out / 'report.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
