# Handbuch — Lauf 2 der Transportachse

*Operativ. Für einen Menschen geschrieben. Owner: Co-Creator · entworfen in PBP-S010, 2026-09-19*
*Repository: `andreasborchmann/DELTA` (öffentlich) · `<START>` = `76b33f9`*

*Versiegelt vor dem Versand, zusammen mit `VERSAND_Lauf-2.txt`. Auswahlregel, Testszenario und
Fehlerklassen stehen in `AUSWERTUNG_Lauf2.md` und werden hier nicht wiederholt.*

---

## 0 — Was gemessen wird, in einem Satz

Ob ein Änderungsauftrag, den ein fremdes Modell ohne Kenntnis der Anwendung schnürt, ohne
Nacharbeit durch die Kette läuft und so im Repository landet, wie `check` ihn freigegeben hat.

**Was nicht gemessen wird:** ob die Änderung inhaltlich klug ist. Das entscheidest du am Diff.

---

## 1 — Stand beim Versiegeln

| | |
|---|---|
| `<START>` | `76b33f9d82ce8c0b56e510abd1a95ba1d21b2817` (Merge von PR #6) |
| Zieldatei | `artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md` |
| Abschnitt | `### 2.1 Schicht-Architektur`, 53 Zeilen |
| `context_hash` | `sha256:f34a74a4fcb5d59eaf1988087b10da0404b4b0c4610742f1df719ae5c78de8f1` |
| Werkzeug | `engine/deltakit.py`, sha256 `931cd7eb12dd46d413b8cc23cf5eb645707abfa4d52fcf8bc65824aff6d73b3c` |
| Auswertung | `AUSWERTUNG_Lauf2.md`, sha256 `60f3b2e7048efef4f98836b4ad7f0b8a36faa6345174244f699119ca5bf09435` |
| Auftragspaket | `VERSAND_Lauf-2.txt`, sha256 `cc4506adf6fc41c96cbbd61fe99d80e7d0f1347f0dd4ee63427af554b64abd18` |
| `delta_id` | `ULTRA-Δ-20260919-004` |
| Agent | Claude Code Web, Haiku 4.5 |
| Regel für `main` | Ruleset, leere Bypass-Liste, durchgesetzt (gemessen 2026-09-19) |

---

## 2 — Regeln bis zum Ende des Laufs

- **R1** Nach dem Ankerzug bleibt die Zieldatei unberührt, bis die Anwendung sie ändert. `check`
  vergleicht nämlich die ganze Datei gegen `base_sha`, nicht nur §2.1.
- **R2** Nach `<START>` landet unter `artefakte/` nur noch die Anwendung, und zwar mit `delta_id`
  im Betreff. Versiegelte Dateien kommen ins Wurzelverzeichnis, Rohausgaben nach `deltas/eingang/`.
- **R3** Kein Vorbereitungs-Commit nennt eine `delta_id` im Betreff. `audit` erkennt den
  Delta-Bezug als Teilstring im Betreff.
- **R4** Jeder Merge wird als „Create a merge commit" ausgeführt.
- **R5** Maßgeblich ist immer die Werkzeugausgabe, nie eine Zusammenfassung. Abschnittskopien
  werden nachgerechnet: genau einen Umbruch am Ende entfernen, dann muss sha256 den
  `context_hash` ergeben.
- **R6** Das Repository bleibt öffentlich, bis Lauf 2 abgeschlossen ist. Sonst greift die Regel
  für `main` nicht mehr.
- **R7** In der Vorbereitung schreibst nur du. Im Lauf schreibt der Agent die Anwendung auf einen
  Branch, weil das Erfolgskriterium es so verlangt. Gemergt wird weiterhin von dir.

---

## 3 — Versand

1. Drei frische Chats: ChatGPT, Grok, Qwen. In jedem vorher Websuche und chatübergreifendes
   Gedächtnis ausschalten oder einen temporären bzw. privaten Chat nutzen. Was der Anbieter
   dafür anbietet, prüfst du vorher; geht es bei einem nicht, notierst du das.
2. In jeden Chat den vollständigen Inhalt von `VERSAND_Lauf-2.txt` einfügen, sonst nichts.
   Nichts aus Lauf 1a oder 1b erwähnen.
3. Rückfragen zum Abschnitt sind erlaubt. Rückfragen zur Anwendung nicht beantworten, sonst ist
   der Auftrag nicht mehr blind gegenüber der Anwendung.
4. Antworten roh sichern als `chatgpt-lauf2.json`, `grok-lauf2.json`, `qwen-lauf2.json`:
   speichern, keinen Formatierbefehl ausführen, nichts reparieren, nichts kürzen. Ein Modell, das
   ungültiges JSON liefert, hat ein ungültiges Delta geliefert — das ist ein Messwert.
5. Enthält eine Antwort Quellenangaben oder Links, notierst du das: Dann hat das Modell gesucht.

---

## 4 — Eingang, Prüfung, Anwendung

**4.1 Eingang** (du, Browser). Die drei Dateien über „Add file" → „Upload files" nach
`deltas/eingang/`, neuer Branch, Pull Request, „Create a merge commit".
Commit message: `Lauf 2: drei Deltas eingegangen`.

**4.2 Prüfen** (Claude Code Web, neue Sitzung nach dem Eingang):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts, repariere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
sha256sum engine/deltakit.py
python3 engine/deltakit.py check deltas/eingang/chatgpt-lauf2.json --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/grok-lauf2.json --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/qwen-lauf2.json --repo . ; echo "exit $?"
```

Die ganze Seite kopieren (R5). Angewendet wird nach der Auswahlregel in `AUSWERTUNG_Lauf2.md`.
Besteht keines, endet der Lauf hier — als Ergebnis, nicht als Abbruch.

**4.3 Anwenden** (Claude Code Web, dieselbe Sitzung). `<x>` steht für das gewählte Delta,
zum Beispiel `qwen-lauf2`:

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe. Keine Zusammenfassung.
python3 engine/deltakit.py pr-body deltas/eingang/<x>.json --repo .
git checkout -b delta/20260919-004
python3 engine/deltakit.py render deltas/eingang/<x>.json --repo . --write
git add artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md
git commit -m "ULTRA-Δ-20260919-004 (<x>.json): Anwendung Lauf 2"
git push -u origin delta/20260919-004
git show --stat HEAD
Nicht nach main pushen, nichts mergen.
```

**4.4 Pull Request** (du, Browser). Nach dem Push „Compare & pull request", als Beschreibung
die Ausgabe von `pr-body`. P2 am Diff prüfen (Abschnitt 5), dann „Create a merge commit".

**4.5 Nachprüfen** (Claude Code Web, neue Sitzung nach dem Merge):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
python3 engine/deltakit.py verify deltas/eingang/<x>.json --repo . ; echo "exit $?"
python3 engine/deltakit.py audit --repo . --start 76b33f9d82ce8c0b56e510abd1a95ba1d21b2817 --head HEAD ; echo "exit $?"
```

P3 und P4 nach `AUSWERTUNG_Lauf2.md`. Solange das Repository öffentlich ist, rechne ich `check`,
`verify` und `audit` auf einem eigenen Klon nach.

---

## 5 — P2: Erwartung und Lesart

Zeilennummern im Abschnitt, Überschrift = Zeile 1:

| Aussage | betroffene Zeilen |
|---|---|
| 1 — Notiz entfällt | 2 bis 5: die Notiz und die Leerzeilen zwischen Überschrift und Code-Block |
| 2 — drei neue Vermerke | 23 und 24; 33 und 34 werden zu einer Zeile |
| 3 — neuer letzter Eintrag | eine neue Zeile nach Zeile 48 |

**Referenzumsetzung** (gebaut in PBP-S010, mit `check` am Anker geprüft): 53 → 50 Zeilen,
7 Zeilen geändert oder entfernt, 4 eingefügt, rund 15 Zeilen im Auftrag. Das ist eine
Erwartung, kein Gate.

**„Nichts sonst" heißt:** Außerhalb der betroffenen Zeilen ändert sich keine Zeile. Innerhalb ist
die Form frei, solange die Aussage zutrifft — zum Beispiel, ob der Pfeil `←` vor einem Vermerk
stehen bleibt oder wie der neue Eintrag eingerückt ist.

---

## 6 — Was in diesem Handbuch ungeprüft ist

- Ob ChatGPT, Grok und Qwen Websuche und Gedächtnis abschalten lassen.
- Ob die Chatfenster beim Einfügen Leerzeichen oder Zeilen verändern. Das war in 1b genauso
  wenig messbar.
- Der Befundtext von `audit` spricht noch von einem Repository „ohne durchgesetzte Branch
  Protection". Das ist fester Text im Werkzeug; das Werkzeug bleibt für Lauf 2 unverändert.

---

*HANDBUCH_Lauf-2-Transportachse.md | Operative Referenz | Owner: Co-Creator | 2026-09-19*
