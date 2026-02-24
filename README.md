# VerbenForm

📘 **German Verbs Learning System**

The project is an educational system for training German verbs.

## Core Idea

Learning is built around **learning atoms** `(verb + skill_type + pronoun)`

---

## 🧱 Domain Entities (Models)

### 1️⃣ Verb

**German verb**

**Contains:**
- `infinitive`
- `translation_en`
- `translation_ru`
- `translation_uk`
- `verb_type`
- `level`
- `auxiliary`
- `participle_ii`

**Used by:**
- ConjugationResolver
- CardFactory
- DistractorGenerator
- LearningUnit
- UserVerbProgress

---

### 2️⃣ VerbForm

**Stores forms for:**
- Präsens
- Präteritum

**Connected to:**
- Verb (FK)
- tense
- pronoun
- form

**Used by:**
- ConjugationResolver
- DistractorGenerator (simple tenses)

---

### 3️⃣ Topic

**Logical topic (200 characters)**

Used for grouping LearningUnit.

---

### 4️⃣ LearningUnit

**Specific learning module**

**Fields:**
- `level`
- `skill_type`
- `title`
- `order`
- `verbs` (ManyToMany → Verb)

**Important rule:**
LearningUnit = topic + specific skill type

**Examples:**
- "Movement — Präsens"
- "Movement — Translation"

LearningUnit DOES NOT store pronouns. They are taken from Enum Pronoun.

---

### 5️⃣ UserVerbProgress

**Stores user progress for one atom**

**Uniqueness:**
`(user, verb, skill_type, pronoun)`

**Fields:**
- `correct_count`
- `wrong_count`
- `streak`
- `mastered`
- `last_answer_at`

**Learning atom:** `(verb, skill_type, pronoun)`

---

## 🧠 Domain Types

### LearningAtom

**Not a model. Pure domain object**

**Contains:**
- `verb`
- `skill_type`
- `pronoun`

Used inside services.

### LearningStatus (Enum)

- `NEW`
- `LEARNING`
- `MASTERED`

Used for displaying progress within a module.

---

## ⚙️ Service Layer

All services are UI-independent.

### 1️⃣ LearningUnitProgressService

**Responsible for:**
- generating atoms within LearningUnit
- building progress matrix
- determining completed
- calculating percent

**Does not modify data. Read-only.**

**Uses:**
- LearningUnit
- UserVerbProgress
- LearningAtom
- Pronoun Enum

---

### 2️⃣ TrainingEngine

**Responsible for:**
- selecting next atom
- card display strategy

**Does not update progress.**

**Algorithm:**
1. Gets atoms from LearningUnitProgressService
2. Divides them into NEW / LEARNING / MASTERED
3. Selects atom by probabilistic strategy

Doesn't know about cards.

---

### 3️⃣ CardFactory

**Transforms LearningAtom → TrainingCard**

**Interacts with:**
- ConjugationResolver
- DistractorGenerator

**Generates:**
- `question`
- `options`
- `correct_answer`

**Supports:**
- Translation
- Präsens
- Präteritum
- Perfekt

---

### 4️⃣ DistractorGenerator

**Responsible for generating incorrect options**

**Translation:**
- takes translations of other verbs
- only from current LearningUnit
- language determined via settings

**Simple tenses:**
- uses other forms of the same verb

**Perfekt:**
Generates:
- other forms with other pronouns
- incorrect auxiliary
- incorrect participle ending
- missing ge-
- extra ge-

Doesn't know anything about users.

---

### 5️⃣ ConjugationResolver

**Responsible only for generating the correct form**

**Supports:**
- Präsens
- Präteritum
- Perfekt

**Perfekt built dynamically:**
`auxiliary + participle_ii`

Doesn't know about learning.

---

### 6️⃣ ProgressService

**Responsible ONLY for updating progress**

**Method:**
`record_answer(progress, is_correct)`

**Logic:**
- +1 correct_count for correct answer
- +1 wrong_count for error
- streak increases for correct answer
- streak resets for error
- mastered = True for 5 in a row
- mastered is not automatically removed

Doesn't select cards. Doesn't know about LearningUnit.

---

## 🔁 Complete Interaction Cycle

```
User opens module
        ↓
TrainingEngine → selects LearningAtom
        ↓
CardFactory → creates TrainingCard
        ↓
User answers
        ↓
ProgressService.record_answer()
        ↓
LearningUnitProgressService recalculates progress
        ↓
If all atoms mastered → LearningUnit completed
```

---

## 🧩 Separation of Concerns Principle

| Component | Responsibility |
|-----------|-----------------|
| Model | data storage |
| LearningUnitProgressService | reading progress |
| TrainingEngine | selecting next atom |
| CardFactory | generating card |
| DistractorGenerator | generating errors |
| ConjugationResolver | correct form |
| ProgressService | updating progress |

No service does more than one thing.

---

## 🎯 Definition of "Module Completed"

LearningUnit is considered completed if:
**all atoms (verb + skill_type + pronoun) have mastered=True**

---

## 🏛 Architectural Principles

- Domain-driven approach
- Clear layer separation
- No business logic in models
- Services are independent
- Learning atom — central unit
