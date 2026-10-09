# Auswertung Lauf 4 — Transportachse

*Versiegelt vor dem Versand: gilt ab dem Merge dieser Datei auf `main` und wird danach nicht mehr geändert.
Owner: Co-Creator · entworfen in PBP-S014, 2026-10-07*

---

## 1 — Auswahlregel

Angewendet wird das erste Delta in der Reihenfolge ChatGPT, Grok, Qwen,
das deltakit check ohne Handkorrektur besteht. Bestehen alle drei, gilt
ChatGPT. Besteht keines, wird keines angewendet.

Wortgleich mit `AUSWERTUNG_Lauf1.md` (`47bc2c2`), `AUSWERTUNG_Lauf2.md` (`0221334`) und
`AUSWERTUNG_Lauf3.md` (`47e944e`).

## 2 — Begriffe

**Versiegelt** heißt für Lauf 4: vor dem Versand auf `main` gemergt. Das gilt für diese Datei,
für den Zieltext `ZIELTEXT_Lauf4.md`, für `HANDBUCH_Lauf-4-Transportachse.md` und für das
Auftragspaket `VERSAND_Lauf-4.txt`.

**`<START>`** ist der `base_sha` des versandten Ankers, also der Commit, auf dem der Anker
gezogen wurde. Er steht in jeder Delta-Datei dieses Laufs.

**Ankerwerte** sind die Werte im ANKER-Block von `VERSAND_Lauf-4.txt` — `document`,
`section_heading`, `base_sha`, `context_hash`, `expected_lines.before` und
`expected_lines.after` — und die `delta_id` aus dem Ausgabeformat des Pakets. Ein Delta übernimmt
sie unverändert.

**Zieltext** ist der Inhalt von `ZIELTEXT_Lauf4.md`: der Abschnitt, wie er nach der Änderung
aussehen soll, Zeichen für Zeichen, mit Überschrift. Er steht wortgleich im Auftragspaket.
`check` vergleicht ihn mit dem Abschnitt nach dem Delta (`--zieltext ZIELTEXT_Lauf4.md`).

## 3 — Testszenario

Vier Prüfungen. P2 wird beim Versiegeln geprüft, die übrigen im Lauf, in dieser Reihenfolge. Jede
hat genau ein Ergebnis.

| # | Prüfung | Bestanden wenn |
|---|---|---|
| P1 | `check` mit `--zieltext ZIELTEXT_Lauf4.md` auf dem gewählten Delta | Exit 0, ohne dass jemand die Datei angefasst hat |
| P2 | Zieltext, beim Versiegeln | erfüllt die drei Aussagen (unten in diesem Abschnitt) und **nichts sonst** |
| P3 | `verify` nach dem Merge | Exit 0, Byte für Byte |
| P4 | `audit` von `<START>` (exklusiv) bis `HEAD` | kein Commit auf `artefakte/` ohne Delta-Bezug |

**P2 wird beim Versiegeln getrennt geprüft.** Du liest den Zieltext gegen die drei Aussagen und
hältst dein Urteil fest, bevor du die Messung der KI siehst; die KI misst per Skript mit
Kontrollfällen. P2 ist bestanden, wenn beide ja sagen. Sagt einer nein oder sagen beide
Verschiedenes, wird nicht versiegelt; die Abweichung ist ein Befund.

**Die drei Aussagen** (aus `VERSAND_Lauf-3.txt`, AUFGABE — hier ausgeschrieben, damit sie beim
Versiegeln ohne den Vorlauf vorliegen):

1. Die kursive Notiz am Abschnittsanfang zum verworfenen Delta `ULTRA-Δ-20260912-001` entfällt
   vollständig; zwischen Überschrift und Code-Block steht danach genau eine Leerzeile.
2. Unter „SCHICHT 2" tragen drei Einträge neue Vermerke:
   `ULTRA_PROTOCOL_SYS_DELTA_1_1.md`: „§2.2 und Z.134 korrekturbedürftig, s. Sektion 1";
   `ULTRA_REF_SYS_DELTA_ENGINE_1_0.md`: „Schreibseite aufgegeben, s. PBP-ART-014";
   `ULTRA_ARCH_SYS_DELTA-FORCE-SUBSTRAT_0_1.md`: „[Entwurf — §6 überholt, s. PBP-ART-014]",
   und zwar auf einer einzigen Zeile.
3. Unter „SCHICHT 3" steht als letzter Eintrag:
   `Rohausgaben Lauf 1a: ChatGPT.json · Grok.json · Qwen.json`

**Im Lauf** deckt P1 den Inhalt ab und P3 die angewendeten Bytes. Zusätzlich rechnet der
Steuerungs-Chat den Abschnitt nach dem gewählten Delta ohne das Werkzeug nach und vergleicht ihn
mit dem Zieltext.

### Fehlerklassen, vorab benannt

| Klasse | Bedeutung |
|---|---|
| A — Schema-Ablehnung | Das Modell hat das Format nicht getroffen, einschließlich der Regeln von `replace_lines`: kein Treffer, mehrere Treffer, Überlappung. Werkzeug ok. |
| B — Hash-Ablehnung | Der Abschnitt oder die Zieldatei hat sich seit dem Anker bewegt. Werkzeug ok, Schutz greift. |
| C — Bilanz-Ablehnung | Erklärte und gemessene Zeilenzahl weichen ab. Werkzeug ok. |
| D — durchgelassen, aber falsch | `check` sagt ja, der Diff zeigt ungewollte Änderungen. **Werkzeuglücke.** |
| E — `verify` weicht ab | Zwischen Anwendung und Merge ist etwas passiert. **Kettenlücke.** |
| F — nackter Commit im `audit` | Ein Commit ohne Delta-Bezug hat das Merge-Tor passiert. Gehört gezählt und erklärt. |
| G — Inhalts-Ablehnung | Die Zeilenbilanz stimmt, aber der Abschnitt nach dem Delta gleicht nicht dem Zieltext. Werkzeug ok. |

**Zu Klasse A:** Dazu zählen auch ein Delta, das einen Ankerwert ändert (Abschnitt 2), und eine
Antwort, die kein gültiges JSON ist. Ein solches Delta wird nicht angewendet. Ungültiges JSON
lehnt `check` seit der Fassung S014 mit exit 2 ab; in Lauf 3 brach es mit einem Absturz ab.

**Zu Klasse D:** Mit vorgegebenem Zieltext heißt D: Der Zieltext verfehlt die Aufgabe — dann war
P2 falsch — oder das Werkzeug vergleicht falsch.

**Zu Klasse G:** Weil der Zieltext 50 Zeilen hat, ist jedes Delta der Klasse C auch inhaltlich
falsch. G trennt davon die Deltas, die die Zielzahl treffen und trotzdem nicht den Zieltext.
Nennt `check` mehrere Gründe, zählt die erste Klasse in der Reihenfolge A, B, C, G.

**Entscheidend:** A, B, C und G sind **keine Fehlschläge des Laufs**. Sie sind das Tor bei
der Arbeit. Der Lauf scheitert nur an D und E — wenn etwas Falsches durchkommt oder
etwas anderes im Repository landet als angesagt.

Ein Lauf, in dem alle drei Deltas abgelehnt werden, ist **kein Nichtergebnis**. Er sagt:
Die Kette hält, und das Schnüren durch fremde Modelle ist schwerer als gedacht. Das ist
mehr wert als ein Erfolg, den man sich zurechtgelegt hat.

Ob Lauf 4 als zweiter Lauf zählt, entscheiden die Definitionen „fehlerfrei", „unabhängig" und
„automatisch" zum Erfolgskriterium (Owner-Entscheid 2026-09-17, PBP-Instanz DELTA-FORCE).

Stand vor Lauf 4: Die Transportachse steht bei 1 von 2 (Lauf 1b). Lauf 2 zählt nicht (Klasse D,
kein Merge), Lauf 3 zählt nicht (A, C, C — nichts angewendet).

## 4 — Erklärte Abweichungen

Gegenüber Lauf 1b, dem gezählten Lauf, gelten die Abweichungen aus `AUSWERTUNG_Lauf2.md` §4 und
`AUSWERTUNG_Lauf3.md` §4 weiter. Gegenüber Lauf 3 kommen hinzu:

- **Gewollt** (Owner-Entscheide 2026-10-06 und -07):
  - Der Zieltext ist vorgegeben. Er steht im Auftragspaket statt der drei Aussagen und als
    `ZIELTEXT_Lauf4.md` im Repository; `check` vergleicht ihn mit dem Ergebnis
    (`VERSAND_Lauf-4.txt`, AUFGABE und fünfte Regel).
  - Das Werkzeug ist die Fassung S014: `engine/deltakit.py` mit `engine/kontrollfaelle.json`.
  - Das Auftragspaket erklärt das Einfügen von Zeilen und verlangt die Antwort in einem Codeblock.
  - P2 wird beim Versiegeln am Zieltext geprüft, nicht im Lauf am Diff (Abschnitt 3).
  - Neue Fehlerklasse G; Klasse A ohne Absturz (Abschnitt 3).
- **Aus Lauf 3 festgeschrieben** (Δ-ABG4-02; Owner-Entscheide 2026-10-01 und -07): Messung vor
  jedem Merge, Upload-Dateien allein in einer Antwort, Commit-Zeile nur aus dem Kasten,
  Prüfmerkmal vor dem Einfügen, Kopierweg (Handbuch R9 bis R12 und §3).
- **Unvermeidlich:** Anker (`<START>`, `base_sha`) und `delta_id` sind neu.
- **Unverändert:** Abschnitt (53 Zeilen, `context_hash` wie in Lauf 2 und 3), die Ankerwerte samt
  Zielzahl 50, die drei Anbieter, der Agent, der Wortlaut der Auswahlregel, das öffentliche
  Repository mit derselben Gegenmaßnahme.

---

*AUSWERTUNG_Lauf4.md | Auswertungsschlüssel Lauf 4 | Owner: Co-Creator | 2026-10-07*
