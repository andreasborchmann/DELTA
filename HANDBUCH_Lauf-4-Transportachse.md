# Handbuch — Lauf 4 der Transportachse

*Operativ. Für einen Menschen geschrieben. Owner: Co-Creator · entworfen in PBP-S014, 2026-10-07*
*Repository: `andreasborchmann/DELTA` (öffentlich) · `<START>` = `50288ea`*

*Versiegelt vor dem Versand, zusammen mit `VERSAND_Lauf-4.txt`. Auswahlregel, Testszenario und
Fehlerklassen stehen in `AUSWERTUNG_Lauf4.md` und werden hier nicht wiederholt.*

---

## 0 — Was gemessen wird, in einem Satz

Ob ein Änderungsauftrag, den ein fremdes Modell ohne Kenntnis der Anwendung gegen einen
vorgegebenen Zieltext schnürt, ohne Nacharbeit durch die Kette läuft und so im Repository landet,
wie `check` ihn freigegeben hat.

**Was nicht gemessen wird:** ob das Modell die Aufgabe versteht — der Zieltext nimmt sie ihm ab
(PBP-ART-050). Ob der Zieltext die Aufgabe trifft, entscheidest du beim Versiegeln (P2, Abschnitt 5).

---

## 1 — Stand beim Versiegeln

| | |
|---|---|
| `<START>` | `50288ea8c5a711a4beebea353cbf45214a110986` (Merge des Pull Requests mit Auswertung und Zieltext) |
| Zieldatei | `artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md` |
| Abschnitt | `### 2.1 Schicht-Architektur`, 53 Zeilen; nach der Änderung 50 |
| `context_hash` | `sha256:f34a74a4fcb5d59eaf1988087b10da0404b4b0c4610742f1df719ae5c78de8f1` |
| Zieltext | `ZIELTEXT_Lauf4.md`, sha256 `ce48daaa1a7fc198a6ed913469b701f870def61ae67d4fd8d5dfc04d43087f70`; Abschnitt danach `sha256:9da6be7ddd7ee3d6b75aa2aa761a09622fbbe423103621f80714a5db8f96545b`, 50 Zeilen |
| Werkzeug | `engine/deltakit.py`, sha256 `77759f9fbd4906b79b0c054dc9d9d9e92a54f573f945257557adef3db39b588f`, Fassung S014 |
| Kontrollfälle | `engine/kontrollfaelle.json`, sha256 `8abdc339973cd807c9f3b99aeb677389b2ad170c4b0f39d8578e46f897b6f2a9` |
| Auswertung | `AUSWERTUNG_Lauf4.md`, sha256 `f8346188d0862cc9896eaefc1ee1ececa6a9993a2b9962d0c1d18acb867a15a0` |
| Auftragspaket | `VERSAND_Lauf-4.txt`, sha256 `fb71137623c44f7ef08226f0c17287db2d6aff02386ecf0f01c79479972d4f3e` |
| `delta_id` | `ULTRA-Δ-20261009-006` |
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
  `context_hash` ergeben, beim Zieltext im Auftragspaket dessen Abschnitts-Hash aus Abschnitt 1.
- **R6** Das Repository bleibt öffentlich, bis Lauf 4 abgeschlossen ist. Sonst greift die Regel
  für `main` nicht mehr.
- **R7** In der Vorbereitung schreibst nur du. Im Lauf schreibt der Agent die Anwendung auf einen
  Branch, weil das Erfolgskriterium es so verlangt. Gemergt wird weiterhin von dir.
- **R8** Jeder Schritt in den Abschnitten 3 und 4 nennt eine Erwartung. Weicht eine Ausgabe davon
  ab, geht es erst weiter, wenn geklärt ist, warum. Maßgeblich ist die Ausgabe, nicht die Meldung,
  ein Schritt sei erledigt.
- **R9** Vor jedem Merge misst der Steuerungs-Chat den offenen Pull Request und den Test-Merge;
  gemergt wird erst nach seiner Meldung.
- **R10** Dateien zum Hochladen kommen allein in einer Antwort des Steuerungs-Chats; du prüfst ihre
  Namen vor dem Commit.
- **R11** Die Commit-Zeile steht allein in einem Kasten und wird nur von dort übernommen.
- **R12** Vor dem Einfügen in einen Chat prüfst du das Prüfmerkmal der versiegelten Fassung: Zeile 8
  nennt den vollen `<START>`, und der Text enthält kein `⟨`.

---

## 3 — Versand

0. **Vor dem Versand** (Steuerungs-Chat, eigener Klon, nur lesend).
   *Erwartung:* `main` ist der Merge-Commit der Versiegelung; `<START>` ist Vorfahre von
   `main`; unter `artefakte/` gibt es seit `<START>` keinen Commit; `hash` auf §2.1 an `main`
   ergibt den `context_hash` aus Abschnitt 1 bei 53 Zeilen; eine `check`-Probe mit `base_sha`
   `<START>` besteht, eine mit gekipptem `context_hash` wird abgelehnt.
   `AUSWERTUNG_Lauf4.md`, `ZIELTEXT_Lauf4.md` und `VERSAND_Lauf-4.txt` an `main` haben die sha256
   aus Abschnitt 1; Teil B und der Zieltext im Auftragspaket ergeben nachgerechnet ihre Hashes
   (R5); die Zieldatei hat keine Windows-Zeilenenden.
   Dazu du: Dialog-Test auf `main` mit einer echten Änderung, dann abbrechen.
   *Erwartung:* Der Dialog bietet nur „neuen Branch anlegen" an.
1. Drei frische Chats: ChatGPT, Grok, Qwen. In jedem vorher Websuche und chatübergreifendes
   Gedächtnis ausschalten oder einen temporären bzw. privaten Chat nutzen. Was der Anbieter
   dafür anbietet, prüfst du vorher; geht es bei einem nicht, notierst du das.
2. In jeden Chat den vollständigen Inhalt von `VERSAND_Lauf-4.txt` einfügen, sonst nichts; vorher
   das Prüfmerkmal nach R12. Nichts aus Lauf 1a, 1b, 2 oder 3 erwähnen.
3. Rückfragen zum Abschnitt sind erlaubt. Rückfragen zur Anwendung nicht beantworten, sonst ist
   der Auftrag nicht mehr blind gegenüber der Anwendung.
4. Antworten roh sichern als `chatgpt-lauf4.json`, `grok-lauf4.json`, `qwen-lauf4.json`:
   speichern, keinen Formatierbefehl ausführen, nichts reparieren, nichts kürzen. Besteht eine
   Antwort nur aus einem Codeblock, zählt sein Inhalt; gesichert wird über den Kopier-Knopf des
   Codeblocks. Sonst wird die ganze Antwort unverändert gesichert, über den Kopier-Knopf der
   Antwort, und du notierst das (Codeblock-Regel aus Lauf 2, Owner-Entscheid 2026-09-28;
   Kopierweg aus Lauf 3, Owner-Entscheid 2026-10-07). Ein Modell, das ungültiges JSON liefert,
   hat ein ungültiges Delta geliefert — das ist ein Messwert.
5. Enthält eine Antwort Quellenangaben oder Links, notierst du das: Dann hat das Modell gesucht.

---

## 4 — Eingang, Prüfung, Anwendung

**4.1 Eingang** (du, Browser). Die drei Dateien über „Add file" → „Upload files" nach
`deltas/eingang/`, neuer Branch, Pull Request; gemergt wird nach der Messung (R9), mit „Create a
merge commit". Commit message, aus dem Kasten (R11): `Lauf 4: drei Deltas eingegangen`.
*Erwartung:* `main` ist ein neuer Merge-Commit. Unter `deltas/eingang/` liegen drei neue
Dateien, bytegleich mit deinen gesicherten Rohausgaben; unter `artefakte/` hat sich nichts
geändert.

**4.2 Ankerabgleich** (Steuerungs-Chat, eigener Klon, nur lesend), für jede der drei Dateien,
bevor das Werkzeug sie prüft.
*Erwartung:* gültiges JSON; `delta_id` = `ULTRA-Δ-20261009-006`; `target.document`,
`target.section_heading`, `target.base_sha` und `target.context_hash` wie im ANKER von
`VERSAND_Lauf-4.txt`; `meta.expected_lines` = `{"before": 53, "after": 50}`. Weicht ein Wert
ab oder ist die Datei kein gültiges JSON, ist das Delta Klasse A und wird nicht angewendet
(`AUSWERTUNG_Lauf4.md` §3).

**4.3 Prüfen** (Claude Code Web, neue Sitzung nach dem Eingang):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts, repariere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
sha256sum engine/deltakit.py ZIELTEXT_Lauf4.md
python3 engine/deltakit.py check deltas/eingang/chatgpt-lauf4.json --zieltext ZIELTEXT_Lauf4.md --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/grok-lauf4.json --zieltext ZIELTEXT_Lauf4.md --repo . ; echo "exit $?"
python3 engine/deltakit.py check deltas/eingang/qwen-lauf4.json --zieltext ZIELTEXT_Lauf4.md --repo . ; echo "exit $?"
```

*Erwartung:* `HEAD` und `origin/main` sind beide der Merge-Commit aus 4.1; sonst prüft die
Sitzung den alten Stand, wie beim ersten Versuch in Lauf 2. `sha256sum` ergibt die Hashes von
Werkzeug und Zieltext aus Abschnitt 1. Jede Prüfung endet mit exit 0 (anwendbar, Inhalt gleich
dem Zieltext) oder exit 2 (abgelehnt).
- exit 3 ist ein Bedienfehler. Fehlt eine Datei, stimmt der Stand nicht: zurück zu 4.1. Einen
  Absturz mit exit 1 kennt die Fassung S014 nicht mehr; träte er auf, ist das ein Befund zum
  Werkzeug.
- Lehnt `check` ab, nennt es jeden Grund mit vollen Werten; weicht der Inhalt ab, zeigt es bis zu
  20 Zeilen Unterschied. Eingeordnet wird nach `AUSWERTUNG_Lauf4.md` §3 (A, B, C, G).

Die ganze Seite kopieren (R5). Der Steuerungs-Chat rechnet `check` auf dem eigenen Klon nach und
dazu den Abschnitt nach dem gewählten Delta ohne das Werkzeug; angewendet wird erst, wenn alle
Rechnungen übereinstimmen (aus Lauf 2, Owner-Entscheid 2026-09-28; die Rechnung ohne Werkzeug
seit P2 beim Versiegeln, Owner-Entscheid 2026-10-07). Angewendet wird nach der Auswahlregel in
`AUSWERTUNG_Lauf4.md`, unter den Deltas, die 4.2 bestanden haben. Besteht keines, endet der Lauf
hier — als Ergebnis, nicht als Abbruch.

**4.4 Anwenden** (Claude Code Web, dieselbe Sitzung). `<x>` steht für das gewählte Delta,
zum Beispiel `qwen-lauf4`:

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe. Keine Zusammenfassung.
python3 engine/deltakit.py pr-body deltas/eingang/<x>.json --zieltext ZIELTEXT_Lauf4.md --repo . ; echo "exit $?"
git checkout -b delta/20261009-006
python3 engine/deltakit.py render deltas/eingang/<x>.json --zieltext ZIELTEXT_Lauf4.md --repo . --write
git add artefakte/TESTGEGENSTAND_TRANSPORTACHSE_01.md
git commit -m "ULTRA-Δ-20261009-006 (<x>.json): Anwendung Lauf 4"
git push -u origin delta/20261009-006
git show --stat HEAD
Nicht nach main pushen, nichts mergen.
```

*Erwartung:* `pr-body` endet mit exit 0. `git show --stat` zeigt genau eine geänderte Datei, die
Zieldatei. Der Abschnitt hat danach 50 Zeilen und gleicht dem Zieltext, und die Datei hat die
sha256, die der Steuerungs-Chat vorher aus dem gewählten Delta berechnet hat.

**4.5 Pull Request** (du, Browser). Nach dem Push „Compare & pull request", als Beschreibung
die Ausgabe von `pr-body`. Vor dem Merge misst der Steuerungs-Chat den Pull Request und den
Test-Merge (R9); erst nach seiner Meldung „Create a merge commit".
*Erwartung:* Die Beschreibung beginnt mit `## ULTRA-Δ-20261009-006`; „Files changed" zeigt
genau die Zieldatei.
Meldet die Messung eine Abweichung: nicht mergen, den Pull Request schließen und den Branch als
Beleg stehen lassen. Nachgeprüft wird dann im Steuerungs-Chat auf dem eigenen Klon, wie in Lauf 2:
den Branch mit ausdrücklicher Ref-Zuordnung holen, dann
`verify … --head origin/delta/20261009-006` und
`audit … --start 50288ea8c5a711a4beebea353cbf45214a110986 --head origin/delta/20261009-006`
(Owner-Entscheide 2026-09-29). *Erwartung:* `verify` exit 0; `audit` ein Commit mit
Delta-Bezug, exit 0. `verify` ohne `--head` prüft `main` und meldet dort zwingend eine
Abweichung — das ist keine Klasse E.

**4.6 Nachprüfen** (Claude Code Web, neue Sitzung nach dem Merge):

```
Führe nacheinander aus und zeige mir jeweils die vollständige Ausgabe einschließlich Exit-Code.
Ändere nichts. Keine Zusammenfassung, keine Wiederholung der Ausgaben.
git fetch origin && git rev-parse HEAD origin/main
python3 engine/deltakit.py verify deltas/eingang/<x>.json --repo . ; echo "exit $?"
python3 engine/deltakit.py audit --repo . --start 50288ea8c5a711a4beebea353cbf45214a110986 --head HEAD ; echo "exit $?"
```

*Erwartung:* `HEAD` und `origin/main` sind der Merge-Commit aus 4.5. `verify` endet mit exit 0
(„byte-identisch"). `audit` meldet genau einen Commit auf Artefakten, mit Delta-Bezug, exit 0.
Eingangsdateien, die kein gültiges JSON sind, nennt es als übersprungen, etwa `chatgpt-lauf3.json`.

P3 und P4 nach `AUSWERTUNG_Lauf4.md`. Solange das Repository öffentlich ist, rechne ich `check`,
`verify` und `audit` auf einem eigenen Klon nach.

---

## 5 — P2 beim Versiegeln: Erwartung, Lesart und Verfahren

P2 prüft den Zieltext, nicht ein Delta. Die drei Aussagen stehen ausgeschrieben in
`AUSWERTUNG_Lauf4.md` §3 (Quelle: `VERSAND_Lauf-3.txt`, AUFGABE).
Zeilennummern im Abschnitt, wie er jetzt ist, Überschrift = Zeile 1:

| Aussage | betroffene Zeilen |
|---|---|
| 1 — Notiz entfällt | 2 bis 5: die Notiz und die Leerzeilen zwischen Überschrift und Code-Block |
| 2 — drei neue Vermerke | 23 und 24; 33 und 34 werden zu einer Zeile |
| 3 — neuer letzter Eintrag | eine neue Zeile nach Zeile 48 |

**Der Zieltext** ist die Referenzumsetzung aus PBP-S010 (Handbuch Lauf 3 §5): 53 → 50 Zeilen,
7 Zeilen geändert oder entfernt, 4 eingefügt.

**„Nichts sonst" heißt:** Außerhalb der betroffenen Zeilen ändert sich keine Zeile.

**Verfahren** (Owner-Entscheid 2026-10-07, nach dem Verfahren aus Lauf 3 vom 2026-09-29):
1. Du liest den Zieltext — am einfachsten das Diff vom Abschnitt jetzt zum Zieltext — und hältst
   dein Urteil schriftlich fest: je Aussage ja oder nein, dazu „nichts sonst" ja oder nein.
2. Der Steuerungs-Chat misst P2 per Skript mit den Prüfern aus S013 und mit Kontrollfällen, die
   aus dem richtigen Grund bestehen oder scheitern, und legt das Ergebnis erst danach vor.
3. Versiegelt wird nur, wenn beide ja sagen. Sagen sie Verschiedenes, wird nicht versiegelt; die
   Abweichung ist ein Befund.

---

## 6 — Werkzeug in diesem Lauf

`engine/deltakit.py` in der Fassung S014 behebt die Lücken W-1 bis W-5, 1b-4, 1b-5 und 1b-9 und
bringt die Inhaltsprüfung; `selftest` prüft die Leseseite und die Kontrollfälle aus
`engine/kontrollfaelle.json` (PBP-S014). Zwei Punkte bleiben Verfahrensregeln ohne Umbau:

| Lücke | Gegenmaßnahme |
|---|---|
| 1b-6 — `audit` liest nur den Betreff | R4: jeder Merge als Merge-Commit |
| 1b-7 — eine `delta_id` für drei Aufträge | Dateiname im Commit-Betreff (4.4) |

---

## 7 — Was in diesem Handbuch ungeprüft ist

- Ob ChatGPT, Grok und Qwen Websuche und Gedächtnis abschalten lassen.
- Ob die Chatfenster beim Einfügen Leerzeichen oder Zeilen verändern. Das war in 1b und 2
  genauso wenig messbar.
- Ob die Modelle die Antwort in einem Codeblock geben und ob der Kopier-Knopf des Codeblocks den
  Text unverändert liefert; woher die 44 Escape-Folgen in `chatgpt-lauf3.json` kommen, ist offen.
- Ob die Modelle den Zieltext Zeichen für Zeichen übernehmen.

---

*HANDBUCH_Lauf-4-Transportachse.md | Operative Referenz | Owner: Co-Creator | 2026-10-07*
