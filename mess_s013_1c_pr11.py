#!/usr/bin/env python3
"""mess_s013_1c_pr11.py — PBP-S013, Schritt 1c: Pull Request #11 vor dem Merge messen.

Nur lesend, frischer Klon. Schreibt messung_S013_1c_pr11.txt. Sollwerte aus: Handgriffe 2 und 3
der Antwort zu 1b (erwartete Dateien), messung_S013_1b.txt (Stand nach 1a), Meldung und
Screenshot des Owners zu PR #11 (30.09.), sha256 der in diesem Chat gelieferten Dateien.
"""
import datetime
import hashlib
import os
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True

JETZT = datetime.datetime.now(datetime.timezone.utc)
KLON = pathlib.Path(f"/home/claude/andreasborchmann/delta-s013-1c-{JETZT.strftime('%Y%m%dT%H%M%SZ')}")
URL = "https://github.com/andreasborchmann/delta"
SCR = pathlib.Path("/tmp/claude-0/-home-claude/d4b90973-e897-5562-a754-c757c3acfa92/scratchpad/s013/1c")
OUT = pathlib.Path("/home/claude/s013/messung_S013_1c_pr11.txt")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_PAGER="cat")

START = "4efdce9eec95ea82bd57e485e15e67aa608c89a0"
BRANCH = "delta/20260919-004"
BRANCH_SHA = "db543e332474bb4ccd24ad0ee9e231218e42e3e1"
PR = "11"
PR_HEAD = "8fb07d8f89cfce9087b9cd960c6b21f542845a51"
Q_1B = "messung_S013_1b.txt"
Q_OWN = "Meldung und Screenshot des Owners zu PR #11, 30.09."
Q_HG = "Antwort zu 1b, Handgriffe 2 und 3"
# In diesem Chat gelieferte Dateien und ihre sha256 (gemessen vor der Auslieferung):
GELIEFERT = {
    "VERSAND_Lauf-3.txt": "39b8faec2da13898ca855e087368d672af055d939e55bc6bb453bdd308e3663e",
    "HANDBUCH_Lauf-3-Transportachse.md": "f14a3427bb2ff32859df6f840cac0f4e6ca79ea21a56fa02a43ff50d61c26297",
    "messung_S013_schritt0.txt": "36396edc516a63c7198891c1c8a220e96d358645fd6d2cc80f9e89ef8a4e869e",
    "mess_s013_schritt0.py": "f8cd2e49eea8eeb0efbfdc838de4290789e1eacfdd86301f9ac4a5b1b9a06d08",
    "messung_S013_1b.txt": "e6bce8db5ab7ae6ec7857edfd0f1f462bbef4ff8b4599a86c332633a0a92c271",
    "mess_s013_1b.py": "4fb150e66df85244eec11cbef7d5a77b876469d787741529f8733907aec19007",
}
ERWARTET = ["HANDBUCH_Lauf-3-Transportachse.md", "VERSAND_Lauf-3.txt"]

L, CHECKS = [], []


def w(s=""):
    L.append(s)


def sec(t):
    w(); w("=" * 96); w(t); w("=" * 96)


def pruef(cid, text, soll, ist, ok, quelle):
    CHECKS.append((cid, bool(ok)))
    w(f"{cid}  {text}")
    w(f"       Soll: {soll}")
    w(f"             [Quelle: {quelle}]")
    w(f"       Ist:  {ist}")
    w(f"       Ergebnis: {'✓' if ok else '✗ ABWEICHUNG'}")


def run(cmd):
    return subprocess.run(cmd, cwd=str(KLON), env=ENV, capture_output=True)


def zeige(cmdtext, r, maxzeilen=None):
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    w(f"$ {cmdtext}")
    txt = out + (("[stderr]\n" + err) if err else "")
    z = txt.rstrip("\n").split("\n") if txt else []
    if maxzeilen is not None and len(z) > maxzeilen:
        z = z[:maxzeilen] + [f"… {len(z) - maxzeilen} weitere Zeilen, gekürzt im Protokoll"]
    for s in z:
        w("  " + s)
    w(f"  exit {r.returncode}")
    return out


SCR.mkdir(parents=True, exist_ok=True)
jetzt = JETZT.strftime("%Y-%m-%dT%H:%M:%SZ")
rk = subprocess.run(["git", "clone", URL, str(KLON)], env=dict(ENV, GIT_LFS_SKIP_SMUDGE="1"), capture_output=True)
if rk.returncode != 0:
    sys.exit("Klon fehlgeschlagen: " + rk.stderr.decode("utf-8", "replace"))
w("messung_S013_1c_pr11.txt — PBP-S013, Schritt 1c: Pull Request #11 vor dem Merge gemessen")
w(f"Erstellt: {jetzt} (UTC) · Prüfdatum für Quellenangaben: {jetzt[:10]}")
w("Rolle: Analyst (P1) · Steuerungs-Chat · frischer Klon, nur lesend")
w(f"$ git clone {URL} {KLON}")
w("  " + rk.stderr.decode("utf-8", "replace").strip())
w(f"  exit {rk.returncode}")
w("Anlass: Der Owner meldet, dass „Files changed\" in PR #11 zwei andere Dateien zeigt als erwartet.")

sec("§1 — Stand auf dem Server")
r = run(["git", "ls-remote", "origin"])
out = zeige("git ls-remote origin", r)
refs = {}
for z in out.splitlines():
    if "\t" in z:
        s_, ref = z.split("\t", 1)
        refs[ref] = s_
pruef("1C-01", "main unverändert bei <START> — nichts gemergt", START, refs.get("refs/heads/main", "—"),
      refs.get("refs/heads/main") == START, f"{Q_1B} 1B-01; {Q_OWN} (PR #11 offen)")
pruef("1C-02", f"Pull Request #{PR} zeigt auf den gemeldeten Commit", PR_HEAD, refs.get(f"refs/pull/{PR}/head", "—"),
      refs.get(f"refs/pull/{PR}/head") == PR_HEAD, Q_OWN)
branches = sorted(k[len("refs/heads/"):] for k in refs if k.startswith("refs/heads/"))
pruef("1C-03", "Branches auf dem Server", "andreasborchmann-patch-2 (offener PR), delta/20260919-004, main",
      ", ".join(branches),
      branches == ["andreasborchmann-patch-2", BRANCH, "main"] and refs.get(f"refs/heads/{BRANCH}") == BRANCH_SHA
      and refs.get("refs/heads/andreasborchmann-patch-2") == PR_HEAD,
      f"{Q_OWN} („from andreasborchmann-patch-2\"); {Q_1B} 1B-02")

sec(f"§2 — Der Commit in Pull Request #{PR}")
r = run(["git", "fetch", "origin", f"+refs/pull/{PR}/head:refs/remotes/origin/pr/{PR}"])
zeige(f"git fetch origin +refs/pull/{PR}/head:refs/remotes/origin/pr/{PR}", r)
r = run(["git", "log", "-1", "--format=%H%n%P%n%s%n%an%n%aI", f"refs/remotes/origin/pr/{PR}"])
o = zeige(f"git log -1 --format='%H%n%P%n%s%n%an%n%aI' refs/remotes/origin/pr/{PR}", r).split("\n")
pruef("1C-04", "Upload-Commit auf <START> angelegt, ein Elternteil", START[:7],
      (o[1][:7] if len(o) > 1 else "—"), len(o) > 1 and o[1] == START, "Antwort zu 1b, Handgriff 2")
r = run(["git", "diff", "--name-status", START, f"refs/remotes/origin/pr/{PR}"])
ns = zeige(f"git diff --name-status {START[:7]} refs/remotes/origin/pr/{PR}", r).strip()
paare = sorted((z.split("\t", 1)[1], z.split("\t", 1)[0]) for z in ns.splitlines() if "\t" in z)
dateien = [p[0] for p in paare]
arten = [p[1] for p in paare]
pruef("1C-05", "Pull Request bringt genau die zwei gefüllten Dateien",
      "A  " + " · A  ".join(ERWARTET), " · ".join(f"{a}  {d}" for a, d in zip(arten, dateien)) or "—",
      dateien == ERWARTET and arten == ["A", "A"], Q_HG)
pruef("1C-06", "nichts unter artefakte/, alles im Wurzelverzeichnis", "keine Datei unter artefakte/ oder in einem Ordner",
      "alle im Wurzelverzeichnis" if all("/" not in d for d in dateien) else "Ordner betroffen",
      bool(dateien) and all("/" not in d for d in dateien), "HANDBUCH R2; Antwort zu 1b, Handgriff 3")

sec("§3 — Bytes der hochgeladenen Dateien gegen die gelieferten")
w("Zusatz: Weil die hochgeladenen Dateien ebenfalls aus diesem Chat stammen, zeigt der Vergleich, ob der")
w("Weg Chat → Rechner → GitHub die Bytes verändert (die Frage hinter Entscheidung 2).")
for d in dateien:
    r = run(["git", "show", f"refs/remotes/origin/pr/{PR}:{d}"])
    f = SCR / d
    w(f"$ git show refs/remotes/origin/pr/{PR}:{d} > {f}")
    w(f"  exit {r.returncode}")
    if r.returncode != 0:
        continue
    f.write_bytes(r.stdout)
    ist = hashlib.sha256(r.stdout).hexdigest()
    zeige(f"sha256sum {f}", subprocess.run(["sha256sum", str(f)], capture_output=True))
    soll = GELIEFERT.get(d)
    pruef(f"1C-{7 + dateien.index(d):02d}", f"{d}: bytegleich mit der in diesem Chat gelieferten Datei",
          soll or "— (keine Datei dieses Namens geliefert)", ist, soll is not None and ist == soll,
          "sha256 der gelieferten Dateien, gemessen vor der Auslieferung (Antworten zu Schritt 0 und 1b)")

# ---------------------------------------------------------------- §3a unerwarteter Branch
UNERW = sorted(set(branches) - {"andreasborchmann-patch-2", BRANCH, "main"})
sec("§3a — Branches, die in 1C-03 nicht erwartet waren (Befund, ohne Sollwert)")
if not UNERW:
    w("keine")
for b_ in UNERW:
    ref = f"refs/remotes/origin/{b_}"
    r = run(["git", "log", "-3", "--format=%H%n  Eltern: %P%n  Betreff: %s%n  Autor-Zeit: %aI", ref])
    zeige(f"git log -3 --format=… {ref}", r)
    r = run(["git", "merge-base", "--is-ancestor", START, ref])
    zeige(f"git merge-base --is-ancestor {START[:7]} {ref}", r)
    r = run(["git", "diff", "--name-status", START, ref])
    ns_u = zeige(f"git diff --name-status {START[:7]} {ref}", r).strip()
    for z in ns_u.splitlines():
        if "\t" not in z:
            continue
        art, d = z.split("\t", 1)
        if art == "D":
            continue
        rr = run(["git", "show", f"{ref}:{d}"])
        w(f"$ git show {ref}:{d} > {SCR / ('u_' + d.replace('/', '_'))}")
        w(f"  exit {rr.returncode}")
        if rr.returncode != 0:
            continue
        (SCR / ("u_" + d.replace("/", "_"))).write_bytes(rr.stdout)
        ist = hashlib.sha256(rr.stdout).hexdigest()
        soll = GELIEFERT.get(pathlib.Path(d).name)
        gleich = "bytegleich mit der gelieferten Datei" if soll == ist else (
            "NICHT bytegleich mit der gelieferten Datei" if soll else "kein gelieferter Name")
        w(f"  {d}: {len(rr.stdout)} Bytes · sha256 {ist} · {gleich}")
    r = run(["git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/remotes/origin/pr"])
    zeige("git for-each-ref refs/remotes/origin/pr", r)
    w(f"Ein Pull Request mit diesem Branch als Head ist unter refs/pull/*/head "
      f"{'vorhanden' if any(v == refs.get('refs/heads/' + b_) and k.startswith('refs/pull/') for k, v in refs.items()) else 'nicht vorhanden'}.")

sec("§4 — Klon nach der Messung")
r = run(["git", "status", "--porcelain", "--ignored"])
out = zeige("git status --porcelain --ignored", r)
pruef("1C-09", "Arbeitsverzeichnis des Klons unverändert", "leer", "leer" if not out.strip() else out.strip(),
      r.returncode == 0 and not out.strip(), "Übergabe S012→S013 §7, M-11")

sec("Schluss")
n_ok = sum(ok for _, ok in CHECKS)
abw = [c for c, ok in CHECKS if not ok]
w(f"Prüfungen: {n_ok} von {len(CHECKS)} ohne Abweichung. Abweichungen: {', '.join(abw) if abw else 'keine'}")
w("Befunde: 1C-05 (andere Dateien im Pull Request als erwartet); 1C-03 (Branch, der nicht erwartet war,")
w("vermessen in §3a). Nicht gemergt — main steht bei <START> (1C-01).")
w()
w("*messung_S013_1c_pr11.txt | Messprotokoll Schritt 1c, PR #11 | PBP-S013 | Owner: Co-Creator*")
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{n_ok}/{len(CHECKS)} ok · Abweichungen: {abw or 'keine'}")
print(f"geschrieben: {OUT}")
