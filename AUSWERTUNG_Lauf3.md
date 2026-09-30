# Auswertung Lauf 3 — Transportachse

*Versiegelt vor dem Versand: gilt ab dem Merge dieser Datei auf `main` und wird danach nicht mehr geändert.
Owner: Co-Creator · entworfen in PBP-S012, 2026-09-30*

---

## 1 — Auswahlregel

Angewendet wird das erste Delta in der Reihenfolge ChatGPT, Grok, Qwen,
das deltakit check ohne Handkorrektur besteht. Bestehen alle drei, gilt
ChatGPT. Besteht keines, wird keines angewendet.

Wortgleich mit `AUSWERTUNG_Lauf1.md` (`47bc2c2`) und `AUSWERTUNG_Lauf2.md` (`0221334`).

## 2 — Begriffe

**Versiegelt** heißt für Lauf 3: vor dem Versand auf `main` gemergt. Das gilt für diese Datei,
für `HANDBUCH_Lauf-3-Transportachse.md` und für das Auftragspaket `VERSAND_Lauf-3.txt`.

**`<START>`** ist der `base_sha` des versandten Ankers, also der Commit, auf dem der Anker
gezogen wurde. Er steht in jeder Delta-Datei dieses Laufs.

**Ankerwerte** sind die Werte im ANKER-Block von `VERSAND_Lauf-3.txt` — `document`,
`section_heading`, `base_sha`, `context_hash`, `expected_lines.before` und
`expected_lines.after` — und die `delta_id` aus dem Ausgabeformat des Pakets. Ein Delta übernimmt
sie unverändert.

## 3 — Testszenario

Vier Prüfungen, in dieser Reihenfolge. Jede hat genau ein Ergebnis.

| # | Prüfung | Bestanden wenn |
|---|---|---|
| P1 | `check` auf dem gewählten Delta | Exit 0, ohne dass jemand die Datei angefasst hat |
| P2 | Diff im Pull Request | enthält die drei Änderungen, die die Aufgabe in `VERSAND_Lauf-3.txt` verlangt, und **nichts sonst** |
| P3 | `verify` nach dem Merge | Exit 0, Vergleich nach Angleichung der Zeilenenden |
| P4 | `audit` von `<START>` (exklusiv) bis `HEAD` | kein Commit auf `artefakte/` ohne Delta-Bezug |

Zu P2: Ein Delta, das mehr als etwa 15 der 53 Zeilen berührt, tut mehr als die Aufgabe
verlangt. Das ist kein Gate — es ist die Erwartung, gegen die du den Diff liest.

**P2 wird getrennt geprüft.** Du liest den Diff und hältst dein Urteil fest, bevor du die
Messung der KI siehst; die KI misst per Skript mit Kontrollfällen. P2 ist bestanden, wenn
beide ja sagen. Sagt einer nein, wird nicht gemergt. Sagen beide Verschiedenes, zählt der
Lauf nicht; die Abweichung wird als Befund zu P2 geführt, nicht als Klasse A bis F.

### Fehlerklassen, vorab benannt

| Klasse | Bedeutung |
|---|---|
| A — Schema-Ablehnung | Das Modell hat das Format nicht getroffen, einschließlich der Regeln von `replace_lines`: kein Treffer, mehrere Treffer, Überlappung. Werkzeug ok. |
| B — Hash-Ablehnung | Der Abschnitt oder die Zieldatei hat sich seit dem Anker bewegt. Werkzeug ok, Schutz greift. |
| C — Bilanz-Ablehnung | Erklärte und gemessene Zeilenzahl weichen ab. Werkzeug ok. |
| D — durchgelassen, aber falsch | `check` sagt ja, der Diff zeigt ungewollte Änderungen. **Werkzeuglücke.** |
| E — `verify` weicht ab | Zwischen Anwendung und Merge ist etwas passiert. **Kettenlücke.** |
| F — nackter Commit im `audit` | Ein Commit ohne Delta-Bezug hat das Merge-Tor passiert. Gehört gezählt und erklärt. |

**Zu Klasse A:** Dazu zählen auch ein Delta, das einen Ankerwert ändert (Abschnitt 2), und eine
Antwort, die kein gültiges JSON ist. Ein solches Delta wird nicht angewendet. Bei ungültigem
JSON endet `check` mit einem Absturz statt mit einer Ablehnung (Handbuch §6); an der Einordnung
ändert das nichts.

**Entscheidend:** A, B und C sind **keine Fehlschläge des Laufs**. Sie sind das Tor bei
der Arbeit. Der Lauf scheitert nur an D und E — wenn etwas Falsches durchkommt oder
etwas anderes im Repository landet als angesagt.

Ein Lauf, in dem alle drei Deltas abgelehnt werden, ist **kein Nichtergebnis**. Er sagt:
Die Kette hält, und das Schnüren durch fremde Modelle ist schwerer als gedacht. Das ist
mehr wert als ein Erfolg, den man sich zurechtgelegt hat.

Ob Lauf 3 als zweiter Lauf zählt, entscheiden die Definitionen „fehlerfrei", „unabhängig" und
„automatisch" zum Erfolgskriterium (Owner-Entscheid 2026-09-17, PBP-Instanz DELTA-FORCE).

Stand vor Lauf 3: Die Transportachse steht bei 1 von 2 (Lauf 1b). Lauf 2 zählt nicht (Klasse D,
kein Merge).

## 4 — Erklärte Abweichungen

Gegenüber Lauf 1b, dem gezählten Lauf, gelten die Abweichungen aus `AUSWERTUNG_Lauf2.md` §4
weiter. Gegenüber Lauf 2 kommen hinzu:

- **Gewollt** (Owner-Entscheide 2026-09-29 und -30):
  - Die Zielzeilenzahl 50 steht als Ankerwert im Auftrag. Die Modelle rechnen sie nicht mehr
    selbst (`VERSAND_Lauf-3.txt`, ANKER und vierte Regel).
  - Die vierte Regel verlangt auch die `delta_id` unverändert.
  - Klasse A umfasst geänderte Ankerwerte und ungültiges JSON (Abschnitt 3).
  - P2 wird getrennt geprüft (Abschnitt 3).
  - Das Handbuch nennt je Schritt eine Erwartung; beim Eingang werden die Ankerwerte jeder
    Datei abgeglichen; vor dem Versand misst Schritt 0 den Stand.
- **Aus Lauf 2 festgeschrieben** (dort im Lauf entschieden, übernommen 2026-09-30):
  Codeblock-Regel beim Sichern, Anwenden erst nach übereinstimmender Nachrechnung, Verfahren
  bei verfehltem P2 (Handbuch §3, 4.3, 4.5).
- **Unvermeidlich:** Anker (`<START>`, `base_sha`) und `delta_id` sind neu.
- **Unverändert:** Aufgabe (wortgleich) und Abschnitt (53 Zeilen, `context_hash` wie in Lauf 2),
  die drei Anbieter, das Werkzeug mit seinen bekannten Lücken (Handbuch §6), der Agent, der
  Wortlaut der Auswahlregel, das öffentliche Repository mit derselben Gegenmaßnahme.
- **Vorab präzisiert:** Klasse A, das Verfahren für P2 und die Einordnung, wenn Owner und
  Messung verschieden urteilen (Abschnitt 3).

---

*AUSWERTUNG_Lauf3.md | Auswertungsschlüssel Lauf 3 | Owner: Co-Creator | 2026-09-30*
