#!/usr/bin/env python3
"""
deltakit — minimales, deterministisches Delta-Werkzeug fuer DELTA-FORCE.
Fassung S014 (PBP-S014, 2026-10-06): Inhaltspruefung gegen einen vorgegebenen Zieltext; Luecken
W-1 bis W-5, 1b-4, 1b-5 und 1b-9 behoben; Kontrollfaelle in engine/kontrollfaelle.json.

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

Inhaltspruefung (seit Fassung S014, Typ I — Argument des Werkzeugs, kein Feld im Auftragsformat):
  check, render und pr-body verlangen --zieltext DATEI oder ausdruecklich --ohne-inhalt.
  Mit --zieltext muss der Abschnitt nach dem Delta bytegenau dem Zieltext gleichen. Die Datei traegt
  den Abschnitt wortgetreu, Ueberschrift zuerst, genau ein Zeilenumbruch am Ende.
  Fehlt beides, endet der Aufruf mit 3: Fehlender Schutz darf kein Default sein.

Subkommandos:
  check    <delta.json> (--zieltext DATEI | --ohne-inhalt) [--repo DIR]   Fail-closed Pruefung. Exit 0 = anwendbar.
  render   <delta.json> (--zieltext DATEI | --ohne-inhalt) [--repo DIR] [--write]   Neue Bytes erzeugen.
  pr-body  <delta.json> (--zieltext DATEI | --ohne-inhalt) [--repo DIR]   Markdown fuer den PR-Body; liest HEAD.
  hash     <dokument> --heading H [--repo DIR]   Anker-Paket fuer den Delta-Autor; auch absolute Pfade.
  verify   <delta.json> [--repo DIR] [--head REF] [--max-lines N]   Nach-Audit, byteweise.
  audit    [--repo DIR] [--start SHA] [--head REF] [--deltas DIR] [--artefacts PFAD]   Gate-Abdeckung.
  selftest [--corpus DIR ...] [--kontrollfaelle DATEI] [--repo DIR] [--nur-leseseite]   Leseseite und Kontrollfaelle.

Exit-Codes: 0 ok · 2 abgelehnt oder Befund (Grund auf stderr) · 3 Bedienfehler. Nie 1.
Zeilenenden: Gelesen und geschrieben werden Bytes. Dateien mit Windows-Zeilenenden lehnt das Werkzeug
ab, statt sie still umzuschreiben.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FASSUNG = "S014"
SCHEMA_VERSION = "udp-1.0"
OPERATIONS = {"replace_section", "replace_lines", "insert_after", "append_to_section", "delete"}
EXIT_OK, EXIT_ABGELEHNT, EXIT_BEDIENFEHLER = 0, 2, 3
MAX_DIFF = 20

_FENCE = re.compile(r"^(```|~~~)")
_HEAD = re.compile(r"^#{1,6}\s")


class Bedienfehler(Exception):
    """Fehler im Aufruf oder in einer Eingabe, die nicht das Delta ist. Exit 3."""


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
    if operation == "delete":
        return None
    if not isinstance(payload, str):
        raise ValueError(f"{operation} verlangt payload als Text")
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
    else:
        raise ValueError(f"unbekannte operation: {operation}")
    return "\n".join(new + tail)


# ------------------------------------------------------------------ Dateien

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """git mit Bytes. Nie Textmodus: Zeilenenden werden nicht umgewandelt (1b-5)."""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def _git_text(repo: Path, *args: str) -> tuple[int, str, str]:
    r = _git(repo, *args)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def _show(repo: Path, ref: str, relpath: str) -> bytes | None:
    r = _git(repo, "show", f"{ref}:{relpath}")
    return r.stdout if r.returncode == 0 else None


def _text(raw: bytes) -> str | None:
    """UTF-8 ohne Umwandlung der Zeilenenden; None, wenn es kein UTF-8 ist."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def resolve_doc(repo: Path, doc: str) -> tuple[Path | None, str | None, str]:
    """target.document traegt meist nur den Dateinamen, das Repo hat Ordner.
    Eindeutiger Treffer oder Ablehnung — nie der erste von mehreren.
    Gibt (absoluter Pfad, Pfad relativ zum Repo, Grund) zurueck. Absolute Pfade gehen auch (W-5)."""
    basis = repo.resolve()
    p = Path(doc)
    direct = p if p.is_absolute() else basis / p
    if direct.is_file():
        try:
            rel = direct.resolve().relative_to(basis)
        except ValueError:
            return None, None, f"Pfad liegt nicht im Repository: {doc}"
        return direct.resolve(), rel.as_posix(), "ok"
    name = p.name
    hits = [q for q in basis.rglob(name)
            if q.is_file() and ".git" not in q.relative_to(basis).parts]
    if not hits:
        return None, None, f"Zieldatei nicht im Repo gefunden: {doc}"
    if len(hits) > 1:
        rel = ", ".join(q.relative_to(basis).as_posix() for q in sorted(hits))
        return None, None, f"Zieldatei mehrdeutig ({len(hits)} Treffer): {rel}"
    return hits[0], hits[0].relative_to(basis).as_posix(), "ok"


# ------------------------------------------------------------------ Pruefung

def _ist_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _diff_zeilen(soll: str, ist: str, links: str = "ZIELTEXT", rechts: str = "NACH DEM DELTA") -> list[str]:
    d = list(difflib.unified_diff(soll.split("\n"), ist.split("\n"), links, rechts, lineterm="", n=0))
    if len(d) > MAX_DIFF:
        d = d[:MAX_DIFF] + [f"… {len(d) - MAX_DIFF} weitere Zeilen"]
    return d


def check(delta, repo: Path, ziel: str | None = None, quelle: str = "arbeitsbaum") -> tuple[bool, list[str], dict]:
    """Fail-closed. Jede Unklarheit ist eine Ablehnung, keine Warnung.
    ziel: Zieltext des Abschnitts (Inhaltspruefung) oder None (ausdruecklich ohne).
    quelle: "arbeitsbaum" liest die Zieldatei aus dem Arbeitsbaum, "HEAD" aus Git (fuer pr-body, 1b-9)."""
    reasons: list[str] = []
    ctx: dict = {"details": []}
    if not isinstance(delta, dict):
        return False, ["Delta ist kein JSON-Objekt"], ctx

    if delta.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"schema_version != {SCHEMA_VERSION}")
    did = delta.get("delta_id")
    if not (isinstance(did, str) and did):
        reasons.append("delta_id fehlt")
    op = delta.get("operation")
    op_gueltig = isinstance(op, str) and op in OPERATIONS
    if not op_gueltig:
        reasons.append(f"operation ungueltig: {op!r}")
    pay = delta.get("payload", "")
    pay_ok = op_gueltig
    if op == "delete":
        if pay not in ("", [], None):
            reasons.append("delete verlangt leeren payload")
            pay_ok = False
    elif op == "replace_lines":
        if not isinstance(pay, list) or not pay:
            reasons.append("replace_lines verlangt payload als nicht-leere Liste von {old,new}")
            pay_ok = False
    elif op_gueltig:
        if not isinstance(pay, str) or not pay.strip():
            reasons.append("payload leer oder kein Text")
            pay_ok = False

    meta = delta.get("meta")
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        reasons.append("meta ist kein JSON-Objekt")
        meta = {}
    rationale = meta.get("rationale")
    if not (isinstance(rationale, str) and rationale.strip()):
        reasons.append("meta.rationale fehlt")
    exp = meta.get("expected_lines")
    exp_ok = isinstance(exp, dict) and _ist_int(exp.get("before")) and _ist_int(exp.get("after"))
    if not exp_ok:
        reasons.append("meta.expected_lines {before:int, after:int} fehlt — "
                       "erklaerte Absicht ist Pflicht")

    target = delta.get("target")
    if target is None:
        target = {}
    if not isinstance(target, dict):
        reasons.append("target ist kein JSON-Objekt")
        return False, reasons, ctx
    doc, heading = target.get("document"), target.get("section_heading")
    if not (isinstance(doc, str) and doc) or not (isinstance(heading, str) and heading):
        reasons.append("target.document oder target.section_heading fehlt")
        return False, reasons, ctx

    path, rel, why = resolve_doc(repo, doc)
    if path is None:
        reasons.append(why)
        return False, reasons, ctx

    if quelle == "HEAD":
        raw = _show(repo, "HEAD", rel)
        if raw is None:
            reasons.append(f"Zieldatei {rel} nicht in HEAD")
            return False, reasons, ctx
    else:
        raw = path.read_bytes()
    content = _text(raw)
    if content is None:
        reasons.append(f"Zieldatei {rel} ist kein UTF-8")
        return False, reasons, ctx
    if "\r" in content:
        reasons.append(f"Zieldatei {rel} enthält Windows-Zeilenenden (CR) — nicht unterstützt; "
                       "das Werkzeug schreibt sie nicht still um")
        return False, reasons, ctx
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
        # beide vollstaendig: Hashes, die sich erst spaet unterscheiden, bleiben unterscheidbar (W-2)
        reasons.append(f"context_hash veraltet: deklariert {declared} · ist {actual} — Ziel hat sich bewegt")

    # --- Zweite Ebene: hat sich die Datei seit base_sha bewegt?
    base = target.get("base_sha")
    if (repo / ".git").exists():
        if not base:
            reasons.append("base_sha fehlt — im Git-Repo Pflicht")
        elif not isinstance(base, str):
            reasons.append("base_sha ist kein Text")
        else:
            r = _git(repo, "diff", "--quiet", base, "HEAD", "--", rel)
            if r.returncode == 1:
                reasons.append(f"Datei seit base_sha {base[:8]} veraendert")
            elif r.returncode not in (0, 1):
                reasons.append("base_sha nicht aufloesbar: "
                               f"{r.stderr.decode('utf-8', 'replace').strip()[:80]}")
    elif base:
        reasons.append("base_sha angegeben, aber kein Git-Repo")

    # --- Operation trocken ausfuehren. Fehler der Operation sind Ablehnungsgruende.
    rendered: str | None = None
    op_ok = False
    if pay_ok:
        try:
            rendered = render_section(sec["section_text"], op, pay)
            op_ok = True
        except ValueError as e:
            reasons.append(str(e))

    # --- N-2: erklaerte Absicht gegen gemessene Wirkung.
    # Kein Schwellenwert. Grosse Loeschungen sind erlaubt — undeklarierte nicht.
    if op_ok and exp_ok:
        act_before = len(sec["section_text"].split("\n"))
        act_after = 0 if rendered is None else len(rendered.split("\n"))
        ctx["balance"] = (act_before, act_after)
        if (act_before, act_after) != (exp["before"], exp["after"]):
            reasons.append(
                f"Zeilenbilanz weicht von der Deklaration ab: erklaert "
                f"{exp['before']} -> {exp['after']}, gemessen {act_before} -> {act_after}")

    # --- Inhalt: Abschnitt nach dem Delta gegen den vorgegebenen Zieltext (Fassung S014).
    if ziel is not None:
        if not op_ok:
            reasons.append("Inhalt nicht prüfbar: die Operation scheitert (s. oben)")
        elif rendered is None:
            reasons.append("Inhalt nicht prüfbar: delete entfernt den Abschnitt")
        elif rendered != ziel:
            reasons.append(f"Inhalt weicht vom Zieltext ab: Zieltext {compute_section_hash(ziel)} · "
                           f"Ergebnis {compute_section_hash(rendered)}")
            ctx["details"] = _diff_zeilen(ziel, rendered)
        else:
            ctx["inhalt"] = compute_section_hash(ziel)

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

class _Parser(argparse.ArgumentParser):
    """Aufruffehler enden mit 3 (Bedienfehler), nicht mit argparse' 2 (= abgelehnt)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"BEDIENFEHLER: {message}", file=sys.stderr)
        sys.exit(EXIT_BEDIENFEHLER)


def _lade_delta(pfad: str):
    """(delta, None) oder (None, Grund). Fehlende Datei ist ein Bedienfehler (W-1),
    eine Datei, die kein JSON ist, ein abgelehntes Delta (1b-4)."""
    p = Path(pfad)
    if not p.is_file():
        raise Bedienfehler(f"Delta-Datei nicht gefunden: {pfad}")
    text = _text(p.read_bytes())
    if text is None:
        return None, "Delta-Datei ist kein UTF-8"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, f"kein gültiges JSON: {e}"


def _lade_zieltext(a) -> str | None:
    """None bei --ohne-inhalt; sonst der Zieltext ohne den einen Zeilenumbruch am Ende."""
    if getattr(a, "ohne_inhalt", False):
        return None
    if not getattr(a, "zieltext", None):
        raise Bedienfehler("Inhaltsprüfung verlangt: --zieltext DATEI angeben oder die Prüfung "
                           "ausdrücklich mit --ohne-inhalt abschalten")
    p = Path(a.zieltext)
    if not p.is_file():
        raise Bedienfehler(f"Zieltext-Datei nicht gefunden: {a.zieltext}")
    t = _text(p.read_bytes())
    if t is None:
        raise Bedienfehler("Zieltext-Datei ist kein UTF-8")
    if t.startswith("﻿"):
        raise Bedienfehler("Zieltext-Datei beginnt mit einer BOM")
    if "\r" in t:
        raise Bedienfehler("Zieltext-Datei enthält Windows-Zeilenenden (CR)")
    if t.endswith("\n"):
        t = t[:-1]
    if not _HEAD.match(t.split("\n", 1)[0]):
        raise Bedienfehler("Zieltext-Datei beginnt nicht mit einer Überschrift")
    return t


def _pruefe_ziel_ueberschrift(ziel: str | None, delta) -> None:
    if ziel is None or not isinstance(delta, dict) or not isinstance(delta.get("target"), dict):
        return
    heading = delta["target"].get("section_heading")
    erste = ziel.split("\n", 1)[0]
    if isinstance(heading, str) and erste.rstrip() != heading.rstrip():
        raise Bedienfehler(f"Zieltext beginnt nicht mit der Überschrift des Deltas: Zieltext „{erste}\", "
                           f"Delta „{heading}\" — falsche Zieltext-Datei oder geänderter Ankerwert im Delta")


def _vorbereiten(a, quelle: str = "arbeitsbaum"):
    """Gemeinsamer Weg fuer check, render und pr-body: Inhaltsentscheid, Zieltext, Delta, Pruefung."""
    ziel = _lade_zieltext(a)
    delta, fehler = _lade_delta(a.delta)
    if fehler:
        return None, False, [fehler], {"details": []}, ziel
    _pruefe_ziel_ueberschrift(ziel, delta)
    ok, reasons, ctx = check(delta, Path(a.repo), ziel, quelle)
    return delta, ok, reasons, ctx, ziel


def _melde_ablehnung(reasons: list[str], ctx: dict) -> int:
    for r in reasons:
        print("ABGELEHNT:", r, file=sys.stderr)
    for z in ctx.get("details", []):
        print("  " + z, file=sys.stderr)
    return EXIT_ABGELEHNT


def _inhalt_text(ctx: dict, ziel: str | None) -> str:
    return f"Inhalt gleich dem Zieltext {ctx['inhalt']}" if ziel is not None \
        else "ohne Inhaltsprüfung (--ohne-inhalt)"


def cmd_check(a) -> int:
    _, ok, reasons, ctx, ziel = _vorbereiten(a)
    if ok:
        print(f"ok — anwendbar · {_inhalt_text(ctx, ziel)}")
        return EXIT_OK
    return _melde_ablehnung(reasons, ctx)


def cmd_render(a) -> int:
    delta, ok, reasons, ctx, ziel = _vorbereiten(a)
    if not ok:
        return _melde_ablehnung(reasons, ctx)
    out = render(delta, ctx)
    if a.write:
        ctx["path"].write_bytes(out.encode("utf-8"))          # Bytes: kein Umwandeln der Zeilenenden
        before, after = ctx.get("balance", ("?", "?"))
        print(f"geschrieben: {ctx['path'].name} | Abschnitt {before} -> {after} Zeilen | "
              f"{_inhalt_text(ctx, ziel)}")
    else:
        sys.stdout.write(out)
    return EXIT_OK


def cmd_pr_body(a) -> int:
    # Liest die Zieldatei aus HEAD, nicht aus dem Arbeitsbaum: vor und nach render --write gleich (1b-9).
    delta, ok, reasons, ctx, ziel = _vorbereiten(a, quelle="HEAD")
    if not ok:
        return _melde_ablehnung(reasons, ctx)
    new_content = render(delta, ctx)
    new_sec = find_section(new_content, delta["target"]["section_heading"])
    new_hash = (compute_section_hash(new_sec["section_text"])
                if new_sec["status"] == "ok" else "— (Abschnitt entfernt)")
    b = len(ctx["section"]["section_text"].split("\n"))
    aft = "0" if new_sec["status"] != "ok" else len(new_sec["section_text"].split("\n"))
    meta = delta.get("meta") or {}
    inhalt = f"gleich dem Zieltext `{ctx['inhalt']}`" if ziel is not None else "nicht geprüft (--ohne-inhalt)"
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
| Inhalt | {inhalt} |
| Autor | {meta.get('author','—')} |

**Rationale.** {meta.get('rationale','—')}

Der Diff unten ist von git berechnet, nicht von diesem Werkzeug erzeugt.
Human Gate = Merge-Freigabe. Ohne Freigabe bleibt die Aenderung im Branch.""")
    return EXIT_OK


def _leseseite(corpus: list[str]) -> bool:
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

    files = [p for d in corpus for p in sorted(Path(d).glob("*.md"))]
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
    print("R-06 Leseseite")
    print(f"Korpus: {len(files)} Dateien, {tot} Ueberschriften")
    print(f"  identisch zur naiven Referenz : {agree}")
    print(f"  Fence-bedingt abweichend      : {fence_win}  (deltakit ist hier die sichere Seite)")
    print(f"  bewusst abgelehnt             : {refused}  (mehrdeutige Anker)")
    bad = 0
    for name, doc, head, pred in cases:
        good = pred(find_section(doc, head))
        bad += not good
        print(f"  [{'ok ' if good else 'FAIL'}] {name}")
    return bad == 0


def cmd_verify(a) -> int:
    """Nach-Audit: Ist im Repository genau das gelandet, was das Delta gesagt hat?
    Rechnet aus dem base_sha neu und vergleicht Bytes, wie sie im Repository stehen (1b-5)."""
    delta, fehler = _lade_delta(a.delta)
    if fehler:
        print(f"NICHT PRUEFBAR: {fehler}", file=sys.stderr)
        return EXIT_ABGELEHNT
    if not isinstance(delta, dict):
        print("NICHT PRUEFBAR: Delta ist kein JSON-Objekt", file=sys.stderr)
        return EXIT_ABGELEHNT
    repo = Path(a.repo)
    t = delta.get("target") if isinstance(delta.get("target"), dict) else {}
    doc, base, heading = t.get("document"), t.get("base_sha"), t.get("section_heading")
    if not (isinstance(base, str) and base):
        print("NICHT PRUEFBAR: base_sha fehlt im Delta", file=sys.stderr)
        return EXIT_ABGELEHNT
    if not (isinstance(doc, str) and doc and isinstance(heading, str) and heading):
        print("NICHT PRUEFBAR: target.document oder target.section_heading fehlt", file=sys.stderr)
        return EXIT_ABGELEHNT

    path, rel, why = resolve_doc(repo, doc)
    rel = rel or doc
    base_raw = _show(repo, base, rel)
    if base_raw is None:
        print(f"NICHT PRUEFBAR: {rel} existiert nicht in {base[:8]}", file=sys.stderr)
        return EXIT_ABGELEHNT
    base_content = _text(base_raw)
    if base_content is None:
        print(f"NICHT PRUEFBAR: {rel} in {base[:8]} ist kein UTF-8", file=sys.stderr)
        return EXIT_ABGELEHNT
    if "\r" in base_content:
        print(f"BEFUND: {rel} enthält in {base[:8]} Windows-Zeilenenden (CR). Dieses Werkzeug arbeitet "
              "nur mit LF; eine Anwendung hätte die Datei umgeschrieben.", file=sys.stderr)
        return EXIT_ABGELEHNT

    sec = find_section(base_content, heading)
    if sec["status"] != "ok":
        print(f"NICHT PRUEFBAR: Abschnitt im Basisstand nicht adressierbar "
              f"({sec['reason']})", file=sys.stderr)
        return EXIT_ABGELEHNT
    base_hash = compute_section_hash(sec["section_text"])
    if t.get("context_hash") and t["context_hash"] != base_hash:
        print(f"BEFUND: context_hash passt nicht zum Basisstand — das Delta wurde "
              f"gegen einen anderen Stand gebaut als gegen {base[:8]}", file=sys.stderr)
        return EXIT_ABGELEHNT

    try:
        rendered = render(delta, {"content": base_content, "section": sec})
    except ValueError as e:
        print(f"BEFUND: Das Delta laesst sich auf den Basisstand nicht anwenden: {e}", file=sys.stderr)
        return EXIT_ABGELEHNT
    actual_raw = _show(repo, a.head, rel)
    if actual_raw is None:
        print(f"BEFUND: {rel} existiert in {a.head} nicht mehr", file=sys.stderr)
        return EXIT_ABGELEHNT

    if rendered.encode("utf-8") == actual_raw:
        print(f"verifiziert — {rel} in {a.head} ist byte-identisch mit dem, "
              f"was {delta.get('delta_id')} aus {base[:8]} erzeugt")
        return EXIT_OK

    print(f"BEFUND: {rel} weicht ab von dem, was {delta.get('delta_id')} erzeugt haette.",
          file=sys.stderr)
    actual = actual_raw.decode("utf-8", "replace")
    if "\r" in actual:
        print(f"  {rel} enthält in {a.head} Windows-Zeilenenden (CR).", file=sys.stderr)
    d = list(difflib.unified_diff(rendered.split("\n"), actual.split("\n"),
                                  "LAUT DELTA", f"IM REPO ({a.head})", lineterm="", n=1))
    print("\n".join(d[: a.max_lines]), file=sys.stderr)
    if len(d) > a.max_lines:
        print(f"… {len(d) - a.max_lines} weitere Zeilen", file=sys.stderr)
    return EXIT_ABGELEHNT


def cmd_audit(a) -> int:
    """Gate-Abdeckung messen. Verhindert keinen Bypass — macht ihn sichtbar.
    Konvention: die delta_id steht in der Commit-Nachricht."""
    repo = Path(a.repo)
    ids: dict[str, str] = {}
    hinweise: list[str] = []
    dd = Path(a.deltas)
    for p in sorted(dd.rglob("*.json")) if dd.is_dir() else []:
        text = _text(p.read_bytes())
        try:
            if text is None:
                raise ValueError("kein UTF-8")
            d = json.loads(text)
        except ValueError:                      # JSONDecodeError ist ein ValueError
            hinweise.append(f"übersprungen (kein gültiges JSON): {p}")
            continue
        if not isinstance(d, dict):
            hinweise.append(f"übersprungen (kein JSON-Objekt): {p}")
            continue
        did = d.get("delta_id")
        if isinstance(did, str) and did:
            tgt = d.get("target")
            ids[did] = tgt.get("document", "?") if isinstance(tgt, dict) else "?"

    rng = f"{a.start}..{a.head}" if a.start else a.head
    code, out, err = _git_text(repo, "log", "--format=%H%x1f%s", "--reverse", rng, "--", a.artefacts)
    if code != 0:
        print("git log fehlgeschlagen:", err.strip()[:160], file=sys.stderr)
        return EXIT_BEDIENFEHLER
    rows = [l.split("\x1f", 1) for l in out.splitlines() if l.strip()]

    covered, naked = [], []
    for sha, subject in rows:
        hit = next((i for i in ids if i in subject), None)
        files = _git_text(repo, "show", "--name-only", "--format=", sha)[1].split()
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
    for h in hinweise:
        print("Hinweis:", h)
    if naked:
        print("\nBefund: Commits auf Artefakten ohne Delta-Bezug im Betreff.")
    return EXIT_ABGELEHNT if naked else EXIT_OK


def cmd_hash(a) -> int:
    """Liefert das Anker-Paket fuer den Delta-Autor: Abschnittstext, Hash, base_sha."""
    repo = Path(a.repo)
    path, rel, why = resolve_doc(repo, a.document)
    if path is None:
        print(why, file=sys.stderr)
        return EXIT_ABGELEHNT
    content = _text(path.read_bytes())
    if content is None:
        print(f"{rel} ist kein UTF-8", file=sys.stderr)
        return EXIT_ABGELEHNT
    if "\r" in content:
        print(f"{rel} enthält Windows-Zeilenenden (CR) — nicht unterstützt", file=sys.stderr)
        return EXIT_ABGELEHNT
    sec = find_section(content, a.heading)
    if sec["status"] != "ok":
        print(f"Abschnitt nicht adressierbar: {sec['reason']}", file=sys.stderr)
        return EXIT_ABGELEHNT
    body = sec["section_text"].split("\n")
    _, head, _ = _git_text(repo, "rev-parse", "HEAD")
    print(f"document      : {Path(rel).name}")
    print(f"pfad_im_repo  : {rel}")
    print(f"section_heading: {a.heading}")
    print(f"base_sha      : {head.strip() or '— (kein Git-Repo)'}")
    print(f"context_hash  : {compute_section_hash(sec['section_text'])}")
    print(f"expected_lines.before: {len(body)}")
    print("--- ABSCHNITT, WORTGETREU (Ueberschrift + Body) ---")
    print(sec["section_text"])
    print("--- ENDE ABSCHNITT ---")
    return EXIT_OK


# ------------------------------------------------------------------ selftest

def _dateikopf_subkommandos() -> list[str]:
    teil = (__doc__ or "").split("Subkommandos:", 1)[-1].split("\n\n", 1)[0]
    return [z.split()[0] for z in teil.strip("\n").split("\n") if z.strip()]


def _argparse_subkommandos() -> list[str]:
    for act in _parser()._actions:
        if isinstance(act, argparse._SubParsersAction):
            return list(act.choices)
    return []


def _klon(repo: Path, stand: str, ziel: Path) -> None:
    """Wegwerf-Kopie des Repositorys am festen Stand. Teilt die Objekte, aendert den Klon nicht."""
    r = subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(ziel)],
                       capture_output=True)
    if r.returncode != 0:
        raise Bedienfehler(f"Kopie von {repo} fehlgeschlagen: {r.stderr.decode('utf-8', 'replace').strip()[:160]}")
    r = subprocess.run(["git", "-C", str(ziel), "-c", "advice.detachedHead=false", "checkout", "--quiet",
                        "--detach", stand], capture_output=True)
    if r.returncode != 0:
        raise Bedienfehler(f"Stand {stand} nicht auszucheckbar: {r.stderr.decode('utf-8', 'replace').strip()[:160]}")


def _passt(r: subprocess.CompletedProcess, erw: dict) -> tuple[bool, str]:
    text = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    fehlt = [s for s in erw.get("enthaelt", []) if s not in text]
    zuviel = [s for s in erw.get("enthaelt_nicht", []) if s in text]
    ok = r.returncode == erw["exit"] and not fehlt and not zuviel
    teile = [f"exit {r.returncode} (erwartet {erw['exit']})"]
    if fehlt:
        teile.append("fehlt: " + " | ".join(repr(s) for s in fehlt))
    if zuviel:
        teile.append("darf nicht vorkommen: " + " | ".join(repr(s) for s in zuviel))
    return ok, " · ".join(teile)


def _laufe_kontrollfaelle(kf: dict, repo: Path, kf_pfad: Path) -> bool:
    tool = Path(__file__).resolve()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_PAGER="cat")
    print()
    print(f"Kontrollfälle: {kf_pfad} · sha256 {hashlib.sha256(kf_pfad.read_bytes()).hexdigest()}")
    print(f"Werkzeug: {tool} · sha256 {hashlib.sha256(tool.read_bytes()).hexdigest()} · Fassung {FASSUNG}")
    print(f"Klon: {repo}")
    for stand in kf["staende"]:
        r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{stand}^{{commit}}"], capture_output=True)
        if r.returncode != 0:
            raise Bedienfehler(f"Stand {stand} fehlt im Klon {repo} — erst 'git fetch --all' ausführen")
    tmp = Path(tempfile.mkdtemp(prefix="deltakit-selftest-"))
    try:
        ablage = tmp / "faelle"
        ablage.mkdir()
        deltas, ziele = {}, {}
        for name, d in kf["deltas"].items():
            p = ablage / f"{name}.json"
            p.write_bytes((json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            deltas[name] = p
        for name, z in kf["zieltexte"].items():
            t = z["text"] if "text" in z else kf["zieltexte"][z["basis"]]["text"]
            if "erste_zeile" in z:
                t = z["erste_zeile"] + "\n" + t.split("\n", 1)[1]
            if z.get("crlf"):
                t = t.replace("\n", "\r\n")
            p = ablage / f"ziel_{name}.md"
            p.write_bytes((t + ("\r\n" if z.get("crlf") else "\n")).encode("utf-8"))
            ziele[name] = p

        def arg(x: str, klon: Path) -> str:
            if x.startswith("@delta:"):
                return str(deltas[x[7:]])
            if x.startswith("@ziel:"):
                return str(ziele[x[6:]])
            if x == "@fehlt":
                return str(tmp / "fehlt" / "fehlt.json")
            if x.startswith("@abs:"):
                return str(klon / x[5:])
            return x

        def lauf(befehl: list[str], klon: Path) -> subprocess.CompletedProcess:
            return subprocess.run([sys.executable, str(tool)] + [arg(x, klon) for x in befehl],
                                  cwd=str(klon), env=env, capture_output=True)

        gesamt, gut = 0, 0
        for n, fall in enumerate(kf["faelle"]):
            fid, typ = fall["id"], fall.get("typ", "aufruf")
            if typ == "verweis":
                print(f"  [—  ] {fid}  {fall['beschreibung']}")
                continue
            gesamt += 1
            if typ == "intern":
                a_kopf, a_arg = _dateikopf_subkommandos(), _argparse_subkommandos()
                ok = sorted(a_kopf) == sorted(a_arg) and len(a_arg) == fall["anzahl"]
                info = f"Dateikopf {len(a_kopf)} · argparse {len(a_arg)}"
            else:
                klon = tmp / f"k{n:02d}"
                if typ == "synthetisch":
                    _synthetisch_crlf(fall, klon, repo, deltas)
                else:
                    _klon(repo, fall["stand"], klon)
                for v in fall.get("vorbereitung", []):
                    ziel_p = klon / v["pfad"]
                    if v["aktion"] == "crlf":
                        ziel_p.write_bytes(ziel_p.read_bytes().replace(b"\n", b"\r\n"))
                    elif v["aktion"] == "schreibe":
                        ziel_p.write_bytes(v["inhalt"].encode("utf-8"))
                schritte = fall["schritte"] if typ == "folge" else [fall]
                ergebnisse, ok, infos = [], True, []
                for s in schritte:
                    r = lauf(s["befehl"], klon)
                    ergebnisse.append(r)
                    o, i = _passt(r, s["erwartung"])
                    ok &= o
                    infos.append(i)
                for i, j in fall.get("gleich", []):
                    same = ergebnisse[i].stdout == ergebnisse[j].stdout
                    ok &= same
                    infos.append(f"Ausgabe Schritt {i + 1} {'=' if same else '≠'} Schritt {j + 1}")
                info = " ; ".join(infos)
            gut += ok
            print(f"  [{'ok ' if ok else 'ABW'}] {fid}  {fall['beschreibung']} — {info}")
        print(f"Kontrollfälle: {gesamt} · wie erwartet: {gut}")
        return gut == gesamt
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _synthetisch_crlf(fall: dict, ziel: Path, repo: Path, deltas: dict) -> None:
    """W-10: Wegwerf-Repository, in dem die Zieldatei mit CRLF lag und dann so umgeschrieben wurde,
    wie es die Fassung vor S014 tat (alles LF, Delta angewendet). verify muss das melden."""
    g = ["git", "-C", str(ziel), "-c", "user.name=selftest", "-c", "user.email=selftest@invalid",
         "-c", "commit.gpgsign=false"]
    ziel.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(ziel)], check=True, capture_output=True)
    quelle = subprocess.run(["git", "-C", str(repo), "show", f"{fall['stand']}:{fall['datei']}"],
                            capture_output=True, check=True).stdout
    lf = quelle.decode("utf-8")
    datei = ziel / fall["datei"]
    datei.parent.mkdir(parents=True, exist_ok=True)
    datei.write_bytes(lf.replace("\n", "\r\n").encode("utf-8"))
    subprocess.run(g + ["add", "-A"], check=True, capture_output=True)
    subprocess.run(g + ["commit", "--quiet", "-m", "Basisstand mit CRLF"], check=True, capture_output=True)
    base = subprocess.run(["git", "-C", str(ziel), "rev-parse", "HEAD"], capture_output=True,
                          check=True).stdout.decode().strip()
    d = json.loads(deltas[fall["delta"]].read_bytes().decode("utf-8"))
    sec = find_section(lf, d["target"]["section_heading"])
    alt = render(d, {"content": lf, "section": sec})
    datei.write_bytes(alt.encode("utf-8"))
    subprocess.run(g + ["add", "-A"], check=True, capture_output=True)
    subprocess.run(g + ["commit", "--quiet", "-m", "Anwendung, Datei auf LF umgeschrieben"], check=True,
                   capture_output=True)
    d["target"]["base_sha"] = base
    (ziel / "delta.json").write_bytes((json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def cmd_selftest(a) -> int:
    gut = _leseseite(a.corpus)
    if a.nur_leseseite:
        return EXIT_OK if gut else EXIT_ABGELEHNT
    pfad = Path(a.kontrollfaelle) if a.kontrollfaelle else Path(__file__).resolve().parent / "kontrollfaelle.json"
    if not pfad.is_file():
        raise Bedienfehler(f"Kontrollfälle nicht gefunden: {pfad}")
    kf = json.loads(pfad.read_bytes().decode("utf-8"))
    gut = _laufe_kontrollfaelle(kf, Path(a.repo).resolve(), pfad) and gut
    return EXIT_OK if gut else EXIT_ABGELEHNT


def _parser() -> _Parser:
    ap = _Parser(prog="deltakit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("check", cmd_check), ("render", cmd_render), ("pr-body", cmd_pr_body)):
        p = sub.add_parser(name)
        p.add_argument("delta")
        p.add_argument("--repo", default=".")
        g = p.add_mutually_exclusive_group()
        g.add_argument("--zieltext", default=None)
        g.add_argument("--ohne-inhalt", action="store_true")
        if name == "render":
            p.add_argument("--write", action="store_true")
        p.set_defaults(fn=fn)
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

    p = sub.add_parser("selftest")
    p.add_argument("--corpus", nargs="+", default=["."])
    p.add_argument("--kontrollfaelle", default=None)
    p.add_argument("--repo", default=".")
    p.add_argument("--nur-leseseite", action="store_true")
    p.set_defaults(fn=cmd_selftest)
    return ap


def main(argv: list[str] | None = None) -> int:
    a = _parser().parse_args(argv)
    try:
        return a.fn(a)
    except Bedienfehler as e:
        print(f"BEDIENFEHLER: {e}", file=sys.stderr)
        return EXIT_BEDIENFEHLER
    except Exception as e:  # noqa: BLE001 — nie exit 1; ein interner Fehler laesst nichts durch
        print(f"INTERNER FEHLER ({type(e).__name__}): {e}", file=sys.stderr)
        return EXIT_BEDIENFEHLER


if __name__ == "__main__":
    sys.exit(main())
