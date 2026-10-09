### 2.1 Schicht-Architektur

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
  ULTRA_PROTOCOL_SYS_DELTA_1_1.md            ← §2.2 und Z.134 korrekturbedürftig, s. Sektion 1
  ULTRA_REF_SYS_DELTA_ENGINE_1_0.md          ← Schreibseite aufgegeben, s. PBP-ART-014
  ULTRA_PROTOCOL_SYS_WARTUNG_1_3.md          (v1.3.10 — Δ-DF-01 angewendet 2026-08-31)
  ULTRA_REF_SYS_REGISTRY_3_2.md              (v3.2.36 — kein ausstehender Fix)
  ULTRA_REF_SYS_STRUKTUR_1_5.md              (nicht mit STRUKTURSTANDARD verwechseln)
  ULTRA_REF_SYS_STRUKTURSTANDARD_1_1.md
  ULTRA_REF_SYS_NAMING_CONVENTION_1_0.md
  ULTRA_PROTOCOL_SYS_CIP_1_0.md              (Fossil, Härtung zurückgestellt)
  ULTRA_ARCH_SYS_FOUNDATION_1_0.md
  ULTRA_PROTOCOL_SYS_ITA_1_2.md
  ULTRA_ARCH_SYS_DELTA-FORCE-SUBSTRAT_0_1.md [Entwurf — §6 überholt, s. PBP-ART-014]

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
  Rohausgaben Lauf 1a: ChatGPT.json · Grok.json · Qwen.json
```

**Layer-1-Count: 7 / 7 Slots — 7 Dateien.**
Der Befund zur Bündel-Konvention ist geschlossen.

