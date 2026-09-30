# Handbuch — Lauf 3 der Transportachse

*Operativ. Für einen Menschen geschrieben. Owner: Co-Creator · entworfen in PBP-S012, 2026-09-30*
*Repository: `andreasborchmann/DELTA` (öffentlich) · `<START>` = `4efdce9`*

*Versiegelt vor dem Versand, zusammen mit `VERSAND_Lauf-3.txt`. Auswahlregel, Testszenario und
Fehlerklassen stehen in `AUSWERTUNG_Lauf3.md` und werden hier nicht wiederholt.*

---

## 0 — Was gemessen wird, in einem Satz

Ob ein Änderungsauftrag, den ein fremdes Modell ohne Kenntnis der Anwendung schnürt, ohne
Nacharbeit durch die Kette läuft und so im Repository landet, wie `check` ihn freigegeben hat.

**Was nicht gemessen wird:** ob die Änderung inhaltlich klug ist. Das entscheidest du am Diff.

---

## 1 — Stand beim Versiegeln

| | |
|---|---|
| `<START>` | `4efdce9eec95ea82bd57e485e15e67aa608c89a0` (Merge von PR #10) |
| Zieldatei | `artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md` |
| Abschnitt | `### 2.1 Schicht-Architektur`, 53 Zeilen; nach der Änderung 50 |
| `context_hash` | `sha256:f34a74a4fcb5d59eaf1988087b10da0404b4b0c4610742f1df719ae5c78de8f1` |
| Werkzeug | `engine/deltakit.py`, sha256 `931cd7eb12dd46d413b8cc23cf5eb645707abfa4d52fcf8bc65824aff6d73b3c` |
| Auswertung | `AUSWERTUNG_Lauf3.md`, sha256 `865eaf5e29993ae6217870b2f1c17db8bdc07d85af893a6b7c036482e777ed70` |
| Auftragspaket | `VERSAND_Lauf-3.txt`, sha256 `39b8faec2da13898ca855e087368d672af055d939e55bc6bb453bdd308e3663e` |
| `delta_id` | `ULTRA-Δ-20260930-005` |
| Agent | Claude Code Web, Haiku 4.5 |
| Regel für `main` | Ruleset, leere Bypass-Liste, durchgesetzt (Dialog-Test, gemeldet 2026-09-29) |

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
- **R6** Das Repository bleibt öffentlich, bis Lauf 3 abgeschlossen ist. Sonst greift die Regel
  für `main` nicht mehr.
- **R7** In der Vorbereitung schreibst nur du. Im Lauf schreibt der Agent die Anwendung auf einen
  Branch, weil das Erfolgskriterium es so verlangt. Gemergt wird weiterhin von dir.
- **R8** Jeder Schritt in den Abschnitten 3 und 4 nennt eine Erwartung. Weicht eine Ausgabe davon
  ab, geht es erst weiter, wenn geklärt ist, warum. Maßgeblich ist die Ausgabe, nicht die Meldung,
  ein Schritt sei erledigt.

---

## 3 — Versand

0. **Vor dem Versand** (Steuerungs-Chat, eigener Klon, nur lesend).
   *Erwartung:* `main` ist der Merge-Commit der Versiegelung; `<START>` ist Vorfahre von
   `main`; unter `artefakte/` gibt es seit `<START>` keinen Commit; `hash` auf §2.1 an `main`
   ergibt den `context_hash` aus Abschnitt 1 bei 53 Zeilen; eine `check`-Probe mit `base_sha`
   `<START>` besteht, eine mit gekipptem `context_hash` wird abgelehnt.
   `AUSWERTUNG_Lauf3.md` und `VERSAND_Lauf-3.txt` an `main` haben die sha256 aus Abschnitt 1;
   Teil B ergibt nachgerechnet den `context_hash` (R5); die Zieldatei hat keine
   Windows-Zeilenenden.
   Dazu du: Dialog-Test auf `main` mit einer echten Änderung, dann abbrechen.
   *Erwartung:* Der Dialog bietet nur „neuen Branch anlegen" an.
1. Drei frische Chats: ChatGPT, Grok, Qwen. In jedem vorher Websuche und chatübergreifendes
   Gedächtnis ausschalten oder einen temporären bzw. privaten Chat nutzen. Was der Anbieter
   dafür anbietet, prüfst du vorher; geht es bei einem nicht, notierst du das.
2. In jeden Chat den vollständigen Inhalt von `VERSAND_Lauf-3.txt` einfügen, sonst nichts.
   Nichts aus Lauf 1a, 1b oder 2 erwähnen.
3. Rückfragen zum Abschnitt sind erlaubt. Rückfragen zur Anwendung nicht beantworten, sonst ist
   der Auftrag nicht mehr blind gegenüber der Anwendung.
4. Antworten roh sichern als `chatgpt-lauf3.json`, `grok-lauf3.json`, `qwen-lauf3.json`:
   speichern, keinen Formatierbefehl ausführen, nichts reparieren, nichts kürzen. Besteht eine
   Antwort nur aus einem Codeblock, zählt sein Inhalt; steht Text davor oder danach, wird die
   ganze Antwort unverändert gesichert (aus Lauf 2, Owner-Entscheid 2026-09-28). Ein Modell,
   das ungültiges JSON liefert, hat ein ungültiges Delta geliefert — das ist ein Messwert.
5. Enthält eine Antwort Quellenangaben oder Links, notierst du das: Dann hat das Modell gesucht.

---

## 4 — Eingang, Prüfung, Anwendung

**4.1 Eingang** (du, Browser). Die drei Dateien über „Add file" → „Upload files" nach
`deltas/eingang/`, neuer Branch, Pull Request, „Create a merge commit".
Commit message: `Lauf 3: drei Deltas eingegangen`.
*Erwartung:* `main` ist ein neuer Merge-Commit. Unter `deltas/eingang/` liegen drei neue
Dateien, bytegleich mit deinen gesicherten Rohausgaben; unter `artefakte/` hat sich nichts
geändert.

**4.2 Ankerabgleich** (Steuerungs-Chat, eigener Klon, nur lesend), für jede der drei Dateien,
bevor das Werkzeug sie prüft.
*Erwartung:* gültiges JSON; `delta_id` = `ULTRA-Δ-20260930-005`; `target.document`,
`target.section_heading`, `target.base_sha` und `target.context_hash` wie im ANKER von
`VERSAND_Lauf-3.txt`; `meta.expected_lines` = `{"before": 53, "after": 50}`. Weicht ein Wert
ab oder ist die Datei kein gültiges JSON, ist das Delta Klasse A und wird nicht angewendet
(`AUSWERTUNG_Lauf3.md` §3).

**4.3 Prüfen** (Claude Code Web, neue Sitzung nach dem Eingang):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts, repariere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
sha256sum engine/deltakit.py
python3 engine/deltakit.py check deltas/eingang/chatgpt-lauf3.json --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/grok-lauf3.json --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/qwen-lauf3.json --repo . ; echo "exit $?"
```

*Erwartung:* `HEAD` und `origin/main` sind beide der Merge-Commit aus 4.1; sonst prüft die
Sitzung den alten Stand, wie beim ersten Versuch in Lauf 2. `sha256sum` ergibt den
Werkzeug-Hash aus Abschnitt 1. Jede Prüfung endet mit exit 0 (anwendbar) oder exit 2
(abgelehnt).
- exit 1 ist ein Absturz. Ist die Datei kein gültiges JSON oder hat ein Feld den falschen Typ,
  ist das Klasse A. Fehlt die Datei, stimmt der Stand nicht: zurück zu 4.1.
- Lehnt `check` wegen des `context_hash` ab, stehen beide Werte gekürzt im Text; die vollen
  Werte vergleichst du mit `hash`.

Die ganze Seite kopieren (R5). Der Steuerungs-Chat rechnet `check` auf dem eigenen Klon nach;
angewendet wird erst, wenn beide Rechnungen übereinstimmen (aus Lauf 2, Owner-Entscheid
2026-09-28). Bis dein Urteil zu P2 schriftlich vorliegt (§5), meldet der Steuerungs-Chat nur
Exit-Codes, Zeilenbilanz und die sha256 der vorausberechneten Datei — keinen Diff, keinen
Abschnittstext, keine Einschätzung zu den drei Aussagen. Angewendet wird nach der Auswahlregel
in `AUSWERTUNG_Lauf3.md`, unter den Deltas, die 4.2 bestanden haben. Besteht keines, endet der
Lauf hier — als Ergebnis, nicht als Abbruch.

**4.4 Anwenden** (Claude Code Web, dieselbe Sitzung). `<x>` steht für das gewählte Delta,
zum Beispiel `qwen-lauf3`:

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe. Keine Zusammenfassung.
python3 engine/deltakit.py pr-body deltas/eingang/<x>.json --repo . ; echo "exit $?"
git checkout -b delta/20260930-005
python3 engine/deltakit.py render deltas/eingang/<x>.json --repo . --write
git add artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md
git commit -m "ULTRA-Δ-20260930-005 (<x>.json): Anwendung Lauf 3"
git push -u origin delta/20260930-005
git show --stat HEAD
Nicht nach main pushen, nichts mergen.
```

*Erwartung:* `pr-body` endet mit exit 0; es läuft vor `render`, danach lehnt es ab.
`git show --stat` zeigt genau eine geänderte Datei, die Zieldatei. Der Abschnitt hat danach
50 Zeilen, und die Datei hat die sha256, die der Steuerungs-Chat vorher aus dem gewählten
Delta berechnet hat.

**4.5 Pull Request** (du, Browser). Nach dem Push „Compare & pull request", als Beschreibung
die Ausgabe von `pr-body`. Dann P2 nach Abschnitt 5; nur wenn P2 besteht: „Create a merge
commit".
*Erwartung:* Die Beschreibung beginnt mit `## ULTRA-Δ-20260930-005`.
Besteht P2 nicht: nicht mergen, den Pull Request schließen und den Branch als Beleg stehen
lassen. Nachgeprüft wird dann im Steuerungs-Chat auf dem eigenen Klon, wie in Lauf 2: den
Branch mit ausdrücklicher Ref-Zuordnung holen, dann
`verify … --head origin/delta/20260930-005` und
`audit … --start 4efdce9eec95ea82bd57e485e15e67aa608c89a0 --head origin/delta/20260930-005`
(Owner-Entscheide 2026-09-29). *Erwartung:* `verify` exit 0; `audit` ein Commit mit
Delta-Bezug, exit 0. `verify` ohne `--head` prüft `main` und meldet dort zwingend eine
Abweichung — das ist keine Klasse E.

**4.6 Nachprüfen** (Claude Code Web, neue Sitzung nach dem Merge):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
python3 engine/deltakit.py verify deltas/eingang/<x>.json --repo . ; echo "exit $?"
python3 engine/deltakit.py audit --repo . --start 4efdce9eec95ea82bd57e485e15e67aa608c89a0 --head HEAD ; echo "exit $?"
```

*Erwartung:* `HEAD` und `origin/main` sind der Merge-Commit aus 4.5. `verify` endet mit exit 0
(„byte-identisch"). `audit` meldet genau einen Commit auf Artefakten, mit Delta-Bezug, exit 0.

P3 und P4 nach `AUSWERTUNG_Lauf3.md`. Solange das Repository öffentlich ist, rechne ich `check`,
`verify` und `audit` auf einem eigenen Klon nach.

---

## 5 — P2: Erwartung, Lesart und Verfahren

Zeilennummern im Abschnitt, Überschrift = Zeile 1:

| Aussage | betroffene Zeilen |
|---|---|
| 1 — Notiz entfällt | 2 bis 5: die Notiz und die Leerzeilen zwischen Überschrift und Code-Block |
| 2 — drei neue Vermerke | 23 und 24; 33 und 34 werden zu einer Zeile |
| 3 — neuer letzter Eintrag | eine neue Zeile nach Zeile 48 |

**Referenzumsetzung** (gebaut in PBP-S010, mit `check` am Anker geprüft): 53 → 50 Zeilen,
7 Zeilen geändert oder entfernt, 4 eingefügt, rund 15 Zeilen im Auftrag. Das ist eine
Erwartung, kein Gate. Sie gilt für Lauf 3 unverändert, weil der Abschnitt derselbe ist.

**„Nichts sonst" heißt:** Außerhalb der betroffenen Zeilen ändert sich keine Zeile. Innerhalb ist
die Form frei, solange die Aussage zutrifft — zum Beispiel, ob der Pfeil `←` vor einem Vermerk
stehen bleibt oder wie der neue Eintrag eingerückt ist.

**Verfahren** (Owner-Entscheid 2026-09-29):
1. Du liest den Diff im Pull Request und hältst dein Urteil schriftlich fest — je Aussage ja
   oder nein, dazu „nichts sonst" ja oder nein —, bevor du die Messung siehst.
2. Der Steuerungs-Chat misst P2 per Skript, mit Kontrollfällen, die aus dem richtigen Grund
   bestehen oder scheitern, und legt das Ergebnis erst danach vor.
3. Gemergt wird nur, wenn beide ja sagen. Sagen sie Verschiedenes, wird nicht gemergt; die
   Abweichung ist ein Befund.

---

## 6 — Bekannte Werkzeuglücken in diesem Lauf

Das Werkzeug bleibt für Lauf 3 unverändert; behoben wird nach Lauf 3, in einer neuen Fassung
(Owner-Entscheide 2026-09-29 und -30). Gegenmaßnahmen in diesem Lauf:

| Lücke | Gegenmaßnahme |
|---|---|
| W-1 — fehlende Delta-Datei: Absturz mit exit 1 statt 3 | Erwartung in 4.3: `HEAD` = Eingang |
| W-2 — Ablehnungstext kürzt beide Hashes gleich | volle Werte mit `hash` vergleichen (4.3) |
| W-3 — Zielzahl aus der Selbstauskunft | Zielzahl 50 als Ankerwert, Ankerabgleich in 4.2 |
| W-4 — veralteter Befundtext von `audit` | fester Text; die Regel für `main` greift |
| W-5 — `hash` mit absolutem Pfad: Absturz | nur relative Pfade |
| 1b-4 — ungültiges JSON, falscher Feldtyp: Absturz | zählt als Klasse A (4.2, 4.3) |
| 1b-4 auch in `audit`: Eine Eingangsdatei mit gültigem JSON, aber falscher Struktur bricht `audit` ab (exit 1) | P4 misst dann der Steuerungs-Chat mit `git log 4efdce9eec95ea82bd57e485e15e67aa608c89a0..HEAD -- artefakte`; ein Befund zum Werkzeug, keine Klasse E |
| 1b-5 — `verify` gleicht Zeilenenden an | folgenlos: Zieldatei ohne Windows-Zeilenenden |
| 1b-6 — `audit` liest nur den Betreff | R4: jeder Merge als Merge-Commit |
| 1b-7 — eine `delta_id` für drei Aufträge | Dateiname im Commit-Betreff (4.4) |
| 1b-9 — `pr-body` nur vor `render` | Reihenfolge in 4.4 |

---

## 7 — Was in diesem Handbuch ungeprüft ist

- Ob ChatGPT, Grok und Qwen Websuche und Gedächtnis abschalten lassen.
- Ob die Chatfenster beim Einfügen Leerzeichen oder Zeilen verändern. Das war in 1b und 2
  genauso wenig messbar.
- Ob die Modelle die Zielzahl aus dem Anker übernehmen. Die vorgegebenen Ankerwerte haben in
  Lauf 1b und Lauf 2 alle sechs Antworten übernommen; die Zielzahl steht zum ersten Mal darin.

---

*HANDBUCH_Lauf-3-Transportachse.md | Operative Referenz | Owner: Co-Creator | 2026-09-30*
