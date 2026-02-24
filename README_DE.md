# VerbenForm

📘 **System zum Erlernen deutscher Verben**

Das Projekt ist ein Lernsystem zum Trainieren deutscher Verben.

## Grundidee

Das Lernen basiert auf **Lernatomen** `(verb + skill_type + pronoun)`

---

## 🧱 Domänenentitäten (Models)

### 1️⃣ Verb

**Deutsches Verb**

**Enthält:**
- `infinitive`
- `translation_en`
- `translation_ru`
- `translation_uk`
- `verb_type`
- `level`
- `auxiliary`
- `participle_ii`

**Verwendet von:**
- ConjugationResolver
- CardFactory
- DistractorGenerator
- LearningUnit
- UserVerbProgress

---

### 2️⃣ VerbForm

**Speichert Formen für:**
- Präsens
- Präteritum

**Verbunden mit:**
- Verb (FK)
- tense
- pronoun
- form

**Verwendet von:**
- ConjugationResolver
- DistractorGenerator (einfache Zeiten)

---

### 3️⃣ Topic

**Logisches Thema (200 Zeichen)**

Wird zur Gruppierung von LearningUnit verwendet.

---

### 4️⃣ LearningUnit

**Konkretes Lernmodul**

**Felder:**
- `level`
- `skill_type`
- `title`
- `order`
- `verbs` (ManyToMany → Verb)

**Wichtige Regel:**
LearningUnit = Thema + konkreter Fertigkeitstyp

**Beispiele:**
- "Bewegung — Präsens"
- "Bewegung — Translation"

LearningUnit speichert KEINE Pronomen. Diese stammen aus dem Enum Pronoun.

---

### 5️⃣ UserVerbProgress

**Speichert den Fortschritt des Benutzers für ein einzelnes Atom**

**Eindeutigkeit:**
`(user, verb, skill_type, pronoun)`

**Felder:**
- `correct_count`
- `wrong_count`
- `streak`
- `mastered`
- `last_answer_at`

**Lernatom:** `(verb, skill_type, pronoun)`

---

## 🧠 Domain Types

### LearningAtom

**Kein Modell. Reines Domänenobjekt**

**Enthält:**
- `verb`
- `skill_type`
- `pronoun`

Wird innerhalb von Services verwendet.

### LearningStatus (Enum)

- `NEW`
- `LEARNING`
- `MASTERED`

Wird zur Anzeige des Fortschritts innerhalb eines Moduls verwendet.

---

## ⚙️ Service-Schicht

Alle Services sind UI-unabhängig.

### 1️⃣ LearningUnitProgressService

**Verantwortlich für:**
- Generierung von Atomen innerhalb von LearningUnit
- Erstellung der Fortschrittsmatrix
- Bestimmung von completed
- Berechnung von percent

**Verändert keine Daten. Liest nur.**

**Verwendet:**
- LearningUnit
- UserVerbProgress
- LearningAtom
- Pronoun Enum

---

### 2️⃣ TrainingEngine

**Verantwortlich für:**
- Auswahl des nächsten Atoms
- Strategie für die Anzeige von Karten

**Aktualisiert keinen Fortschritt.**

**Algorithmus:**
1. Erhält Atome von LearningUnitProgressService
2. Teilt sie in NEW / LEARNING / MASTERED ein
3. Wählt Atom nach wahrscheinlichkeitsbasierter Strategie

Kennt keine Karten.

---

### 3️⃣ CardFactory

**Wandelt LearningAtom → TrainingCard um**

**Interagiert mit:**
- ConjugationResolver
- DistractorGenerator

**Generiert:**
- `question`
- `options`
- `correct_answer`

**Unterstützt:**
- Translation
- Präsens
- Präteritum
- Perfekt

---

### 4️⃣ DistractorGenerator

**Verantwortlich für die Generierung falscher Optionen**

**Translation:**
- nutzt Übersetzungen anderer Verben
- nur aus der aktuellen LearningUnit
- Sprache wird über Settings bestimmt

**Simple tenses:**
- verwendet andere Formen desselben Verbs

**Perfekt:**
Generiert:
- andere Formen mit anderen Pronomen
- falsches auxiliary
- falsches participle-Endung
- fehlendes ge-
- zusätzliches ge-

Kennt nichts über Benutzer.

---

### 5️⃣ ConjugationResolver

**Verantwortlich nur für die Generierung der korrekten Form**

**Unterstützt:**
- Präsens
- Präteritum
- Perfekt

**Perfekt wird dynamisch erstellt:**
`auxiliary + participle_ii`

Kennt kein Lernen.

---

### 6️⃣ ProgressService

**Verantwortlich NUR für die Aktualisierung des Fortschritts**

**Methode:**
`record_answer(progress, is_correct)`

**Logik:**
- +1 correct_count bei korrekter Antwort
- +1 wrong_count bei Fehler
- streak erhöht sich bei korrekter Antwort
- streak wird bei Fehler zurückgesetzt
- mastered = True bei 5 hintereinander
- mastered wird nicht automatisch entfernt

Wählt keine Karten. Kennt keine LearningUnit.

---

## 🔁 Vollständiger Interaktionszyklus

```
Benutzer öffnet Modul
        ↓
TrainingEngine → wählt LearningAtom
        ↓
CardFactory → erstellt TrainingCard
        ↓
Benutzer antwortet
        ↓
ProgressService.record_answer()
        ↓
LearningUnitProgressService berechnet Fortschritt neu
        ↓
Wenn alle Atome mastered → LearningUnit completed
```

---

## 🧩 Prinzip der Verantwortungstrennung

| Komponente | Verantwortung |
|------------|---------------|
| Model | Datenspeicherung |
| LearningUnitProgressService | Lesen des Fortschritts |
| TrainingEngine | Auswahl des nächsten Atoms |
| CardFactory | Generierung der Karte |
| DistractorGenerator | Generierung von Fehlern |
| ConjugationResolver | Korrekte Form |
| ProgressService | Aktualisierung des Fortschritts |

Kein Service tut mehr als eine Sache.

---

## 🎯 Definition "Modul abgeschlossen"

LearningUnit gilt als abgeschlossen, wenn:
**alle Atome (verb + skill_type + pronoun) haben mastered=True**

---

## 🏛 Architektonische Prinzipien

- Domain-driven Ansatz
- Klare Schichtentrennung
- Keine Geschäftslogik in Modellen
- Services sind unabhängig
- Lernatom — zentrale Einheit
