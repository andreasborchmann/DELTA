# DELTA-FORCE — PBP-Instanz
## SYS | Daten — PBP-Projektinstanz | ULTRA v1.3 Konform

**Herkunftsvermerk:** Diese Datei ist der Testgegenstand der Transportachse im Projekt DELTA-FORCE, eine Kopie von `ULTRA_DATA_SYS_DELTA-FORCE_0_4.md`. Ihr §2.1 ist seit `337876f` (Lauf 1b) verändert. Sie ist kein gepflegtes Artefakt; die gepflegte PBP-Instanz liegt außerhalb dieses Repositorys.

---

**Name:**             DELTA-FORCE — PBP-Instanz
**Version:**          v0.4
**Owner:**            Co-Creator
**Erstellt:**         2026-07-25 (PBP-S001)
**Archiv-Schwelle:**  Bei >8 Sessions oder >15 Artefakten — Kompakt-Summary nach PBP §2.1
                      SKALIERUNGS-SIGNAL erwägen. **Stand: 6 Sessions / 12 Artefakte.**
**Status:**           aktiv laufend (MAJOR 0)
**Basis:**            ULTRA_PROTOCOL_SYS_PBP_1_2.md
**Aktualisiert:**     2026-09-13 (PBP-S006 — Delta verworfen mit Messung, drei externe Läufe,
                      zwei Substrat-Befunde, Prompt-Fehler des Testautors offengelegt)

**MINOR-Bump-Begründung (PBP §2.2 + Erfahrungsbefund v0.3):** Inhaltliche Änderung in vier
Sektionen. Zusätzlich gilt seit v0.3 die verschärfte Hausregel: bei jeder inhaltlichen
Änderung MINOR bumpen, auch wo §2.2 PATCH erlauben würde — der Dateiname ist kein
Versionsidentifikator, und zwei Fassungen unter einem Namen haben real Schaden angerichtet.

---

## SEKTION 1 — PROJECT IDENTITY

```
PROJECT-NAME:        DELTA-FORCE
TYP:                 TEST + UNTERSUCHUNG
ULTRA-VERSION:       1.3
STARTDATUM:          2026-07-25
OWNER:               Co-Creator

IDENTITÄTS-ENTSCHEID:  [unverändert seit PBP-S005]
  Werdender Standard (Pilotprojekt). DELTA-FORCE ist Untersuchungs- UND Testprojekt für
  ein operativ belastbareres Artefaktmanagement und Kontext-Engineering. Das manuelle
  Verfahren ist nicht mehr zielführend und zu unsicher — belegt seit PBP-S005, nicht
  vermutet (PBP-ART-006).

  Zielbild, ausdrücklich als erster Wurf: GitHub als SSOT für Artefakte, Claude Code Web
  als Bedienoberfläche, mit Protokollen für Schreiben, Prüfen, Aktualisieren, Verwalten
  und Laden von Artefakten. Keine Endlösung. Maßstab: belastbar und potentialhaltig —
  oder verwerfen und anders suchen.

  [ZUSATZ, PBP-S006] Das Zielbild hat seit S006 eine erste gemessene Bedingung: Ein
  GitHub-SSOT trägt nur dann einen Audit-Trail, wenn Artefakte einzeln und zum Zeitpunkt
  ihrer Änderung committet werden. Per Sammel-Upload befüllte Repositories tragen für
  alle Dateien dasselbe Datum — die Historie, auf der die Vision beruht, ist dann leer.
  Siehe PBP-ART-011.

ZWEI ACHSEN:  [FORTGESCHRIEBEN, PBP-S006]
  TRANSPORTACHSE — hält die Naht? Delta entsteht dort, wird hier angewendet, Diff passt.
                   Status: ungetestet. **0 von 2 End-to-End-Läufen.** Unverändert seit
                   Projektbeginn. Die drei Läufe aus S006 waren Substrat-Sondierungen,
                   keine End-to-End-Läufe — sie enthielten weder Delta-Erstellung noch
                   Anwendung noch Downstream-Prüfung. Die Zählung „Lauf 2" aus der
                   Übergabe PBP-S005→S006 wird nicht übernommen (Kohärenz-Gate S006,
                   Prüfung 1: Behalte neu).
  URTEILSACHSE   — hält das Tor? Wird eine falsche Begründung gestoppt?
                   Status: Lauf 1 bestanden (2026-09-12, PBP-ART-007). Unverändert.
  Die beiden Achsen messen Verschiedenes und dürfen nicht gegeneinander verrechnet werden.
  [S006] Diese Regel wurde in der eigenen Übergabe verletzt, nicht von außen.

ERFOLGSKRITERIUM:  [GELTEND — unverändert seit PBP-S003]
  Das Projekt ist erfolgreich, wenn zwei unabhängige End-to-End-Testläufe auf GitHub
  fehlerfrei absolviert wurden UND ein gezielter Nach-Audit (mindestens:
  Stichprobenvergleich der angewendeten Deltas gegen die tatsächlichen Repository-Diffs)
  keine stillen Schäden findet. Konkret: Ein externes Modell schnürt jeweils "blind" ein
  Delta-Paket, Claude Code wendet es mit echten GitHub-Credentials auf das Repository an
  und führt die Downstream-Prüfung automatisch durch. Zwei unabhängige Läufe belegen
  "reproduzierbar" tatsächlich. Sobald das erfüllt ist, transformiert das Projekt vom
  Typ TEST in den regulären BETRIEB.

  [NEUFASSUNG WEITERHIN VORGELEGT, NICHT ENTSCHIEDEN — seit PBP-S005, zweite Session offen]
    Erfolgreich, wenn zwei unabhängige End-to-End-Läufe fehlerfrei absolviert wurden UND
    der Nach-Audit belegt, dass JEDES angewendete Delta durch das Gate lief und JEDER
    Gate-Lauf einen Audit-Eintrag hat, der zum Repository-Diff passt.
    Maßstab: "vollständig geprüft, nicht garantiert schadensfrei."
    ERKLÄRTE LÜCKE: Ein inhaltlich falsches Delta, das korrekt angewendet wird, erzeugt
    einen sauberen Diff und einen gültigen Audit-Eintrag. Diese Klasse liegt außerhalb
    der Reichweite des Nach-Audits. Sie gehört zur Urteilsachse, nicht zur Transportachse.
  STATUS: Typ-II-Änderung. Stabilitätsfenster prüfen. Owner entscheidet. Bis dahin gilt
  die Fassung von PBP-S003 unverändert weiter.
  [S006-Anmerkung] Der Audit-Eintrag, auf den die Neufassung sich stützt, setzt voraus,
  dass die Historie überhaupt trägt — siehe PBP-ART-011. Die Neufassung wird dadurch
  nicht falsch, aber ihre Voraussetzung ist jetzt selbst ein Prüfpunkt.

ABGELEITETE PROJECTS:
  (leer)

CROSS-PROJEKT-ABHÄNGIGKEITEN:
  upstream:   Vorsessions dieses Chats (nicht PBP-geführt) → Stand, Optionsraum,
              uebergabe_naechste_session.md, metaposition.md, metaposition_nachtrag.md.
              Externe Raumvermessungs-Session (2026-08-31) → Delta Protocol v1.1 +
              Engine v1.0.1 real geprüft, zwei SSOT-Bugs samt Fix-Deltas,
              ULTRA_ART_INTEGRIERT_DELTA-FORCE-VERMESSUNG_1_0.md als Rohstoff.
  downstream: Rückfluss-Befunde an Framework-Ebene, alle Typ II, nicht Gegenstand
              dieses Projekts — CCR-Rückfluss nach COMMIT Schritt 2 · PBP §3.2 ohne
              Feld für offene Punkte · STRUKTURSTANDARD-Scope (ARCH/RUNBOOK/ART
              undeklariert) · Separator ═══ in INIT-Runtime · ID-Kollisionen.
              [NEU, PBP-S006] DELTA 1.1 §2.2 gegen Engine-Regex: das Protokoll definiert
              replace_section als „bis zur nächsten ##-Überschrift", erlaubt in der
              Feldtabelle aber ausdrücklich ## oder ### als Anker — in sich unstimmig.
              Die Engine matcht ^#{1,6}\s und ist die sichere Seite. Korrekturbedürftig
              ist der Protokolltext, nicht die Implementierung. Typ II.
              [NEU, PBP-S006] Delta-Protokoll/Engine: context_hash ist nur für protected
              files Pflicht (Präfix ULTRA_CORE_ / ULTRA_REF_SYS_REGISTRY_). Für alle
              anderen Dateien läuft eine Anwendung ohne Staleness-Schutz durch. Typ II.
  geparkt:    har_kernel/GATE_RUN-System — Revisit-Trigger: CLAUDE_CODE-Ruleset existiert
              oder wird bewusst übersprungen, UND einer der zwei End-to-End-Läufe steht an.
              🅿 PARKED, unverändert seit PBP-S004.
```

---

## SEKTION 2 — BOOTSTRAP SETUP

### 2.1 Schicht-Architektur

*Delta `ULTRA-Δ-20260912-001` NICHT angewendet — auf `rejected` gesetzt (PBP-ART-009).
Die zwei Statuszeilen, die es korrigieren sollte, stehen seit v0.3 korrekt.*

```
SCHICHT 0 (permanent, kein RAG-Slot):
  Core + Claude Instructions — 2 Dateien

SCHICHT 1 — PFLICHT:
  ULTRA_PROTOCOL_SYS_PBP_1_2.md
  ULTRA_PROTOCOL_SYS_CCR_1_4.md
  ULTRA_PROTOCOL_SYS_INIT_RUNTIME_1_0.md
  ULTRA_PROTOCOL_SYS_COMMIT_RUNTIME_1_0.md
  ULTRA_DATA_SYS_DELTA-FORCE_0_4.md         ← diese Datei selbst, aktiv gepflegt

SCHICHT 1 — NAVIGATORISCH:
  ULTRA_REF_SYS_REGISTRY_RUNTIME_1_0.md
  Führungs-Referenz: UEBERGABE_PBP-S006_nach_S007.md

SCHICHT 2 — bei Bedarf:
  ULTRA_PROTOCOL_SYS_EVOLUTION_1_3.md
  ULTRA_PROTOCOL_SYS_DELTA_1_1.md            ← §2.2 korrekturbedürftig, s. Sektion 1
  ULTRA_REF_SYS_DELTA_ENGINE_1_0.md          ← v1.0.1, vier Befunde PBP-ART-010
  ULTRA_PROTOCOL_SYS_WARTUNG_1_3.md          (v1.3.10 — Δ-DF-01 angewendet 2026-08-31)
  ULTRA_REF_SYS_REGISTRY_3_2.md              (v3.2.36 — kein ausstehender Fix)
  ULTRA_REF_SYS_STRUKTUR_1_5.md              (nicht mit STRUKTURSTANDARD verwechseln)
  ULTRA_REF_SYS_STRUKTURSTANDARD_1_1.md
  ULTRA_REF_SYS_NAMING_CONVENTION_1_0.md
  ULTRA_PROTOCOL_SYS_CIP_1_0.md              (Fossil, Härtung zurückgestellt)
  ULTRA_ARCH_SYS_FOUNDATION_1_0.md
  ULTRA_PROTOCOL_SYS_ITA_1_2.md
  ULTRA_ARCH_SYS_DELTA-FORCE-SUBSTRAT_0_1.md [Entwurf — §1 hat seit S006 zwei
                                               gemessene Befunde, §3–§6 weiter unbelegt]

SCHICHT 3 — Archiv (niemals Standard-Session):
  layer3-archive/hist/, layer3-archive/delta-pakete/, layer3-archive/deprecated/
  β-Vorgeschichte (Kern-Härtung/IMAGO-Linie) — Referenz, kein Layer-1/2-Slot.
  PBP-S004-Arbeitsprodukte: TESTKIT.md, ULTRA_PROTOCOL_SYS_WARTUNG_TEST.md,
  ULTRA_RUNBOOK_SYS_DELTA-FORCE_POISONED-RATIONALE_1_0.md,
  ULTRA_REVIEW_SYS_DELTA-FORCE-TESTVORBEREITUNG_1_0.md
  ULTRA_REVIEW_SYS_DELTA-FORCE-STANDORT_1_0 (P5 aus S005),
  Lauf-1-Ausgabe der Urteilsachse (Claude Code Web, 2026-09-12).
  [NEU, PBP-S006] rejected/ULTRA-Delta-20260912-001.json ·
  HANDBUCH_PBP-S006_Testhandgriffe.md · AUSWERTUNGSSCHLUESSEL_Lauf2_VERSIEGELT.md ·
  Rohausgaben der drei Läufe A/B/C (Haiku 4.5 ×2, Sonnet 5 niedrig).
  metaposition.md · metaposition_nachtrag.md ·
  UEBERGABE_PBP-S005_nach_S006.md — archiviert (Owner-Entscheid 2026-09-15).
```

**Layer-1-Count: 7 / 7 Slots — 7 Dateien.**
Der Befund zur Bündel-Konvention ist geschlossen.

### 2.2 PBP-Instanz-Naming-Konvention

`ULTRA_DATA_[DOMAIN]_[PROJEKTNAME]_[MAJOR]_[MINOR].md` nach PBP §2.2. Diese Datei:
`ULTRA_DATA_SYS_DELTA-FORCE_0_4.md`.

**Erfahrungsbefund, PBP-S005, weiter gültig:** PATCH ohne Dateinamen-Wechsel ist
regelkonform und erzeugt trotzdem ein reales Problem — zwei inhaltlich verschiedene
Fassungen trugen beide `_0_2.md`. Bei jeder inhaltlichen Änderung MINOR bumpen.

**Ergänzung, PBP-S006:** Unter GitHub löst der Commit-SHA das nur, wenn einzeln und zum
Änderungszeitpunkt committet wird. Bei Sammel-Upload trägt der SHA nichts bei — die
Hausregel bleibt also auch nach dem Umzug nötig (PBP-ART-011).

**FREQUENZ-SIGNAL (PBP §2.2):** v0.3 am 12.09., v0.4 am 13.09. — zwei MINOR-Bumps, aber
nur einer innerhalb von 7 Tagen zusätzlich zum vorherigen (v0.2 am 31.08.). Schwelle
„>2 in 7 Tagen" damit knapp nicht erreicht. Bei einem weiteren Bump vor dem 19.09. ist der
Plan-Realitäts-Abgleich nicht mehr nur überfällig, sondern signalisiert.

---

## SEKTION 3 — SESSION BRIEF

### PBP-S001 | 2026-07-25 — ABGESCHLOSSEN
Initiierung der Instanz, Sektion 1+2. KOHÄRENZ: DIVERGENZ_DOKUMENTIERT (Einzellauf).

### PBP-S002 | 2026-07-30 — ABGESCHLOSSEN
Sektionen 3+4 nachgetragen. KOHÄRENZ: ✓ rein additiv.

### PBP-S003 | 2026-08-31 — ABGESCHLOSSEN
Raumvermessung, Erfolgskriterium-Gate entschieden, zwei SSOT-Fix-Deltas.
KOHÄRENZ: ✓. **CCR-REF: — (COMMIT nie ausgelöst, 🔁 seit 13 Tagen offen, vierte Session).**

### PBP-S004 | 2026-09-05 — ABGESCHLOSSEN
Testvorbereitung, Testkit gesichert, Ausführungsweg verifiziert, har_kernel geparkt.
CCR-REF: DELTA_FORCE-Testvorbereitung-20260905. ITA-REF: ITA-20260905-HTMLDETAILS-001.

### PBP-S005 | 2026-09-12 — ABGESCHLOSSEN
Standortbestimmung, Urteilsachse Lauf 1 bestanden, Substrat entschieden.
CCR-REF: DELTA_FORCE-Standortbestimmung-20260912. ITA-REF: ITA-20260912-DELTAPAYLOAD-001.
KOHÄRENZ: ⚠ eine Spannung gehalten (Erfolgskriterium-Neufassung).

### PBP-S006 | 2026-09-13

```
MASTERPLAN-POSITION: Ausführungssession — ein Delta entscheiden, die Transportachse messen.
LAYER-1-COUNT:       7 / 12 Slots (real 9 Dateien — s. 2.1)

VOR DER SESSION:
  ZIEL:              Δ anwenden, dann Lauf 2 (Transportachse). Keine Analyse.
  PFLICHT-ARTEFAKT:  Entscheidung über das Delta + ein durchgeführter Lauf.
  VORBEDINGUNG:      PBP-S005 abgeschlossen; Übergabe, Delta-JSON und metaposition
                     vorgelegt. Engine, Delta-Protokoll, WARTUNG, Registry und _0_2.md
                     im Verlauf nachgereicht.
  ERFOLGSPRÜFUNG:    Das Delta ist entschieden, und die Entscheidung ist gemessen
                     statt begründet.

NACH DER SESSION:
  ARTEFAKT-ID:       PBP-ART-009, PBP-ART-010, PBP-ART-011, PBP-ART-012
  Δ-IDs APPLIED:     keine. ULTRA-Δ-20260912-001 → rejected (ziel-veraltet).
  CCR-REF:           DELTA_FORCE-Ausfuehrung-20260913
  ITA-REF:           ITA-20260913-REPO-AUDITIERBARKEIT-001
  KOHÄRENZ-STATUS:   WIDERSPRUCH: dokumentiert — die Übergabe PBP-S005→S006 zählt den
                     Durchlauf als „Lauf 2" der Transportachse; er war keiner.
                     Entscheidung: Behalte neu, Transportachse bleibt 0 von 2.
                     Prüfung 2–5 ohne Befund. Prüfung 5 fensterfrei: DELTA 1.1 ist nicht
                     Core-Wortlaut, und es wurde nichts geändert, nur befundet.
  E2:                ✓ mit zwei dokumentierten Unregelmäßigkeiten — ERI-Limit P1 von 2
                     auf 3 erhöht (drei externe Läufe); Phase blieb formal P1, während
                     erhebliche Ausführungsarbeit lief.
  SESSION-STATUS:    ABGESCHLOSSEN

OFFENE PUNKTE  [Feld nach PBP §3.1; §3.2 sieht es nicht vor — Framework-Lücke ausgelagert]
  ⏳ ITA-Übergabe an ein Zweitsystem — erzeugt, aber noch nirgends validiert
  ⏳ DELETE-Kandidat Führungs-Referenz-Bündel — Owner entscheidet (s. 2.1)
  ⏳ Zweite _0_2.md (Stand 05.09.) unauffindbar — Handgriff 1 aus S006 nicht geschlossen
  ⏳ DELTA 1.1 §2.2 gegen Engine-Regex — Typ II, ausgelagert
  ⏳ context_hash nur für protected files Pflicht — Typ II, ausgelagert
  ⏳ apply_delta arbeitet mit Zeilenoffsets aus der Vorschau — am Code gelesen,
     nicht provoziert
  🔁 Erfolgskriterium-Neufassung — Owner-Entscheidung, Typ II, zweite Session offen
  🔁 PBP-S003 ohne CCR — seit 2026-08-31, vierte Session in Folge
  🔁 Transportachse 0 von 2 — unverändert seit Projektbeginn
  🔁 Plan-Realitäts-Abgleich (PBP §6) — Trigger seit S004 erreicht, nie ausgeführt,
     jetzt dritte Session überfällig
  🔁 DELTA-FORCE fehlt als Katalogzeile in Registry FULL
  🔁 Substrat-Spezifikation §3–§6 ohne Primärquellenabgleich
  🔁 Tokenökonomie ohne Messgröße
  🅿 har_kernel-Gate-Run — Revisit-Trigger unverändert
```

---

## SEKTION 4 — BEDEUTUNGS-REGISTER

### PBP-ART-001 — PBP-S001 | Plan
Instanz-Entwurf Sektion 1+2. **STATUS: Abgelöst durch PBP-ART-003.**

### PBP-ART-002 — PBP-S002 | Entscheidung
Ressourcen-Check-Disziplin: `/mnt/project/` prüfen, bevor Abwesenheit gemeldet wird.
**STATUS: Aktiv** — in S003 bis S006 real angewendet.

### PBP-ART-003 — PBP-S003 | Entscheidung
Erfolgskriterium-Gate: zwei Läufe statt Einzellauf. **STATUS: Aktiv.**

### PBP-ART-004 — PBP-S004 | Entscheidung
har_kernel-Gate-Run geparkt mit Revisit-Trigger. **STATUS: Aktiv — 🅿 PARKED.**

### PBP-ART-005 — PBP-S004 | Plan
Verifiziertes Vorbereitungspaket. **STATUS: Erfüllt durch PBP-ART-007.**

### PBP-ART-006 — PBP-S005 | Analyse
Die Juli-Kette — Statusaussagen waren nie korrekt, in beide Richtungen. 37 Tage zwischen
„gefixt" behauptet und gefixt, danach der Gegenfehler. **STATUS: Aktiv** — trägt den
Identitäts-Entscheid. [S006: durch Lauf B unabhängig bestätigt, s. PBP-ART-012.]

### PBP-ART-007 — PBP-S005 | Entscheidung
Urteilsachse Lauf 1 bestanden — Ausgang 1. **STATUS: Aktiv.**

### PBP-ART-008 — PBP-S005 | Entscheidung
Substrat entschieden — Abschnitt statt Datei als tragende Einheit.
**STATUS: Aktiv — Entwurf. [S006: Richtung eines Teilbefunds korrigiert, s. PBP-ART-010.]**

### PBP-ART-009

```
SESSION:         PBP-S006 | 2026-09-13
TYP:             Entscheidung
TITEL:           Delta ziel-veraltet verworfen — und warum das nicht dasselbe ist wie falsch
BEDEUTUNG:       ULTRA-Δ-20260912-001 steht auf rejected. Entscheidend ist die Begründung:
                 Gegen seine deklarierte Zieldatei _0_2.md tut das Delta exakt das, was
                 seine Rationale sagt — Dry-Run gemessen, Abschnitt 44 → 54 Zeilen,
                 3 ersetzt, 13 neu. Minimal und korrekt. Gegen die real gepflegte _0_3.md
                 ist dieselbe Operation zerstörerisch: 19 Zeilen entfernt oder ersetzt,
                 darunter der Selbstverweis, drei Dokumentverweise aus S005 und — am
                 schwersten — der ehrliche Layer-1-Count, der durch „Puffer weiterhin
                 komfortabel" ersetzt worden wäre.
                 Damit ist eine Fehlerklasse benannt, die vorher keinen Namen hatte: ein
                 Delta kann inhaltlich richtig und trotzdem gefährlich sein, weil sein
                 Ziel sich unter ihm bewegt hat. „Rejected weil falsch" und „rejected weil
                 ziel-veraltet" verlangen verschiedene Konsequenzen.
                 Gemessene context_hashes (compute_section_hash, inkl. Überschriftszeile):
                 _0_2 §2.1 = sha256:ea224679…94eb2 · _0_3 §2.1 = sha256:4afe6d8f…c56bf.
KOHÄRENZ-CHECK:  ✓ widerspricht keinem Artefakt
ARTEFAKT:        rejected/ULTRA-Delta-20260912-001.json (Payload und target byte-identisch
                 zum Original; nur meta.status und meta.rationale geändert)
EINSCHRÄNKUNG:   Die zweite _0_2.md (Stand 05.09.) lag nie vor. Alles über sie stammt
                 aus der Übergabe.
STATUS:          Aktiv
```

### PBP-ART-010

```
SESSION:         PBP-S006 | 2026-09-13
TYP:             Analyse
TITEL:           Vier Engine-Befunde — und eine Richtungskorrektur an PBP-ART-008
BEDEUTUNG:       Die Engine v1.0.1 wurde erstmals real ausgeführt statt gelesen.
                 B-1: Sie hätte nicht gewarnt. validate_delta → ok, check_context_hash →
                 „no_hash_provided", läuft weiter. Der Staleness-Schutz greift nur bei
                 Präfix ULTRA_CORE_ und ULTRA_REF_SYS_REGISTRY_. Eine PBP-Instanzdatei
                 ist nicht protected — das Delta wäre ohne einen Einwand durchgelaufen.
                 Praxisregel daraus: context_hash immer setzen.
                 B-2: format_preview zeigt keinen Diff. 122 Zeilen Ausgabe, Abschnitt
                 vorher und nachher untereinander, keine Zeilenbilanz, kein Löschhinweis.
                 Das Human Gate trägt nur, wenn ein Mensch zwei 50-Zeilen-Blöcke von Hand
                 vergleicht.
                 B-3, die Korrektur: DELTA 1.1 §2.2 definiert replace_section als „bis zur
                 nächsten ##-Überschrift", erlaubt in der Feldtabelle aber ausdrücklich
                 ## oder ### als Anker. Der Protokolltext ist in sich unstimmig. Die Engine
                 matcht ^#{1,6}\s und ist fence-fest. Auf diesem Delta: Engine endet bei
                 „### 2.2", Protokoll-Wortlaut erst bei „## SEKTION 3" — 22 Zeilen
                 Differenz in _0_2, 13 in _0_3. Eine protokolltreue Implementierung hätte
                 zwei Sektionen mitersetzt. PBP-ART-008 führte die Divergenz neutral;
                 sie ist nicht neutral. Die Engine ist die sichere Seite.
                 B-4: run_delta hält sein Human Gate über input() — der Mechanismus, den
                 metaposition.md als sandbox-unzuverlässig gemessen hat. Und apply_delta
                 lädt den Inhalt neu, arbeitet dann aber mit den Zeilenoffsets aus der
                 Vorschau.
KOHÄRENZ-CHECK:  ⚠ korrigiert die Richtung eines Teilbefunds in PBP-ART-008, ersetzt es
                 nicht. Entscheidung: beide behalten, Korrektur hier dokumentiert.
EINSCHRÄNKUNG:   B-4 zweite Hälfte am Code gelesen, nicht durch einen provozierten
                 Fehlschlag belegt. Die Engine ist Layer 3 und trägt selbst den Vermerk
                 „nicht in LLM-Kontext laden" — bewusster Regelbruch für einen
                 einmaligen Messzweck, hier deklariert.
STATUS:          Aktiv
```

### PBP-ART-011

```
SESSION:         PBP-S006 | 2026-09-13
TYP:             Analyse
TITEL:           Zwei Substrat-Befunde, die niemand designt hat
BEDEUTUNG:       Beide fielen als Nebenprodukt der Läufe an und betreffen die Vision
                 unmittelbarer als der geplante Test.
                 (1) NAMENSSUCHE. Die Glob-Suche **/*[Ww]artung* findet
                 ULTRA_PROTOCOL_SYS_WARTUNG_1_3.md nicht — die Namenskonvention schreibt
                 den Domänenteil durchgehend groß, das Muster deckt nur Wartung/wartung.
                 Zwei von drei Dateinamen-Suchen liefen leer; gerettet hat den Lauf erst
                 eine Inhaltssuche. Der Fehlschlag ist stumm: der Agent erhält
                 „nicht vorhanden" statt „nicht getroffen".
                 (2) HISTORIE. git log zeigt für alle vier Dateien dasselbe Datum —
                 das des Sammel-Uploads. Ein per Upload befülltes Repository trägt keine
                 Evidenz für historische Aussagen. Für eine Vision, die auf git-nativem
                 Audit-Trail beruht, ist das der härteste Fund dieser Session: der
                 Audit-Trail entsteht nicht durch GitHub, sondern durch die Commit-
                 Disziplin. Ohne sie ist die Historie leer und sieht trotzdem gültig aus.
                 Beide Befunde gehören in die Substrat-Spezifikation §1 — der einzige
                 Abschnitt, der seit S005 eine Grundlage hatte, und jetzt zwei mehr.
KOHÄRENZ-CHECK:  ✓ ergänzt PBP-ART-008 §1, widerspricht nichts
ITA-REF:         ITA-20260913-REPO-AUDITIERBARKEIT-001 (schema-validiert, 0 Fehler)
EINSCHRÄNKUNG:   Einzelquelle — ein Repository, drei Läufe, keine unabhängige
                 Wiederholung. Reproduktionsrezept im ITA unter
                 falsification.verification_path, Aufwand zwei Minuten.
STATUS:          Aktiv
```

### PBP-ART-012

```
SESSION:         PBP-S006 | 2026-09-13
TYP:             Analyse
TITEL:           Drei Läufe, drei Fehlerbilder — und der Fehler lag im Testinstrument
BEDEUTUNG:       Lauf A (Haiku 4.5, Originalprompt): findet die korrekte Belegstelle
                 v1.3.10 / Δ-DF-01, zitiert sie — und bricht eine Zeile vor dem Satz ab,
                 der den Fall entscheidet. Urteil: „stimmt". Belegstelle richtig,
                 Urteil invertiert. Diese Klasse fehlte im eigenen Auswertungsschlüssel;
                 sie ist gefährlicher als ein Nichtfund, weil sie einen Beleg mitliefert.
                 Lauf B (Haiku 4.5, geschärfter Prompt, drei Subagenten): benennt die
                 37 Tage explizit. Die Hypothese aus der Auswertung von Lauf A — der
                 Prompt hatte Datum und Version weggelassen — ist damit gestützt.
                 Lauf C (Sonnet 5, Aufwand niedrig): beantwortet die Versionsfrage korrekt
                 und datiert, ordnet die Repo-Grenze sauber als „weder bestätigt noch
                 widerlegt" ein — und prüft die Fix-Behauptung gar nicht. Das Wort
                 „gefixt" stand in derselben Zeile wie die Version.
                 DER EIGENTLICHE BEFUND: Der geschärfte Prompt enthielt die falsche
                 Prämisse „Aussagen über den Stand anderer Dateien in diesem Repository".
                 Die Dateilisten der Übergabe sind Aussagen über eine Projekt-Wissensbasis,
                 nicht über ein Repo. Beide Läufe übernahmen die Prämisse und erzeugten
                 Scheinbefunde („83 % der Dateien fehlen", „die zentrale Behauptung ist
                 widerlegt"). Der Prompt behob das invertierte Urteil und entfernte dabei
                 den Prüfgegenstand.
                 Das ist die Bewegung aus metaposition.md — eine punktuell korrekte
                 Korrektur wird verallgemeinert, ohne die Verallgemeinerung zu prüfen —
                 diesmal im Testinstrument, und der Autor war die KI dieser Session.
KOHÄRENZ-CHECK:  ✓ bestätigt PBP-ART-006 unabhängig (Lauf B), widerspricht nichts
EINSCHRÄNKUNG:   Ein Modell je Promptfassung. Dass der Prompt und nicht das Modell den
                 Ausschlag gab, ist gestützt, nicht bewiesen — dafür fehlt Lauf A mit
                 Sonnet 5.
STATUS:          Aktiv
```

---

## CHANGELOG

v0.4 (2026-09-13, PBP-S006) — MINOR:
  Delta ULTRA-Δ-20260912-001 verworfen statt angewendet, mit gemessenem Dry-Run.
  Zwei Achsen fortgeschrieben: Transportachse bleibt 0 von 2, „Lauf 2"-Zählung der
  Übergabe nicht übernommen (Kohärenz-Gate Prüfung 1, Behalte neu).
  Identitäts-Entscheid um eine gemessene Bedingung ergänzt (Commit-Disziplin).
  §2.1: Führungs-Referenz auf die neue Übergabe, DELETE-Kandidat für das Altbündel
  markiert. Layer-1-Zählung auf 7/9 aktualisiert, 7/7 bei Annahme.
  §2.2: Frequenz-Signal nach PBP §2.2 ausgewertet.
  Zwei neue Downstream-Einträge (DELTA 1.1 §2.2, context_hash-Geltungsbereich), beide Typ II.
  PBP-ART-009 bis PBP-ART-012 neu. ITA-20260913-REPO-AUDITIERBARKEIT-001 erzeugt.

v0.3 (2026-09-12, PBP-S005) — MINOR:
  Identitäts-Entscheid präzisiert, Zwei-Achsen-Modell neu, Erfolgskriterium-Neufassung
  vorgelegt. Metadatenblock nach STRUKTURSTANDARD §2.4 ergänzt. PBP-ART-006/007/008 neu.
  Dateiname-Kollision `_0_2.md` durch MINOR-Bump aufgelöst.

v0.2 (2026-08-31, PBP-S003; 2026-09-05, PBP-S004 als PATCH):
  Erfolgskriterium-Gate entschieden. Testvorbereitung, har_kernel geparkt.
  *Anmerkung v0.3: Der PATCH vom 5.9. erzeugte eine zweite, inhaltlich verschiedene Datei
  unter demselben Namen. Regelkonform nach PBP §2.2 und trotzdem ein realer Defekt.*

v0.1 (2026-07-25, PBP-S001; 2026-07-30, PBP-S002):
  Initiierung. Sektionen 3+4 nachgetragen.

---

*ULTRA_DATA_SYS_DELTA-FORCE_0_4.md | PBP-Instanz | Owner: Co-Creator | 2026-09-13*
