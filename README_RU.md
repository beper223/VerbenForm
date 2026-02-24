# VerbenForm

📘 **Система для изучения немецких глаголов**

Проект представляет собой учебную систему для тренировки немецких глаголов.

## Основная идея

Обучение строится вокруг **атомов обучения** `(verb + skill_type + pronoun)`

---

## 🧱 Доменные сущности (Models)

### 1️⃣ Verb

**Немецкий глагол**

**Содержит:**
- `infinitive`
- `translation_en`
- `translation_ru`
- `translation_uk`
- `verb_type`
- `level`
- `auxiliary`
- `participle_ii`

**Используется:**
- ConjugationResolver
- CardFactory
- DistractorGenerator
- LearningUnit
- UserVerbProgress

---

### 2️⃣ VerbForm

**Хранит формы для:**
- Präsens
- Präteritum

**Связан с:**
- Verb (FK)
- tense
- pronoun
- form

**Используется:**
- ConjugationResolver
- DistractorGenerator (simple tenses)

---

### 3️⃣ Topic

**Логическая тема (200 символов)**

Используется для группировки LearningUnit.

---

### 4️⃣ LearningUnit

**Конкретный учебный модуль**

**Поля:**
- `level`
- `skill_type`
- `title`
- `order`
- `verbs` (ManyToMany → Verb)

**Важное правило:**
LearningUnit = тема + конкретный тип навыка

**Примеры:**
- "Движение — Präsens"
- "Движение — Translation"

LearningUnit НЕ хранит местоимения. Они берутся из Enum Pronoun.

---

### 5️⃣ UserVerbProgress

**Хранит прогресс пользователя по одному атому**

**Уникальность:**
`(user, verb, skill_type, pronoun)`

**Поля:**
- `correct_count`
- `wrong_count`
- `streak`
- `mastered`
- `last_answer_at`

**Атом обучения:** `(verb, skill_type, pronoun)`

---

## 🧠 Domain Types

### LearningAtom

**Не модель. Чистый доменный объект**

**Содержит:**
- `verb`
- `skill_type`
- `pronoun`

Используется внутри сервисов.

### LearningStatus (Enum)

- `NEW`
- `LEARNING`
- `MASTERED`

Используется для отображения прогресса внутри модуля.

---

## ⚙️ Сервисный слой

Все сервисы независимы от UI.

### 1️⃣ LearningUnitProgressService

**Отвечает за:**
- генерацию атомов внутри LearningUnit
- построение матрицы прогресса
- определение completed
- расчёт percent

**Не изменяет данные. Только читает.**

**Использует:**
- LearningUnit
- UserVerbProgress
- LearningAtom
- Pronoun Enum

---

### 2️⃣ TrainingEngine

**Отвечает за:**
- выбор следующего атома
- стратегию показа карточек

**Не обновляет прогресс.**

**Алгоритм:**
1. Получает атомы из LearningUnitProgressService
2. Делит их на NEW / LEARNING / MASTERED
3. Выбирает атом по вероятностной стратегии

Не знает про карточки.

---

### 3️⃣ CardFactory

**Превращает LearningAtom → TrainingCard**

**Взаимодействует с:**
- ConjugationResolver
- DistractorGenerator

**Генерирует:**
- `question`
- `options`
- `correct_answer`

**Поддерживает:**
- Translation
- Präsens
- Präteritum
- Perfekt

---

### 4️⃣ DistractorGenerator

**Отвечает за генерацию неправильных вариантов**

**Translation:**
- берёт переводы других глаголов
- только из текущего LearningUnit
- язык определяется через settings

**Simple tenses:**
- использует другие формы того же глагола

**Perfekt:**
Генерирует:
- другие формы с другими местоимениями
- неправильный auxiliary
- неправильное окончание participle
- отсутствие ge-
- лишнее ge-

Не знает ничего про пользователей.

---

### 5️⃣ ConjugationResolver

**Отвечает только за генерацию правильной формы**

**Поддерживает:**
- Präsens
- Präteritum
- Perfekt

**Perfekt строится динамически:**
`auxiliary + participle_ii`

Не знает про обучение.

---

### 6️⃣ ProgressService

**Отвечает ТОЛЬКО за обновление прогресса**

**Метод:**
`record_answer(progress, is_correct)`

**Логика:**
- +1 correct_count при правильном
- +1 wrong_count при ошибке
- streak увеличивается при правильном
- streak сбрасывается при ошибке
- mastered = True при 5 подряд
- mastered не снимается автоматически

Не выбирает карточки. Не знает про LearningUnit.

---

## 🔁 Полный цикл взаимодействия

```
User открывает модуль
        ↓
TrainingEngine → выбирает LearningAtom
        ↓
CardFactory → создаёт TrainingCard
        ↓
Пользователь отвечает
        ↓
ProgressService.record_answer()
        ↓
LearningUnitProgressService пересчитывает прогресс
        ↓
Если все атомы mastered → LearningUnit completed
```

---

## 🧩 Принцип разделения ответственности

| Компонент | Ответственность |
|-----------|-----------------|
| Model | хранение данных |
| LearningUnitProgressService | чтение прогресса |
| TrainingEngine | выбор следующего атома |
| CardFactory | генерация карточки |
| DistractorGenerator | генерация ошибок |
| ConjugationResolver | правильная форма |
| ProgressService | обновление прогресса |

Ни один сервис не делает больше одной вещи.

---

## 🎯 Определение "модуль пройден"

LearningUnit считается завершённым, если:
**все атомы (verb + skill_type + pronoun) имеют mastered=True**

---

## 🏛 Архитектурные принципы

- Domain-driven подход
- Чёткое разделение слоёв
- Нет бизнес-логики в моделях
- Сервисы независимы
- Атом обучения — центральная единица
