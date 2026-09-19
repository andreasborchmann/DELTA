# Auswertung Lauf 2 — Transportachse

*Versiegelt vor dem Versand: gilt ab dem Merge dieser Datei auf `main` und wird danach nicht mehr geändert.
Owner: Co-Creator · entworfen in PBP-S010, 2026-09-19*

---

## 1 — Auswahlregel

Angewendet wird das erste Delta in der Reihenfolge ChatGPT, Grok, Qwen,
das deltakit check ohne Handkorrektur besteht. Bestehen alle drei, gilt
ChatGPT. Besteht keines, wird keines angewendet.

Wortgleich mit `AUSWERTUNG_Lauf1.md` (`47bc2c2`).

## 2 — Begriffe

**Versiegelt** heißt für Lauf 2: vor dem Versand auf `main` gemergt. Das gilt für diese Datei,
für `HANDBUCH_Lauf-2-Transportachse.md` und für das Auftragspaket `VERSAND_Lauf-2.txt`.

**`<START>`** ist der `base_sha` des versandten Ankers, also der Commit, auf dem der Anker
gezogen wurde. Er steht in jeder Delta-Datei dieses Laufs.

## 3 — Testszenario

Vier Prüfungen, in dieser Reihenfolge. Jede hat genau ein Ergebnis.

| # | Prüfung | Bestanden wenn |
|---|---|---|
| P1 | `check` auf dem gewählten Delta | Exit 0, ohne dass jemand die Datei angefasst hat |
| P2 | Diff im Pull Request | enthält die drei Änderungen, die die Aufgabe in `VERSAND_Lauf-2.txt` verlangt, und **nichts sonst** |
| P3 | `verify` nach dem Merge | Exit 0, Vergleich nach Angleichung der Zeilenenden |
| P4 | `audit` von `<START>` (exklusiv) bis `HEAD` | kein Commit auf `artefakte/` ohne Delta-Bezug |

Zu P2: Ein Delta, das mehr als etwa 15 der 53 Zeilen berührt, tut mehr als die Aufgabe
verlangt. Das ist kein Gate — es ist die Erwartung, gegen die du den Diff liest.

### Fehlerklassen, vorab benannt

| Klasse | Bedeutung |
|---|---|
| A — Schema-Ablehnung | Das Modell hat das Format nicht getroffen, einschließlich der Regeln von `replace_lines`: kein Treffer, mehrere Treffer, Überlappung. Werkzeug ok. |
| B — Hash-Ablehnung | Der Abschnitt oder die Zieldatei hat sich seit dem Anker bewegt. Werkzeug ok, Schutz greift. |
| C — Bilanz-Ablehnung | Erklärte und gemessene Zeilenzahl weichen ab. Werkzeug ok. |
| D — durchgelassen, aber falsch | `check` sagt ja, der Diff zeigt ungewollte Änderungen. **Werkzeuglücke.** |
| E — `verify` weicht ab | Zwischen Anwendung und Merge ist etwas passiert. **Kettenlücke.** |
| F — nackter Commit im `audit` | Ein Commit ohne Delta-Bezug hat das Merge-Tor passiert. Gehört gezählt und erklärt. |

**Entscheidend:** A, B und C sind **keine Fehlschläge des Laufs**. Sie sind das Tor bei
der Arbeit. Der Lauf scheitert nur an D und E — wenn etwas Falsches durchkommt oder
etwas anderes im Repository landet als angesagt.

Ein Lauf, in dem alle drei Deltas abgelehnt werden, ist **kein Nichtergebnis**. Er sagt:
Die Kette hält, und das Schnüren durch fremde Modelle ist schwerer als gedacht. Das ist
mehr wert als ein Erfolg, den man sich zurechtgelegt hat.

Ob Lauf 2 als zweiter Lauf zählt, entscheiden die Definitionen „fehlerfrei", „unabhängig" und
„automatisch" zum Erfolgskriterium (Owner-Entscheid 2026-09-17, PBP-Instanz DELTA-FORCE).

Stand vor Lauf 2: Die Transportachse steht bei 1 von 2 (Lauf 1b), ohne Vorbehalt.

## 4 — Erklärte Abweichungen zu Lauf 1b

- **Gewollt:** Die Regel für `main` ist durchgesetzt (Ruleset, leere Bypass-Liste, gemessen am
  19.09.2026). Folge: Jede Änderung an `main` läuft über einen Pull Request mit Merge-Commit,
  auch die Rohausgaben.
- **Unvermeidlich:** Anker (Dateiname, `base_sha`, `context_hash`), eine neue Aufgabe (Wortlaut in
  `VERSAND_Lauf-2.txt`), 53 statt 59 Zeilen, eine neue `delta_id`.
- **Neu durch Owner-Entscheid:**
  - Das Repository ist öffentlich (1b: privat). Gegenmaßnahme: Websuche und Gedächtnis in den
    drei Versand-Chats aus.
  - Auswahlregel, Testszenario, Handbuch und Auftragspaket liegen vor dem Versand auf `main`
    (1b: nur die Auswahlregel).
  - P4 zählt ab `<START>` (1b: ab `b19c382`).
  - Vorbereitende Messungen und der Anker kommen aus einem Klon im Steuerungs-Chat, mit derselben
    `deltakit`-Datei (1b: Claude Code Web).
- **Vorab präzisiert:** Klasse A, B, P3 und F (Abschnitt 3).

---

*AUSWERTUNG_Lauf2.md | Auswertungsschlüssel Lauf 2 | Owner: Co-Creator | 2026-09-19*
