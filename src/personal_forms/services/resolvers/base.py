from src.common.choices import SkillType, Tense


class BaseSkillResolver:
    # Маппинг для сопоставления SkillType (из атома) и Tense (из модели VerbForm)
    # Используем .value для ключей, чтобы поиск по строке работал
    SKILL_TO_TENSE = {
        SkillType.PRAESENS.value: Tense.PRAESENS.value,  # "praesens": "Präsens"
        SkillType.PRAETERITUM.value: Tense.PRAETERITUM.value,  # "praeteritum": "Präteritum"
        SkillType.PERFEKT.value: Tense.PERFEKT.value,  # "perfekt": "Perfekt"
    }

    def get_correct_answer(self, verb, atom, language=None) -> str:
        raise NotImplementedError

    def get_distractors(self, verb, atom, unit_verbs, language=None, limit=3) -> list[str]:
        raise NotImplementedError