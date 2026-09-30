#!/usr/bin/env python3
"""mess_s013_schritt0.py — PBP-S013, Schritt 0: Stand messen, bevor gehandelt wird.

Nur lesend gegenüber dem Repository. Schreibt messung_S013_schritt0.txt.
Sollwerte stammen nur aus Quellen, die in dieser Session geladen sind:
Übergabe S012→S013 (Wissensbasis), Instanz v0.10 (Wissensbasis), die vier Anhänge.
"""
import datetime
import hashlib
import importlib.util
import os
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True

JETZT = datetime.datetime.now(datetime.timezone.utc)
KLON = pathlib.Path(f"/home/claude/andreasborchmann/delta-s013-{JETZT.strftime('%Y%m%dT%H%M%SZ')}")
URL = "https://github.com/andreasborchmann/delta"
TOOL = "engine/deltakit.py"
ANH = pathlib.Path("/mnt/user-data/uploads")
ANH2 = pathlib.Path("/root/.claude/uploads/d4b90973-e897-5562-a754-c757c3acfa92")
SCR = pathlib.Path("/tmp/claude-0/-home-claude/d4b90973-e897-5562-a754-c757c3acfa92/scratchpad/s013")
OUT = pathlib.Path("/home/claude/s013/messung_S013_schritt0.txt")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_PAGER="cat")

Q_UE1 = "Übergabe S012→S013 §1, Schritt 0"
Q_UE2 = "Übergabe S012→S013 §2"
Q_UE4 = "Übergabe S012→S013 §4"
Q_UE1B = "Übergabe S012→S013 §1, Schritt 1b"
Q_INST23 = "Instanz v0.10 §2.3"

MAIN = "6bd45a3928a520acee74e7d091bc839fb6585efa"
BRANCH = "delta/20260919-004"
BRANCH_SHA = "db543e332474bb4ccd24ad0ee9e231218e42e3e1"
START2 = "76b33f9d82ce8c0b56e510abd1a95ba1d21b2817"
TOOL_SHA = "931cd7eb12dd46d413b8cc23cf5eb645707abfa4d52fcf8bc65824aff6d73b3c"
CTX_KURZ = ("f34a74a4", "8de8f1")
ZIEL = "artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md"
H21 = "### 2.1 Schicht-Architektur"
ANH_SOLL = {  # sha256, Zeichen, Zeilenumbrüche, "ohne Zeilenumbruch am Ende" gefordert
    "AUSWERTUNG_Lauf3.md": ("865eaf5e29993ae6217870b2f1c17db8bdc07d85af893a6b7c036482e777ed70", 5548, 103, False),
    "VERSAND_Lauf-3.txt": ("4f9d68e79eae6856ed09f443b70cf4eca1f8950ca12a08b298b3bb0d6eac392e", 5680, 128, False),
    "HANDBUCH_Lauf-3-Transportachse.md": ("a71f0c3072bbbf09c6fcf146d03325428d5d5363bd03a82639cb14bb76011eed", 13221, 243, False),
    "CCR_DELTA_FORCE-PBP-S012.json": ("d1628bf347e78f3980199aecb7a7e703af6c3cb1e1c578f8a521b7e9b197713b", 12575, 209, True),
}
PLATZHALTER_SOLL = {"START", "START7", "PR_START", "JJJJMMTT", "SHA_AUSWERTUNG", "SHA_VERSAND"}
KB_SOLL = {
    "ULTRA_PROTOCOL_SYS_PBP_1_2.md", "ULTRA_PROTOCOL_SYS_CCR_1_4.md",
    "ULTRA_PROTOCOL_SYS_INIT_RUNTIME_1_0.md", "ULTRA_PROTOCOL_SYS_COMMIT_RUNTIME_1_0.md",
    "ULTRA_DATA_SYS_DELTA-FORCE_0_10.md", "ULTRA_REF_SYS_REGISTRY_RUNTIME_1_0.md",
    "UEBERGABE_PBP-S012_nach_S013.md",
}
# Abschrift der Werkzeugausgabe Projects/project_info in diesem Chat (30.09., vor der Messung):
KB_IST = [
    "ULTRA_DATA_SYS_DELTA-FORCE_0_10.md", "UEBERGABE_PBP-S012_nach_S013.md",
    "ULTRA_PROTOCOL_SYS_COMMIT_RUNTIME_1_0.md", "ULTRA_REF_SYS_REGISTRY_RUNTIME_1_0.md",
    "ULTRA_PROTOCOL_SYS_INIT_RUNTIME_1_0.md", "ULTRA_PROTOCOL_SYS_PBP_1_2.md",
    "ULTRA_PROTOCOL_SYS_CCR_1_4.md",
]

L: list[str] = []
CHECKS: list[tuple[str, bool]] = []
KONTR: list[tuple[str, bool]] = []


def w(s: str = "") -> None:
    L.append(s)


def sec(titel: str) -> None:
    w()
    w("=" * 96)
    w(titel)
    w("=" * 96)


def pruef(cid: str, text: str, soll: str, ist: str, ok: bool, quelle: str) -> None:
    CHECKS.append((cid, ok))
    w(f"{cid}  {text}")
    w(f"       Soll: {soll}")
    w(f"             [Quelle: {quelle}]")
    w(f"       Ist:  {ist}")
    w(f"       Ergebnis: {'✓' if ok else '✗ ABWEICHUNG'}")


def kontrolle(kid: str, text: str, erwartung: str, ist: str, ok: bool) -> None:
    KONTR.append((kid, ok))
    w(f"{kid}  Kontrollfall: {text}")
    w(f"       Erwartung: {erwartung}")
    w(f"       Ist:       {ist}")
    w(f"       Ergebnis:  {'wie erwartet' if ok else '✗ NICHT WIE ERWARTET — Prüfung falsch gebaut?'}")


def run(cmd, cwd=KLON):
    return subprocess.run(cmd, cwd=str(cwd), env=ENV, capture_output=True)


def zeige(cmdtext: str, r, maxzeilen: int | None = None) -> str:
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    w(f"$ {cmdtext}")
    txt = out + (("[stderr]\n" + err) if err else "")
    zeilen = txt.rstrip("\n").split("\n") if txt else []
    if maxzeilen is not None and len(zeilen) > maxzeilen:
        for z in zeilen[:maxzeilen]:
            w("  " + z)
        w(f"  … {len(zeilen) - maxzeilen} weitere Zeilen, gekürzt im Protokoll (nicht in der Messung)")
    else:
        for z in zeilen:
            w("  " + z)
    w(f"  exit {r.returncode}")
    return out


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def kurz_passt(full: str) -> bool:
    h = full.split(":", 1)[-1]
    return h.startswith(CTX_KURZ[0]) and h.endswith(CTX_KURZ[1])


# ---------------------------------------------------------------- Kopf
jetzt = JETZT.strftime("%Y-%m-%dT%H:%M:%SZ")
rk = subprocess.run(["git", "clone", URL, str(KLON)], env=dict(ENV, GIT_LFS_SKIP_SMUDGE="1"),
                    capture_output=True)
if rk.returncode != 0:
    sys.exit("Klon fehlgeschlagen: " + rk.stderr.decode("utf-8", "replace"))
w("messung_S013_schritt0.txt — PBP-S013, Schritt 0: Stand messen, bevor gehandelt wird")
w(f"Erstellt: {jetzt} (UTC) · Prüfdatum für Quellenangaben: {jetzt[:10]}")
w("Rolle: Analyst (P1) · Steuerungs-Chat · frischer Klon, nur lesend")
w(f"$ git clone {URL} {KLON}")
w("  " + rk.stderr.decode("utf-8", "replace").strip())
w(f"  exit {rk.returncode}")
w(f"Klon: {KLON} · origin = {run(['git','remote','get-url','origin']).stdout.decode().strip()}")
w("Zugang: anonymer Lesezugriff über den Git-Proxy der Sitzung (keine Zugangsdaten für das")
w("        Repository angehängt; add_repo meldete: öffentliches Repository, anonyme Reads).")
w(f"Werkzeuge: {run(['git','--version']).stdout.decode().strip()} · Python {sys.version.split()[0]}")
w("Sollwerte nur aus geladenen Quellen: Übergabe S012→S013 und Instanz v0.10 (Wissensbasis),")
w("die vier Anhänge. Prüfweg für Repository-Dateien zweistufig: erst in eine Datei, Exit-Code")
w("prüfen, dann sha256 (Übergabe §5, „Prüfweg ohne Pipe\").")
w("Kontrollfälle (K-xx) prüfen die eigene Prüfung; sie zählen nicht zu den Prüfungen (S0-xx).")

# ---------------------------------------------------------------- §1 Server
sec("§1 — Stand auf dem Server (git ls-remote)")
r = run(["git", "ls-remote", "origin"])
out = zeige("git ls-remote origin", r)
refs = {}
for z in out.splitlines():
    if "\t" in z:
        s, ref = z.split("\t", 1)
        refs[ref] = s
r2 = run(["git", "ls-remote", "--symref", "origin", "HEAD"])
out2 = zeige("git ls-remote --symref origin HEAD", r2)
pruef("S0-01", "main auf dem Server", MAIN, refs.get("refs/heads/main", "—"),
      refs.get("refs/heads/main") == MAIN, Q_UE4)
pruef("S0-02", f"Branch {BRANCH} auf dem Server", BRANCH_SHA, refs.get(f"refs/heads/{BRANCH}", "—"),
      refs.get(f"refs/heads/{BRANCH}") == BRANCH_SHA, Q_UE4)
pruef("S0-03", "Pull Request #9 zeigt auf denselben Commit", BRANCH_SHA, refs.get("refs/pull/9/head", "—"),
      refs.get("refs/pull/9/head") == BRANCH_SHA, f"{Q_INST23}, [S012] Stand 2026-09-29")
branches = sorted(k[len("refs/heads/"):] for k in refs if k.startswith("refs/heads/"))
pruef("S0-04", "Branches auf dem Server", "main und delta/20260919-004, keine weiteren",
      ", ".join(branches), branches == ["delta/20260919-004", "main"],
      f"{Q_UE4} (Repository-Block); {Q_INST23} [S010] einziger Branch, [S011] dazu der Beleg-Branch")
default = "refs/heads/main" if out2.startswith("ref: refs/heads/main\tHEAD") else out2.split("\n")[0]
pruef("S0-05", "Default-Branch", "main", default, default == "refs/heads/main", f"{Q_INST23}, Kopf")
prs = sorted(int(k.split("/")[2]) for k in refs if re.fullmatch(r"refs/pull/\d+/head", k))
w(f"Information (kein Sollwert): Pull-Request-Refs auf dem Server #{prs[0]} bis #{prs[-1]}; "
  f"höchste Nummer #{prs[-1]}.")
w("Die Nummer des nächsten Pull Requests vergibt GitHub beim Anlegen; PR_START wird nach dem Merge")
w("aus dem Betreff des Merge-Commits gelesen, nicht vorausgesetzt.")

# ---------------------------------------------------------------- §2 Klon und Branch
sec("§2 — Klon, Branch mit ausdrücklicher Ref-Zuordnung, Historie")
r = run(["git", "fetch", "origin",
         f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}",
         "+refs/pull/9/head:refs/remotes/origin/pr/9"])
zeige(f"git fetch origin +refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH} "
      "+refs/pull/9/head:refs/remotes/origin/pr/9", r)
r = run(["git", "rev-parse", "HEAD", "main", "origin/main", f"refs/remotes/origin/{BRANCH}",
         "refs/remotes/origin/pr/9"])
out = zeige(f"git rev-parse HEAD main origin/main refs/remotes/origin/{BRANCH} refs/remotes/origin/pr/9", r)
rp = out.split()
pruef("S0-06", "HEAD, main und origin/main im Klon", f"alle drei {MAIN}", " / ".join(rp[:3]),
      len(rp) == 5 and rp[0] == rp[1] == rp[2] == MAIN, Q_UE4)
pruef("S0-07", f"origin/{BRANCH} nach ausdrücklicher Ref-Zuordnung", BRANCH_SHA,
      rp[3] if len(rp) > 3 else "—", len(rp) > 3 and rp[3] == BRANCH_SHA, Q_UE1 + " (S011, M-4)")
r = run(["git", "rev-list", "--count", "main"])
cnt = zeige("git rev-list --count main", r).strip()
pruef("S0-08", "Commits auf main", "20", cnt, cnt == "20", Q_UE4)
r = run(["git", "log", "-1", "--format=%s%n%cI", "main"])
out = zeige("git log -1 --format='%s%n%cI' main", r)
subj = out.split("\n")[0]
pruef("S0-09", "Betreff von main", "Merge PR #8 (Eingang Lauf 2)", subj,
      subj.startswith("Merge pull request #8 "), Q_UE4)
r = run(["git", "rev-parse", "76b33f9^{commit}"])
full = zeige("git rev-parse '76b33f9^{commit}'", r).strip()
r2 = run(["git", "merge-base", "--is-ancestor", START2, "main"])
zeige(f"git merge-base --is-ancestor {START2} main", r2)
pruef("S0-10", "<START> Lauf 2 aufgelöst und Vorfahre von main", f"{START2}, Vorfahre (exit 0)",
      f"{full}, exit {r2.returncode}", full == START2 and r2.returncode == 0,
      f"{Q_UE4}; {Q_INST23} [S010], Merge-Folge auf main")
r = run(["git", "log", "--oneline", "--graph", "--all", "-n", "30"])
zeige("git log --oneline --graph --all -n 30", r)

# ---------------------------------------------------------------- §3 Werkzeug
sec("§3 — Werkzeug engine/deltakit.py")
r = run(["git", "show", "main:engine/deltakit.py"])
f_tool = SCR / "deltakit_an_main.py"
w(f"$ git show main:engine/deltakit.py > {f_tool}")
w(f"  exit {r.returncode}")
if r.returncode == 0:
    f_tool.write_bytes(r.stdout)
    r2 = run(["sha256sum", str(f_tool)])
    out = zeige(f"sha256sum {f_tool}", r2)
    ist = out.split()[0] if out else "—"
else:
    ist = "— (git show fehlgeschlagen)"
pruef("S0-11", "sha256 des Werkzeugs an main, zweistufig", TOOL_SHA, ist, ist == TOOL_SHA, Q_UE4)
r = run(["sha256sum", TOOL])
out = zeige(f"sha256sum {TOOL}", r)
ist2 = out.split()[0] if out else "—"
pruef("S0-12", "sha256 des Werkzeugs im Arbeitsverzeichnis des Klons", TOOL_SHA, ist2, ist2 == TOOL_SHA, Q_UE4)
r = run(["git", "log", "-1", "--format=%H %s", "main", "--", TOOL])
out = zeige(f"git log -1 --format='%H %s' main -- {TOOL}", r).strip()
pruef("S0-13", "letzter Commit auf das Werkzeug", "f2694fd", out[:40] or "—",
      out.startswith("f2694fd"), f"{Q_INST23}, engine/: „Referenzfassung … seit f2694fd\"")

w()
w("Kontrollfall zum Prüfweg (Übergabe §5): falscher Commit, einmal mit Pipe, einmal zweistufig.")
r = subprocess.run(["bash", "-c", "git show 0000000:engine/deltakit.py | sha256sum"],
                   cwd=str(KLON), env=ENV, capture_output=True)
out = zeige("git show 0000000:engine/deltakit.py | sha256sum", r)
pipe_leer = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in out and r.returncode == 0
r2 = run(["git", "show", "0000000:engine/deltakit.py"])
w(f"$ git show 0000000:engine/deltakit.py > {SCR / 'k01.bin'}")
w("  " + r2.stderr.decode("utf-8", "replace").strip())
w(f"  exit {r2.returncode}")
kontrolle("K-01", "Prüfweg mit Pipe gegen zweistufig bei falschem Commit",
          "Pipe: exit 0 und Hash der leeren Eingabe e3b0c442…; zweistufig: exit ≠ 0",
          f"Pipe: {'exit 0, e3b0c442…' if pipe_leer else 'anders'}; zweistufig: exit {r2.returncode}",
          pipe_leer and r2.returncode != 0)

# ---------------------------------------------------------------- §4 Zieldatei
sec("§4 — Zieldatei, §2.1 an main")
r = run(["python3", TOOL, "hash", ZIEL, "--heading", H21, "--repo", "."])
out = zeige(f"python3 {TOOL} hash {ZIEL} --heading \"{H21}\" --repo .", r)
m_ctx = re.search(r"^context_hash\s*:\s*(\S+)$", out, re.M)
m_n = re.search(r"^expected_lines\.before:\s*(\d+)$", out, re.M)
m_b = re.search(r"^base_sha\s*:\s*(\S+)$", out, re.M)
ctx_tool = m_ctx.group(1) if m_ctx else "—"
versand_txt = (ANH / "VERSAND_Lauf-3.txt").read_bytes().decode("utf-8")
handbuch_txt = (ANH / "HANDBUCH_Lauf-3-Transportachse.md").read_bytes().decode("utf-8")
m_va = re.search(r"^\s*context_hash\s*:\s*(sha256:[0-9a-f]{64})\s*$", versand_txt, re.M)
m_hb = re.search(r"^\|\s*`context_hash`\s*\|\s*`(sha256:[0-9a-f]{64})`\s*\|\s*$", handbuch_txt, re.M)
ctx_versand = m_va.group(1) if m_va else "—"
ctx_handbuch = m_hb.group(1) if m_hb else "—"
pruef("S0-14", "hash läuft durch", "exit 0", f"exit {r.returncode}", r.returncode == 0, Q_UE1)
pruef("S0-15", "context_hash von §2.1 an main",
      f"f34a74a4…8de8f1; voll wie im ANKER des Versandtexts und in Handbuch §1 ({ctx_versand})",
      ctx_tool,
      kurz_passt(ctx_tool) and ctx_tool == ctx_versand == ctx_handbuch,
      f"{Q_UE1}; VERSAND_Lauf-3.txt ANKER; HANDBUCH_Lauf-3-Transportachse.md §1")
n21 = m_n.group(1) if m_n else "—"
pruef("S0-16", "Zeilen von §2.1 an main", "53", n21, n21 == "53", Q_UE1)
pruef("S0-17", "base_sha in der Ausgabe von hash = main", MAIN, m_b.group(1) if m_b else "—",
      bool(m_b) and m_b.group(1) == MAIN, Q_UE4)
r = run(["git", "show", f"main:{ZIEL}"])
f_ziel = SCR / "ziel_an_main.md"
w(f"$ git show main:{ZIEL} > {f_ziel}")
w(f"  exit {r.returncode}")
ziel_bytes = r.stdout if r.returncode == 0 else b""
f_ziel.write_bytes(ziel_bytes)
out = zeige(f"sha256sum {f_ziel}", run(["sha256sum", str(f_ziel)]))
w("Information (kein Sollwert): sha256 der ganzen Zieldatei an main, s. oben; "
  f"{len(ziel_bytes)} Bytes.")
ncr = ziel_bytes.count(b"\r")
pruef("S0-18", "Windows-Zeilenenden in der Zieldatei an main", "keine (0 × CR)", f"{ncr} × CR",
      r.returncode == 0 and ncr == 0, "HANDBUCH_Lauf-3-Transportachse.md §3 Schritt 0, Entwurf")

w()
w("Kontrollfall: dieselbe Messung am Branch der Lauf-2-Anwendung, der §2.1 verändert hat.")
k02 = SCR / "k02"
(k02 / "artefakte").mkdir(parents=True, exist_ok=True)
r = run(["git", "show", f"{BRANCH_SHA}:{ZIEL}"])
w(f"$ git show {BRANCH_SHA[:7]}:{ZIEL} > {k02 / ZIEL}")
w(f"  exit {r.returncode}")
(k02 / ZIEL).write_bytes(r.stdout)
r2 = run(["python3", str(KLON / TOOL), "hash", ZIEL, "--heading", H21, "--repo", "."], cwd=k02)
out = zeige(f"(in {k02}) python3 {KLON / TOOL} hash {ZIEL} --heading \"{H21}\" --repo .", r2, maxzeilen=8)
m_k = re.search(r"^context_hash\s*:\s*(\S+)$", out, re.M)
ctx_k = m_k.group(1) if m_k else "—"
kontrolle("K-02", "hash unterscheidet den Stand der Lauf-2-Anwendung (db543e3)",
          "exit 0 und ein anderer context_hash als an main",
          f"exit {r2.returncode}, {ctx_k[:23]}…",
          r.returncode == 0 and r2.returncode == 0 and ctx_k.startswith("sha256:") and ctx_k != ctx_tool)

# ---------------------------------------------------------------- §5 artefakte/ seit <START> Lauf 2
sec("§5 — artefakte/ seit <START> Lauf 2 (76b33f9)")
r = run(["git", "log", "--format=%H %s", f"{START2}..main", "--", "artefakte"])
out = zeige(f"git log --format='%H %s' {START2[:7]}..main -- artefakte", r)
pruef("S0-19", "Commits unter artefakte/ seit 76b33f9 bis main", "keiner", "keiner" if not out.strip() else out.strip(),
      r.returncode == 0 and not out.strip(), f"{Q_INST23} (artefakte/: „seit <START> unverändert, auch nach Lauf 2\")")
r1 = run(["git", "rev-parse", f"{START2}:{ZIEL}"])
r2 = run(["git", "rev-parse", f"main:{ZIEL}"])
b1 = zeige(f"git rev-parse {START2[:7]}:{ZIEL}", r1).strip()
b2 = zeige(f"git rev-parse main:{ZIEL}", r2).strip()
pruef("S0-20", "Blob der Zieldatei an 76b33f9 und an main", "derselbe Blob", f"{b1[:12]}… / {b2[:12]}…",
      r1.returncode == 0 and r2.returncode == 0 and b1 == b2, f"{Q_INST23}; PBP-ART-033 („derselbe Blob\")")

# ---------------------------------------------------------------- §6 audit
sec("§6 — audit")
PAT = re.compile(r"Commits auf Artefakten: (\d+) \| mit Delta-Bezug: (\d+) \| OHNE: (\d+)")
r = run(["python3", TOOL, "audit", "--repo", ".", "--start", "76b33f9", "--head", "main"])
out = zeige(f"python3 {TOOL} audit --repo . --start 76b33f9 --head main", r)
m = PAT.search(out)
tri = m.groups() if m else ("—", "—", "—")
pruef("S0-21", "audit ab 76b33f9 bis main", "ohne Befund: 0 Commits auf Artefakten, exit 0",
      f"{tri[0]} Commits, davon {tri[1]} mit und {tri[2]} ohne Delta-Bezug, exit {r.returncode}",
      r.returncode == 0 and tri == ("0", "0", "0"), Q_UE1)
w()
r = run(["python3", TOOL, "audit", "--repo", ".", "--start", "337876f", "--head", "main"])
out = zeige(f"python3 {TOOL} audit --repo . --start 337876f --head main", r)
m = PAT.search(out)
tri = m.groups() if m else ("—", "—", "—")
kontrolle("K-03", "audit findet einen nackten Commit, wo es einen gibt (Umbenennung 962ea3c)",
          "1 Commit ohne Delta-Bezug, 962ea3cb, exit 2 (Instanz §2.3 [S010]: positive Kontrolle)",
          f"{tri[0]} Commits, {tri[2]} ohne Delta-Bezug, exit {r.returncode}, 962ea3cb {'genannt' if '962ea3cb' in out else 'fehlt'}",
          r.returncode == 2 and tri == ("1", "0", "1") and "[OHNE DELTA] 962ea3cb" in out)
w()
r = run(["python3", TOOL, "audit", "--repo", ".", "--start", "76b33f9", "--head", f"refs/remotes/origin/{BRANCH}"])
out = zeige(f"python3 {TOOL} audit --repo . --start 76b33f9 --head refs/remotes/origin/{BRANCH}", r)
m = PAT.search(out)
tri = m.groups() if m else ("—", "—", "—")
kontrolle("K-04", "audit erkennt einen Commit mit Delta-Bezug (Anwendung Lauf 2 am Branch)",
          "1 Commit mit Delta-Bezug (db543e33, ULTRA-Δ-20260919-004), 0 ohne, exit 0",
          f"{tri[0]} Commits, {tri[1]} mit, {tri[2]} ohne Delta-Bezug, exit {r.returncode}",
          r.returncode == 0 and tri == ("1", "1", "0") and "db543e33  ULTRA-Δ-20260919-004" in out)

# ---------------------------------------------------------------- §7 Anhänge
sec("§7 — Die vier Anhänge gegen Übergabe §4")
r = run(["ls", "-la", str(ANH)])
zeige(f"ls -la {ANH}", r)
namen = sorted(p.name for p in ANH.iterdir() if p.is_file())
pruef("S0-22", "Anhänge im ersten Prompt", "genau diese vier: " + ", ".join(sorted(ANH_SOLL)),
      ", ".join(namen), namen == sorted(ANH_SOLL), f"{Q_UE2}, „Anhang im ersten Prompt — genau diese vier\"")
nr = 23
kopien_gleich = True
for name, (soll_sha, soll_z, soll_nl, ohne_nl_am_ende) in ANH_SOLL.items():
    b = (ANH / name).read_bytes()
    t = b.decode("utf-8")
    ist_sha = sha256_bytes(b)
    ncr_a = b.count(b"\r")
    nlf = t.count("\n")
    endet = "mit" if b.endswith(b"\n") else "ohne"
    w()
    w(f"{name}: {len(b)} Bytes · {len(t)} Zeichen · {nlf} × LF · {ncr_a} × CR · "
      f"endet {endet} Zeilenumbruch · sha256 {ist_sha}")
    kopie = [p for p in ANH2.iterdir() if p.name.endswith("-" + name)]
    if kopie:
        kb = kopie[0].read_bytes()
        w(f"  Kopie {kopie[0].name}: sha256 {sha256_bytes(kb)}")
        kopien_gleich &= (kb == b)
    else:
        w("  Kopie: nicht gefunden")
        kopien_gleich = False
    pruef(f"S0-{nr:02d}", f"{name}: sha256", soll_sha, ist_sha, ist_sha == soll_sha, Q_UE4); nr += 1
    pruef(f"S0-{nr:02d}", f"{name}: Zeichen und Zeilenumbrüche", f"{soll_z} Zeichen · {soll_nl} Zeilenumbrüche",
          f"{len(t)} Zeichen · {nlf} Zeilenumbrüche",
          len(t) == soll_z and nlf == soll_nl, Q_UE4); nr += 1
    if ohne_nl_am_ende:
        ok = ncr_a == 0 and endet == "ohne"
        soll_txt = "LF, ohne Zeilenumbruch am Ende"
        ist_txt = f"{ncr_a} × CR, endet {endet} Zeilenumbruch"
    else:
        ok = ncr_a == 0
        soll_txt = "LF (kein CR)"
        ist_txt = f"{ncr_a} × CR"
    pruef(f"S0-{nr:02d}", f"{name}: Zeilenenden", soll_txt, ist_txt, ok, Q_UE4); nr += 1
w()
w("Information: Beide Ablagen der Anhänge (/mnt/user-data/uploads und die @-Kopien) sind "
  + ("bytegleich." if kopien_gleich else "NICHT bytegleich — prüfen."))

# ---------------------------------------------------------------- §8 Teil B
sec("§8 — Teil B des Versandtexts nachgerechnet (R5)")
MARK = "ABSCHNITT IM AKTUELLEN ZUSTAND — folgt nach dieser Zeile.\n"
n_mark = versand_txt.count(MARK)
teilb = versand_txt.split(MARK, 1)[1] if n_mark == 1 else ""
teilb_r5 = teilb[:-1] if teilb.endswith("\n") else teilb
h_r5 = "sha256:" + sha256_bytes(teilb_r5.encode("utf-8"))
h_roh = "sha256:" + sha256_bytes(teilb.encode("utf-8"))
w(f"Trennzeile „{MARK.strip()}\" kommt {n_mark}× vor; Teil B = alles danach, "
  f"{len(teilb.encode('utf-8'))} Bytes.")
w(f"Teil B ohne genau einen Umbruch am Ende: sha256 {h_r5[7:]}")
spec = importlib.util.spec_from_file_location("deltakit_messung", str(f_tool))
dk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dk)
sek = dk.find_section(ziel_bytes.decode("utf-8"), H21)
sek_text = sek.get("section_text", "")
w(f"§2.1 an main über find_section() der Werkzeugfassung an main: {len(sek_text.split(chr(10)))} Zeilen, "
  f"sha256 {sha256_bytes(sek_text.encode('utf-8'))}")
pruef(f"S0-{nr:02d}", "Trennzeile vor Teil B genau einmal", "1×", f"{n_mark}×", n_mark == 1,
      "keine Datei — Voraussetzung dieser Nachrechnung"); nr += 1
pruef(f"S0-{nr:02d}", "Teil B nachgerechnet ergibt den context_hash", ctx_versand, h_r5,
      h_r5 == ctx_versand and kurz_passt(h_r5), f"{Q_UE1B} (Erwartung); HANDBUCH R5"); nr += 1
pruef(f"S0-{nr:02d}", "Teil B bytegleich mit §2.1 an main", "bytegleich",
      "bytegleich" if teilb_r5 == sek_text else "verschieden", teilb_r5 == sek_text and bool(sek_text),
      "VERSAND_Lauf-3.txt („ABSCHNITT IM AKTUELLEN ZUSTAND\"); Instanz v0.10 PBP-ART-044"); nr += 1
nzb = len(teilb_r5.split("\n"))
pruef(f"S0-{nr:02d}", "Teil B hat 53 Zeilen", "53", str(nzb), nzb == 53, Q_UE1); nr += 1
kontrolle("K-05", "ohne das Entfernen des letzten Umbruchs passt der Hash nicht",
          "anderer Hash als der context_hash", f"{h_roh[:23]}…", h_roh != ctx_versand)

# ---------------------------------------------------------------- §9 Platzhalter
sec("§9 — Platzhalter in den Entwürfen")
PH = re.compile(r"⟨([^⟨⟩\n]*)⟩")
kontrolle("K-06", "das Suchmuster findet Platzhalter", "2 Treffer in „a ⟨START⟩ b ⟨X_Y⟩\"",
          f"{len(PH.findall('a ⟨START⟩ b ⟨X_Y⟩'))} Treffer", len(PH.findall("a ⟨START⟩ b ⟨X_Y⟩")) == 2)
funde = {}
for name in ("AUSWERTUNG_Lauf3.md", "VERSAND_Lauf-3.txt", "HANDBUCH_Lauf-3-Transportachse.md"):
    t = (ANH / name).read_bytes().decode("utf-8")
    liste = []
    for i, z in enumerate(t.split("\n"), 1):
        for m in PH.finditer(z):
            liste.append((m.group(1), i))
    funde[name] = liste
    zusammen: dict[str, list[int]] = {}
    for n_, i in liste:
        zusammen.setdefault(n_, []).append(i)
    w(f"{name}: {len(liste)} Platzhalter" + ("" if not liste else " — " + "; ".join(
        f"{k} ×{len(v)} (Zeile {', '.join(map(str, v))})" for k, v in sorted(zusammen.items()))))
pruef(f"S0-{nr:02d}", "AUSWERTUNG_Lauf3.md ohne Platzhalter", "keiner", f"{len(funde['AUSWERTUNG_Lauf3.md'])}",
      not funde["AUSWERTUNG_Lauf3.md"], f"{Q_UE1B}: Platzhalter nur in Versandtext und Handbuch"); nr += 1
namen_ph = {n_ for k in ("VERSAND_Lauf-3.txt", "HANDBUCH_Lauf-3-Transportachse.md") for n_, _ in funde[k]}
pruef(f"S0-{nr:02d}", "Platzhalter in Versandtext und Handbuch", ", ".join(sorted(PLATZHALTER_SOLL)) + ", keine anderen",
      ", ".join(sorted(namen_ph)), namen_ph == PLATZHALTER_SOLL, Q_UE1B); nr += 1

# ---------------------------------------------------------------- §10 Lauf-3-Dateien
sec("§10 — Lauf-3-Dateien noch nicht im Repository")
drei = ["AUSWERTUNG_Lauf3.md", "VERSAND_Lauf-3.txt", "HANDBUCH_Lauf-3-Transportachse.md"]
ex = []
for f in drei:
    r = run(["git", "cat-file", "-e", f"main:{f}"])
    w(f"$ git cat-file -e main:{f}")
    w(f"  exit {r.returncode}")
    ex.append(r.returncode)
r = run(["git", "log", "--all", "--format=%H", "--"] + drei)
out = zeige("git log --all --format=%H -- " + " ".join(drei), r)
pruef(f"S0-{nr:02d}", "keine der drei Lauf-3-Dateien an main oder in einem geholten Ref",
      "nicht vorhanden (cat-file ≠ 0, git log leer)",
      f"cat-file exit {ex}, git log {'leer' if not out.strip() else 'nicht leer'}",
      all(e != 0 for e in ex) and not out.strip() and r.returncode == 0,
      "Instanz v0.10 PBP-ART-044 („Entwurf bis zur Versiegelung\"); Übergabe §1 Schritt 1"); nr += 1

# ---------------------------------------------------------------- §11 Wissensbasis
sec("§11 — Wissensbasis (Layer 1)")
w("Abschrift der Werkzeugausgabe project_info aus diesem Chat, nicht vom Skript gemessen:")
for d in KB_IST:
    w("  " + d)
pruef(f"S0-{nr:02d}", "Layer 1 der Wissensbasis", "genau die sieben Dateien aus Übergabe §2, GESAMT 7 / 12",
      f"{len(KB_IST)} Dateien, {'gleich der Liste' if set(KB_IST) == KB_SOLL else 'abweichend'}",
      set(KB_IST) == KB_SOLL and len(KB_IST) == 7, f"{Q_UE2}, Layer 1"); nr += 1
w("Nicht gemessen: ob die Dateien der Wissensbasis bytegleich mit den Archivfassungen sind — die")
w("Wissensbasis liefert Text, keine Bytes (Übergabe §5, §6).")

# ---------------------------------------------------------------- §12 Aussagen, die versiegelt werden
sec("§12 — Aussagen, die mit der Versiegelung unveränderlich werden")
w("Über die Liste in Übergabe §1 hinaus gemessen: AUSWERTUNG_Lauf3.md wird mit Schritt 1a, Versandtext")
w("und Handbuch mit 1c versiegelt; danach lässt sich an ihnen nichts mehr berichtigen.")


def git_datei(ref: str, pfad: str, ziel: pathlib.Path) -> tuple[int, str]:
    r = run(["git", "show", f"{ref}:{pfad}"])
    w(f"$ git show {ref}:{pfad} > {ziel}")
    w(f"  exit {r.returncode}")
    if r.returncode == 0:
        ziel.write_bytes(r.stdout)
        return 0, r.stdout.decode("utf-8")
    return r.returncode, ""


RE_REGEL = re.compile(r"^Angewendet wird das erste Delta.*?Besteht keines, wird keines angewendet\.$", re.M | re.S)
e1, t1 = git_datei("47bc2c2", "AUSWERTUNG_Lauf1.md", SCR / "auswertung_lauf1_47bc2c2.md")
e2, t2 = git_datei("0221334", "AUSWERTUNG_Lauf2.md", SCR / "auswertung_lauf2_0221334.md")
a3 = (ANH / "AUSWERTUNG_Lauf3.md").read_bytes().decode("utf-8")
regeln = []
for label, t in (("Lauf 1 (47bc2c2)", t1), ("Lauf 2 (0221334)", t2), ("Lauf 3 (Anhang)", a3)):
    m = RE_REGEL.search(t)
    regeln.append(m.group(0) if m else None)
    w(f"Auswahlregel {label}: " + (f"{len(m.group(0))} Zeichen, sha256 "
                                   f"{sha256_bytes(m.group(0).encode('utf-8'))}" if m else "nicht gefunden"))
pruef(f"S0-{nr:02d}", "Auswahlregel in AUSWERTUNG_Lauf3.md §1 wortgleich mit Lauf 1 und Lauf 2",
      "wortgleich, dreimal derselbe Text",
      "wortgleich" if (regeln[0] and regeln[0] == regeln[1] == regeln[2]) else "verschieden oder nicht gefunden",
      e1 == 0 and e2 == 0 and bool(regeln[0]) and regeln[0] == regeln[1] == regeln[2],
      "AUSWERTUNG_Lauf3.md §1 („Wortgleich mit …\"); Instanz v0.10 §2.3 [S012] Auswahlregel"); nr += 1
r1 = run(["git", "log", "--format=%H", "main", "--", "AUSWERTUNG_Lauf1.md"])
o1 = zeige("git log --format=%H main -- AUSWERTUNG_Lauf1.md", r1).split()
r2 = run(["git", "log", "--format=%H", "main", "--", "AUSWERTUNG_Lauf2.md"])
o2 = zeige("git log --format=%H main -- AUSWERTUNG_Lauf2.md", r2).split()
pruef(f"S0-{nr:02d}", "die in §1 genannten Commits sind die einzigen auf diesen Dateien",
      "AUSWERTUNG_Lauf1.md nur 47bc2c2 · AUSWERTUNG_Lauf2.md nur 0221334",
      f"{' '.join(s[:7] for s in o1)} · {' '.join(s[:7] for s in o2)}",
      len(o1) == 1 and o1[0].startswith("47bc2c2") and len(o2) == 1 and o2[0].startswith("0221334"),
      "AUSWERTUNG_Lauf3.md §1; Instanz v0.10 §2.3 (47bc2c2 „seither unverändert\", 0221334 versiegelt)"); nr += 1

w()
e3, v2 = git_datei("main", "VERSAND_Lauf-2.txt", SCR / "versand_lauf2_main.txt")
r = run(["diff", str(SCR / "versand_lauf2_main.txt"), str(ANH / "VERSAND_Lauf-3.txt")])
zeige(f"diff {SCR / 'versand_lauf2_main.txt'} {ANH / 'VERSAND_Lauf-3.txt'}", r)


def maskiere(text: str) -> str | None:
    """Ersetzt Ankerwerte, delta_id-Zeile, expected_lines-Zeile und die vierte Regel durch Marken."""
    z = text.split("\n")

    def idx(pred):
        return [i for i, s in enumerate(z) if pred(s)]
    a, b = idx(lambda s: s.startswith("ANKER —")), idx(lambda s: s == "AUFGABE")
    d, e = idx(lambda s: '"delta_id":' in s), idx(lambda s: '"expected_lines":' in s)
    v = idx(lambda s: s.startswith("VIER REGELN, AN DENEN DER AUFTRAG SONST ABGELEHNT WIRD"))
    if not (len(a) == len(b) == len(d) == len(e) == len(v) == 1):
        return None
    a, b, d, e, v = a[0], b[0], d[0], e[0], v[0]
    if z[b - 1] != "" or not (b - 1 > a + 1):
        return None
    ende = next((i for i in range(v + 1, len(z)) if z[i] == ""), None)
    if ende is None:
        return None
    bullets = [i for i in range(v + 1, ende) if z[i].startswith("  - ")]
    if len(bullets) != 4:
        return None
    out, i = [], 0
    while i < len(z):
        if i == a + 1:
            out.append("[ANKERWERTE]"); i = b - 1; continue
        if i == d:
            out.append("[DELTA_ID]"); i += 1; continue
        if i == e:
            out.append("[EXPECTED_LINES]"); i += 1; continue
        if i == bullets[3]:
            out.append("[REGEL 4]"); i = ende; continue
        out.append(z[i]); i += 1
    return "\n".join(out)


def anker(text: str) -> dict:
    z = text.split("\n")
    a = next(i for i, s in enumerate(z) if s.startswith("ANKER —"))
    b = next(i for i, s in enumerate(z) if s == "AUFGABE")
    kv = {}
    for s in z[a + 1:b - 1]:
        k, _, val = s.partition(":")
        kv[k.strip()] = val.strip()
    return kv


m2, m3 = maskiere(v2), maskiere(versand_txt)
w(f"Maskiert (Ankerwerte, delta_id, expected_lines, vierte Regel): Lauf 2 "
  f"{'ok' if m2 is not None else 'nicht maskierbar'}, Lauf 3 {'ok' if m3 is not None else 'nicht maskierbar'}")
pruef(f"S0-{nr:02d}", "Versandtext Lauf 2 → Lauf 3 außerhalb der erklärten Stellen wortgleich (darin Aufgabe und Teil B)",
      "wortgleich außer Ankerwerten, delta_id, expected_lines im Ausgabeformat und vierter Regel",
      "wortgleich" if (m2 is not None and m2 == m3) else "verschieden oder nicht maskierbar",
      e3 == 0 and m2 is not None and m3 is not None and m2 == m3,
      "AUSWERTUNG_Lauf3.md §4 (Gewollt: Zielzahl im Anker, vierte Regel mit delta_id; Unvermeidlich: Anker "
      "und delta_id neu; Unverändert: Aufgabe wortgleich, Abschnitt)"); nr += 1
k2, k3 = anker(v2), anker(versand_txt)
w(f"ANKER Lauf 2: {k2}")
w(f"ANKER Lauf 3: {k3}")
gleich = [k for k in ("document", "section_heading", "context_hash", "expected_lines.before")
          if k in k2 and k in k3 and k2[k] == k3[k]]
pruef(f"S0-{nr:02d}", "Anker Lauf 2 → Lauf 3: Dokument, Überschrift, context_hash und 53 Zeilen gleich; neu die Zielzahl 50",
      "4 Werte gleich · expected_lines.after = 50 nur in Lauf 3 · base_sha verschieden",
      f"{len(gleich)} gleich ({', '.join(gleich)}) · after = {k3.get('expected_lines.after', '—')} "
      f"(Lauf 2: {k2.get('expected_lines.after', 'fehlt')}) · base_sha {k2.get('base_sha', '—')[:7]} → {k3.get('base_sha', '—')}",
      len(gleich) == 4 and k2.get("expected_lines.before") == "53" and k3.get("expected_lines.after") == "50"
      and "expected_lines.after" not in k2 and k2.get("base_sha") == START2 and k3.get("base_sha") == "⟨START⟩",
      "AUSWERTUNG_Lauf3.md §4 („Abschnitt (53 Zeilen, context_hash wie in Lauf 2)\", Zielzahl 50 als Ankerwert)"); nr += 1
v3_kaputt = versand_txt.replace("Der Befund zur Bündel-Konvention ist geschlossen.",
                                "Der Befund zur Bündel-Konvention ist geschlossen!", 1)
kontrolle("K-07", "die maskierte Gegenüberstellung bemerkt ein geändertes Zeichen in Teil B",
          "ungleich", "ungleich" if maskiere(v3_kaputt) != m2 else "gleich",
          v3_kaputt != versand_txt and maskiere(v3_kaputt) is not None and maskiere(v3_kaputt) != m2)

w()
r = run(["git", "merge-base", "--is-ancestor", BRANCH_SHA, "main"])
zeige(f"git merge-base --is-ancestor {BRANCH_SHA} main", r)
pruef(f"S0-{nr:02d}", "Anwendung aus Lauf 2 (db543e3) nicht auf main", "kein Vorfahre von main (exit 1)",
      f"exit {r.returncode}", r.returncode == 1,
      "AUSWERTUNG_Lauf3.md §3 („Lauf 2 zählt nicht (Klasse D, kein Merge)\"); Instanz v0.10 PBP-ART-035"); nr += 1

w()
Z = sek_text.split("\n")


def zl(n: int) -> str:
    return Z[n - 1] if 0 < n <= len(Z) else "∅"


w("§2.1 an main, Zeilen nach der Zählung in Handbuch §5 (Überschrift = Zeile 1):")
for n in (1, 2, 3, 4, 5, 6, 22, 23, 24, 25, 32, 33, 34, 35, 36, 47, 48, 49, 50):
    w(f"  {n:2d} │{zl(n)}")
ok5 = (zl(1) == H21 and zl(2) == "" and zl(3).startswith("*Delta `ULTRA-Δ-20260912-001`")
       and zl(4).endswith("korrekt.*") and zl(5) == "" and zl(6) == "```"
       and zl(23).lstrip().startswith("ULTRA_PROTOCOL_SYS_DELTA_1_1.md")
       and zl(24).lstrip().startswith("ULTRA_REF_SYS_DELTA_ENGINE_1_0.md")
       and zl(33).lstrip().startswith("ULTRA_ARCH_SYS_DELTA-FORCE-SUBSTRAT_0_1.md")
       and zl(34).startswith(" ") and "gemessene Befunde" in zl(34)
       and zl(36).startswith("SCHICHT 3") and "UEBERGABE_PBP-S005_nach_S006.md" in zl(48) and zl(49) == "```")
pruef(f"S0-{nr:02d}", "Zeilentabelle in Handbuch §5 passt zu §2.1 an main",
      "Notiz mit Leerzeilen 2–5 · Vermerke 23, 24, 33+34 · letzter Eintrag unter SCHICHT 3 in Zeile 48",
      "passt" if ok5 else "passt nicht", ok5,
      "HANDBUCH_Lauf-3-Transportachse.md §5, Entwurf; Aufgabe in VERSAND_Lauf-3.txt"); nr += 1

# ---------------------------------------------------------------- §13 Zusatz
sec("§13 — Zusatz, ohne Prüfung")
w("Regelliste für main über die GitHub-API: Die Anfrage an api.github.com (rules/branches/main)")
w("wurde vom Proxy dieser Sitzung mit HTTP 403 abgewiesen (GitHub-Zugriff für dieses Repository in")
w("der Sitzung nicht freigegeben). Nicht umgangen; Zugangsdaten wurden nicht angefordert, weil in")
w("das Repository nur der Owner schreibt. Der Punkt bleibt offen wie in S011 und S012.")

# ---------------------------------------------------------------- §14 Klon sauber
sec("§14 — Klon nach der Messung")
r = run(["git", "status", "--porcelain", "--ignored"])
out = zeige("git status --porcelain --ignored", r)
pyc = [str(p) for p in KLON.rglob("__pycache__")]
w(f"__pycache__ im Klon: {pyc if pyc else 'keiner'}")
pruef(f"S0-{nr:02d}", "Arbeitsverzeichnis des Klons unverändert", "leer, kein __pycache__",
      ("leer" if not out.strip() else out.strip()) + (", " + str(pyc) if pyc else ", kein __pycache__"),
      r.returncode == 0 and not out.strip() and not pyc, "Übergabe S012→S013 §7, M-11"); nr += 1

# ---------------------------------------------------------------- Schluss
sec("Schluss")
n_ok = sum(ok for _, ok in CHECKS)
k_ok = sum(ok for _, ok in KONTR)
w(f"Prüfungen: {n_ok} von {len(CHECKS)} ohne Abweichung.")
abw = [c for c, ok in CHECKS if not ok]
w("Abweichungen: " + (", ".join(abw) if abw else "keine"))
w(f"Kontrollfälle: {k_ok} von {len(KONTR)} wie erwartet"
  + ("" if k_ok == len(KONTR) else " — " + ", ".join(k for k, ok in KONTR if not ok)))
w("Nicht im Protokoll, weil außerhalb von Schritt 0: check-Proben mit dem Anker von Lauf 3 — sie")
w("gehören zu Handbuch §3 Schritt 0, nach der Versiegelung.")
w("Vor der ersten Ausgabe berichtigt oder ergänzt (Selbstauskunft der KI): die Anzeige von K-01 (ein")
w("doppeltes „exit 0\"), drei Quellenangaben (S0-10, S0-35, S0-37) und §12. Weil jeder Lauf den Klon um")
w("den Ref origin/pr/9 ergänzt, klont das Skript jetzt bei jedem Lauf frisch. Die Messwerte von S0-01")
w("bis S0-42 sind gleich wie im ersten Lauf.")
w()
w("*messung_S013_schritt0.txt | Messprotokoll Schritt 0 | PBP-S013 | Owner: Co-Creator*")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{n_ok}/{len(CHECKS)} Prüfungen ok · {k_ok}/{len(KONTR)} Kontrollfälle wie erwartet · Abweichungen: {abw or 'keine'}")
print(f"geschrieben: {OUT}")
