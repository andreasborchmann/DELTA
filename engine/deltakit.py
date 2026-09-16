#!/usr/bin/env python3
"""
deltakit — minimales, deterministisches Delta-Werkzeug fuer DELTA-FORCE.

Ersetzt die Schreibseite von ULTRA_REF_SYS_DELTA_ENGINE_1_0.md.
Kein Modell im Schreibpfad. Kein input()-Gate. Keine Zeilenoffsets aus einer Vorschau.
Das Human Gate ist der Pull Request, nicht diese Datei.

Protokolltreue: ULTRA_PROTOCOL_SYS_DELTA_1_1.md, schema udp-1.0.
Bewusste Abweichung (1 Stueck, deklariert):
  target.context_hash ist hier PFLICHT fuer JEDE Datei, nicht nur fuer protected files.
  Begruendung: DELTA 1.1 Z.134 ist fail-open; die Engine lief in PBP-S006 mit
  'no_hash_provided' ohne Einwand durch. Fehlender Schutz darf kein Default sein.
  -> Solange DELTA 1.1 nicht nachgezogen ist, ist dieses Werkzeug strenger als sein
     Protokoll. Divergenz hier genannt statt verdeckt.

Subkommandos:
  check    <delta.json> [--repo DIR]   Fail-closed Pruefung. Exit 0 = anwendbar.
  render   <delta.json> [--repo DIR] [--write]   Neue Bytes erzeugen (stdout oder Datei).
  pr-body  <delta.json> [--repo DIR]   Markdown fuer den PR-Body.
  selftest [--corpus DIR ...]          Regressionssuite der Leseseite (R-2).

Exit-Codes: 0 ok · 2 abgelehnt (Grund auf stderr) · 3 Bedienfehler.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = "udp-1.0"
OPERATIONS = {"replace_section", "replace_lines", "insert_after", "append_to_section", "delete"}

_FENCE = re.compile(r"^(```|~~~)")
_HEAD = re.compile(r"^#{1,6}\s")


# ---------------------------------------------------------------- Leseseite
# 54 Zeilen aus der Engine, hier neu implementiert statt importiert.
# Differentialgetestet gegen 186 Ueberschriften des realen Korpus (selftest).

def heading_lines(lines: list[str]):
    """Indizes echter Ueberschriften. Zeilen in Code-Fences zaehlen nicht."""
    in_fence = False
    fence_tok = None
    for i, line in enumerate(lines):
        m = _FENCE.match(line)
        if m:
            tok = m.group(1)
            if not in_fence:
                in_fence, fence_tok = True, tok
            elif line.strip().startswith(fence_tok):
                in_fence, fence_tok = False, None
            continue
        if not in_fence and _HEAD.match(line):
            yield i, line


def find_section(content: str, heading: str) -> dict:
    """Exakter Anker. Mehrdeutig -> Ablehnung, nicht erster Treffer."""
    lines = content.split("\n")
    heads = list(heading_lines(lines))
    hits = [i for i, line in heads if line.rstrip() == heading.rstrip()]
    if not hits:
        return {"status": "fail", "reason": "section_not_found"}
    if len(hits) > 1:
        return {"status": "fail", "reason": f"anchor_ambiguous ({len(hits)} Treffer)"}
    start = hits[0]
    end = next((i for i, _ in heads if i > start), len(lines))
    return {
        "status": "ok",
        "start_line": start,
        "end_line": end,
        "section_text": "\n".join(lines[start:end]),
    }


def compute_section_hash(section_text: str) -> str:
    """Hasht den Abschnittstext inklusive Ueberschriftszeile.
    Konvention gegen den in PBP-S006 protokollierten Wert verifiziert."""
    return "sha256:" + hashlib.sha256(section_text.encode("utf-8")).hexdigest()


# ------------------------------------------------------- Operations-Semantik

def _kurz(s: str, n: int = 48) -> str:
    one = s.replace("\n", "⏎")
    return one if len(one) <= n else one[:n] + "…"


def plan_line_edits(body: str, edits) -> str:
    """replace_lines: jede Fundstelle muss genau einmal vorkommen.
    Null Treffer, mehrere Treffer oder Ueberlappung sind Ablehnungen, keine Warnungen.
    Der Autor liefert nur, was er aendert — unveraendertes kann er nicht beschaedigen."""
    if not isinstance(edits, list) or not edits:
        raise ValueError("replace_lines verlangt payload als nicht-leere Liste von {old,new}")
    problems: list[str] = []
    spans: list[tuple[int, int, str, int]] = []
    for i, e in enumerate(edits, 1):
        if not isinstance(e, dict) or not isinstance(e.get("old"), str) \
                or not isinstance(e.get("new"), str):
            problems.append(f"Edit {i}: erwartet {{\"old\": str, \"new\": str}}")
            continue
        old, new = e["old"], e["new"]
        if not old:
            problems.append(f"Edit {i}: old ist leer")
            continue
        if old == new:
            problems.append(f"Edit {i}: old und new sind identisch — kein Edit")
            continue
        n = body.count(old)
        if n == 0:
            problems.append(f"Edit {i}: old nicht gefunden — \"{_kurz(old)}\"")
        elif n > 1:
            problems.append(f"Edit {i}: old {n}x vorhanden, mehrdeutig — \"{_kurz(old)}\"")
        else:
            s = body.index(old)
            spans.append((s, s + len(old), new, i))
    if problems:
        raise ValueError(" | ".join(problems))
    spans.sort()
    for (_, e1, _, i1), (s2, _, _, i2) in zip(spans, spans[1:]):
        if e1 > s2:
            raise ValueError(f"Edits {i1} und {i2} ueberlappen dieselbe Textstelle")
    out, pos = [], 0
    for s, e, new, _ in spans:
        out.append(body[pos:s])
        out.append(new)
        pos = e
    out.append(body[pos:])
    return "".join(out)


def render_section(section_text: str, operation: str, payload) -> str | None:
    """Neuer Abschnittstext. None bei delete (Abschnitt faellt weg)."""
    lines = section_text.split("\n")
    heading = lines[0]
    body = lines[1:]

    if operation == "replace_lines":
        # Heading ist per Konstruktion geschuetzt: es wird nur der Body durchsucht.
        return heading + "\n" + plan_line_edits("\n".join(body), payload)

    # Leerzeilen am Abschnittsende erhalten, damit der Diff minimal bleibt.
    trailing = 0
    while trailing < len(body) and body[len(body) - 1 - trailing].strip() == "":
        trailing += 1
    tail = body[len(body) - trailing:] if trailing else []
    core = body[: len(body) - trailing] if trailing else body
    pay = payload.split("\n") if payload else []

    if operation == "replace_section":
        # Der payload IST der Body, verbatim. Kein Wiederanhaengen von tail:
        # sonst verdoppeln sich Abschluss-Leerzeilen, wenn der payload sie
        # bereits traegt (gemessener Off-by-one, 44 -> 45 statt 44 -> 44).
        return "\n".join([heading] + pay)
    if operation == "insert_after":
        new = [heading] + pay + core
    elif operation == "append_to_section":
        new = [heading] + core + pay
    elif operation == "delete":
        return None
    else:
        raise ValueError(f"unbekannte operation: {operation}")
    return "\n".join(new + tail)


# ------------------------------------------------------------------ Pruefung

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def resolve_doc(repo: Path, doc: str) -> tuple[Path | None, str]:
    """target.document traegt nur den Dateinamen, das Repo hat Ordner.
    Eindeutiger Treffer oder Ablehnung — nie der erste von mehreren."""
    direct = repo / doc
    if direct.is_file():
        return direct, "ok"
    name = Path(doc).name
    hits = [p for p in repo.rglob(name)
            if p.is_file() and ".git" not in p.parts]
    if not hits:
        return None, f"Zieldatei nicht im Repo gefunden: {doc}"
    if len(hits) > 1:
        rel = ", ".join(str(p.relative_to(repo)) for p in sorted(hits))
        return None, f"Zieldatei mehrdeutig ({len(hits)} Treffer): {rel}"
    return hits[0], "ok"


def _show(repo: Path, ref: str, relpath: str) -> str | None:
    r = _git(repo, "show", f"{ref}:{relpath}")
    return r.stdout if r.returncode == 0 else None


def check(delta: dict, repo: Path) -> tuple[bool, list[str], dict]:
    """Fail-closed. Jede Unklarheit ist eine Ablehnung, keine Warnung."""
    reasons: list[str] = []
    ctx: dict = {}

    if delta.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"schema_version != {SCHEMA_VERSION}")
    if not delta.get("delta_id"):
        reasons.append("delta_id fehlt")
    op = delta.get("operation")
    if op not in OPERATIONS:
        reasons.append(f"operation ungueltig: {op!r}")
    pay = delta.get("payload", "")
    if op == "delete":
        if pay not in ("", [], None):
            reasons.append("delete verlangt leeren payload")
    elif op == "replace_lines":
        if not isinstance(pay, list) or not pay:
            reasons.append("replace_lines verlangt payload als nicht-leere Liste von {old,new}")
    elif op in OPERATIONS:
        if not isinstance(pay, str) or not pay.strip():
            reasons.append("payload leer oder kein Text")
    if not (delta.get("meta") or {}).get("rationale"):
        reasons.append("meta.rationale fehlt")

    exp = (delta.get("meta") or {}).get("expected_lines")
    if not (isinstance(exp, dict)
            and isinstance(exp.get("before"), int)
            and isinstance(exp.get("after"), int)):
        reasons.append("meta.expected_lines {before:int, after:int} fehlt — "
                       "erklaerte Absicht ist Pflicht")

    target = delta.get("target") or {}
    doc, heading = target.get("document"), target.get("section_heading")
    if not doc or not heading:
        reasons.append("target.document oder target.section_heading fehlt")
        return False, reasons, ctx

    path, why = resolve_doc(repo, doc)
    if path is None:
        reasons.append(why)
        return False, reasons, ctx
    rel = str(path.relative_to(repo))

    content = path.read_text(encoding="utf-8")
    sec = find_section(content, heading)
    if sec["status"] != "ok":
        reasons.append(f"Abschnitt nicht adressierbar: {sec['reason']}")
        return False, reasons, ctx
    ctx.update(path=path, relpath=rel, content=content, section=sec)

    # --- Staleness, fail-closed. Kein Hash = keine Anwendung.
    declared = target.get("context_hash")
    actual = compute_section_hash(sec["section_text"])
    ctx["hash_actual"] = actual
    if not declared:
        reasons.append("context_hash fehlt — fail-closed, keine Anwendung ohne Anker")
    elif declared != actual:
        reasons.append(f"context_hash veraltet: deklariert {declared[:23]}… "
                       f"ist {actual[:23]}… — Ziel hat sich bewegt")

    # --- Zweite Ebene: hat sich die Datei seit base_sha bewegt?
    base = target.get("base_sha")
    if (repo / ".git").exists():
        if not base:
            reasons.append("base_sha fehlt — im Git-Repo Pflicht")
        else:
            r = _git(repo, "diff", "--quiet", base, "HEAD", "--", rel)
            if r.returncode == 1:
                reasons.append(f"Datei seit base_sha {base[:8]} veraendert")
            elif r.returncode not in (0, 1):
                reasons.append(f"base_sha nicht aufloesbar: {r.stderr.strip()[:80]}")
    elif base:
        reasons.append("base_sha angegeben, aber kein Git-Repo")

    # --- Operation trocken ausfuehren. Fehler der Operation sind Ablehnungsgruende.
    rendered: str | None = None
    op_ok = False
    if op in OPERATIONS:
        try:
            rendered = render_section(sec["section_text"], op, delta.get("payload", ""))
            op_ok = True
        except ValueError as e:
            reasons.append(str(e))

    # --- N-2: erklaerte Absicht gegen gemessene Wirkung.
    # Kein Schwellenwert. Grosse Loeschungen sind erlaubt — undeklarierte nicht.
    if op_ok and isinstance(exp, dict) and isinstance(exp.get("before"), int) \
            and isinstance(exp.get("after"), int):
        act_before = len(sec["section_text"].split("\n"))
        act_after = 0 if rendered is None else len(rendered.split("\n"))
        ctx["balance"] = (act_before, act_after)
        if (act_before, act_after) != (exp["before"], exp["after"]):
            reasons.append(
                f"Zeilenbilanz weicht von der Deklaration ab: erklaert "
                f"{exp['before']} -> {exp['after']}, gemessen {act_before} -> {act_after}")

    return (not reasons), reasons, ctx


def render(delta: dict, ctx: dict) -> str:
    sec = ctx["section"]
    lines = ctx["content"].split("\n")
    new_sec = render_section(sec["section_text"], delta["operation"],
                             delta.get("payload", ""))
    head, tail = lines[: sec["start_line"]], lines[sec["end_line"]:]
    middle = [] if new_sec is None else new_sec.split("\n")
    return "\n".join(head + middle + tail)


# --------------------------------------------------------------------- CLI

def _load(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def cmd_check(a) -> int:
    ok, reasons, _ = check(_load(a.delta), Path(a.repo))
    if ok:
        print("ok — anwendbar")
        return 0
    for r in reasons:
        print("ABGELEHNT:", r, file=sys.stderr)
    return 2


def cmd_render(a) -> int:
    delta = _load(a.delta)
    ok, reasons, ctx = check(delta, Path(a.repo))
    if not ok:
        for r in reasons:
            print("ABGELEHNT:", r, file=sys.stderr)
        return 2
    out = render(delta, ctx)
    if a.write:
        ctx["path"].write_text(out, encoding="utf-8")
        before = len(ctx["section"]["section_text"].split("\n"))
        after = 0 if delta["operation"] == "delete" else len(
            render_section(ctx["section"]["section_text"], delta["operation"],
                           delta.get("payload", "")).split("\n"))
        print(f"geschrieben: {ctx['path'].name} | Abschnitt {before} -> {after} Zeilen")
    else:
        sys.stdout.write(out)
    return 0


def cmd_pr_body(a) -> int:
    delta = _load(a.delta)
    ok, reasons, ctx = check(delta, Path(a.repo))
    if not ok:
        for r in reasons:
            print("ABGELEHNT:", r, file=sys.stderr)
        return 2
    new_content = render(delta, ctx)
    new_sec = find_section(new_content, delta["target"]["section_heading"])
    new_hash = (compute_section_hash(new_sec["section_text"])
                if new_sec["status"] == "ok" else "— (Abschnitt entfernt)")
    b = len(ctx["section"]["section_text"].split("\n"))
    aft = "0" if new_sec["status"] != "ok" else len(new_sec["section_text"].split("\n"))
    meta = delta.get("meta") or {}
    print(f"""## {delta['delta_id']}

| | |
|---|---|
| Zieldatei | `{delta['target']['document']}` |
| Abschnitt | `{delta['target']['section_heading']}` |
| Operation | `{delta['operation']}` |
| base_sha | `{delta['target'].get('base_sha','—')}` |
| context_hash vorher | `{ctx['hash_actual']}` |
| context_hash nachher | `{new_hash}` |
| Zeilenbilanz Abschnitt | **{b} -> {aft}** (so erklaert, so gemessen) |
| Autor | {meta.get('author','—')} |

**Rationale.** {meta.get('rationale','—')}

Der Diff unten ist von git berechnet, nicht von diesem Werkzeug erzeugt.
Human Gate = Merge-Freigabe. Ohne Freigabe bleibt die Aenderung im Branch.""")
    return 0


def cmd_selftest(a) -> int:
    """Leseseite gegen naive Referenz. Prueft genau das, worauf alles ruht (SUBSTRAT R-2)."""
    def naive(content, heading):
        lines = content.split("\n")
        start = next((i for i, l in enumerate(lines)
                      if l.rstrip() == heading.rstrip()), None)
        if start is None:
            return None
        end = next((j for j in range(start + 1, len(lines))
                    if _HEAD.match(lines[j])), len(lines))
        return "\n".join(lines[start:end])

    files = [p for d in a.corpus for p in sorted(Path(d).glob("*.md"))]
    tot = agree = fence_win = refused = 0
    for p in files:
        c = p.read_text(encoding="utf-8")
        for _, h in heading_lines(c.split("\n")):
            tot += 1
            r = find_section(c, h)
            if r["status"] != "ok":
                refused += 1
                continue
            if r["section_text"] == naive(c, h):
                agree += 1
            else:
                fence_win += 1

    cases = [
        ("Fence-Schutz", "## A\nx\n```\n## FAKE\n```\ny\n## B\n", "## A",
         lambda r: r["status"] == "ok" and "FAKE" in r["section_text"]),
        ("Mehrdeutig", "## A\n1\n## A\n2\n", "## A",
         lambda r: r["status"] == "fail" and "ambiguous" in r["reason"]),
        ("Unbekannt", "## A\n1\n", "## Z",
         lambda r: r["status"] == "fail" and r["reason"] == "section_not_found"),
        ("Teilanker", "## 2.1 X\n1\n", "2.1 X",
         lambda r: r["status"] == "fail"),
    ]
    print(f"Korpus: {len(files)} Dateien, {tot} Ueberschriften")
    print(f"  identisch zur naiven Referenz : {agree}")
    print(f"  Fence-bedingt abweichend      : {fence_win}  (deltakit ist hier die sichere Seite)")
    print(f"  bewusst abgelehnt             : {refused}  (mehrdeutige Anker)")
    bad = 0
    for name, doc, head, pred in cases:
        good = pred(find_section(doc, head))
        bad += not good
        print(f"  [{'ok ' if good else 'FAIL'}] {name}")
    return 0 if bad == 0 else 2


def cmd_verify(a) -> int:
    """Nach-Audit: Ist im Repository genau das gelandet, was das Delta gesagt hat?
    Rechnet aus dem base_sha neu und vergleicht byte-weise. Braucht keine Rechte."""
    import difflib
    delta = _load(a.delta)
    repo = Path(a.repo)
    t = delta.get("target") or {}
    doc, base, heading = t.get("document"), t.get("base_sha"), t.get("section_heading")
    if not base:
        print("NICHT PRUEFBAR: base_sha fehlt im Delta", file=sys.stderr)
        return 2

    path, why = resolve_doc(repo, doc)
    rel = str(path.relative_to(repo)) if path else doc
    base_content = _show(repo, base, rel)
    if base_content is None:
        print(f"NICHT PRUEFBAR: {rel} existiert nicht in {base[:8]}", file=sys.stderr)
        return 2

    sec = find_section(base_content, heading)
    if sec["status"] != "ok":
        print(f"NICHT PRUEFBAR: Abschnitt im Basisstand nicht adressierbar "
              f"({sec['reason']})", file=sys.stderr)
        return 2
    base_hash = compute_section_hash(sec["section_text"])
    if t.get("context_hash") and t["context_hash"] != base_hash:
        print(f"BEFUND: context_hash passt nicht zum Basisstand — das Delta wurde "
              f"gegen einen anderen Stand gebaut als gegen {base[:8]}", file=sys.stderr)
        return 2

    rendered = render(delta, {"content": base_content, "section": sec})
    actual = _show(repo, a.head, rel)
    if actual is None:
        print(f"BEFUND: {rel} existiert in {a.head} nicht mehr", file=sys.stderr)
        return 2

    if rendered == actual:
        print(f"verifiziert — {rel} in {a.head} ist byte-identisch mit dem, "
              f"was {delta.get('delta_id')} aus {base[:8]} erzeugt")
        return 0

    print(f"BEFUND: {rel} weicht ab von dem, was {delta.get('delta_id')} erzeugt haette.",
          file=sys.stderr)
    d = list(difflib.unified_diff(rendered.split("\n"), actual.split("\n"),
                                  "LAUT DELTA", f"IM REPO ({a.head})", lineterm="", n=1))
    print("\n".join(d[: a.max_lines]), file=sys.stderr)
    if len(d) > a.max_lines:
        print(f"… {len(d) - a.max_lines} weitere Zeilen", file=sys.stderr)
    return 2


def cmd_audit(a) -> int:
    """Gate-Abdeckung messen. Verhindert keinen Bypass — macht ihn sichtbar.
    Konvention: die delta_id steht in der Commit-Nachricht."""
    repo = Path(a.repo)
    ids: dict[str, str] = {}
    for p in sorted(Path(a.deltas).rglob("*.json")) if Path(a.deltas).is_dir() else []:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("delta_id"):
            ids[d["delta_id"]] = (d.get("target") or {}).get("document", "?")

    rng = f"{a.start}..{a.head}" if a.start else a.head
    r = _git(repo, "log", "--format=%H%x1f%s", "--reverse", rng, "--", a.artefacts)
    if r.returncode != 0:
        print("git log fehlgeschlagen:", r.stderr.strip()[:160], file=sys.stderr)
        return 3
    rows = [l.split("\x1f", 1) for l in r.stdout.splitlines() if l.strip()]

    covered, naked = [], []
    for sha, subject in rows:
        hit = next((i for i in ids if i in subject), None)
        files = _git(repo, "show", "--name-only", "--format=", sha).stdout.split()
        (covered if hit else naked).append((sha[:8], hit, subject, files))

    print(f"Bereich: {rng} | Pfad: {a.artefacts}/ | Deltas bekannt: {len(ids)}")
    print(f"Commits auf Artefakten: {len(rows)} | mit Delta-Bezug: {len(covered)} "
          f"| OHNE: {len(naked)}")
    for sha, hit, subject, _ in covered:
        print(f"  [ok ] {sha}  {hit}  {subject[:60]}")
    for sha, _, subject, files in naked:
        print(f"  [OHNE DELTA] {sha}  {subject[:60]}")
        for f in files:
            print(f"               {f}")
    unused = [i for i in ids if not any(h == i for _, h, _, _ in covered)]
    if unused:
        print("Deltas ohne zugehoerigen Commit:", ", ".join(sorted(unused)))
    if naked:
        print("\nBefund: Aenderungen an Artefakten ohne Delta-Bezug. In einem Repo ohne "
              "durchgesetzte Branch Protection ist das nicht verhinderbar, aber messbar.")
    return 2 if naked else 0


def cmd_hash(a) -> int:
    """Liefert das Anker-Paket fuer den Delta-Autor: Abschnittstext, Hash, base_sha."""
    repo = Path(a.repo)
    path, why = resolve_doc(repo, a.document)
    if path is None:
        print(why, file=sys.stderr)
        return 2
    rel = str(path.relative_to(repo))
    sec = find_section(path.read_text(encoding="utf-8"), a.heading)
    if sec["status"] != "ok":
        print(f"Abschnitt nicht adressierbar: {sec['reason']}", file=sys.stderr)
        return 2
    body = sec["section_text"].split("\n")
    head = _git(repo, "rev-parse", "HEAD")
    print(f"document      : {Path(rel).name}")
    print(f"pfad_im_repo  : {rel}")
    print(f"section_heading: {a.heading}")
    print(f"base_sha      : {head.stdout.strip() or '— (kein Git-Repo)'}")
    print(f"context_hash  : {compute_section_hash(sec['section_text'])}")
    print(f"expected_lines.before: {len(body)}")
    print("--- ABSCHNITT, WORTGETREU (Ueberschrift + Body) ---")
    print(sec["section_text"])
    print("--- ENDE ABSCHNITT ---")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="deltakit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("check", cmd_check), ("render", cmd_render), ("pr-body", cmd_pr_body)):
        p = sub.add_parser(name)
        p.add_argument("delta")
        p.add_argument("--repo", default=".")
        if name == "render":
            p.add_argument("--write", action="store_true")
        p.set_defaults(fn=fn)
    p = sub.add_parser("selftest")
    p.add_argument("--corpus", nargs="+", default=["."])
    p.set_defaults(fn=cmd_selftest)

    p = sub.add_parser("hash")
    p.add_argument("document")
    p.add_argument("--heading", required=True)
    p.add_argument("--repo", default=".")
    p.set_defaults(fn=cmd_hash)

    p = sub.add_parser("verify")
    p.add_argument("delta")
    p.add_argument("--repo", default=".")
    p.add_argument("--head", default="HEAD")
    p.add_argument("--max-lines", type=int, default=60)
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("audit")
    p.add_argument("--repo", default=".")
    p.add_argument("--start", default=None, help="Nullpunkt-Commit (exklusiv)")
    p.add_argument("--head", default="HEAD")
    p.add_argument("--deltas", default="deltas")
    p.add_argument("--artefacts", default="artefakte")
    p.set_defaults(fn=cmd_audit)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
