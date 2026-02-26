from src.common.choices import SkillType
from src.personal_forms.services.resolvers import (
    TranslationResolver,
    SimpleConjugationResolver,
    PerfektResolver,
)

SKILL_RESOLVERS = {
    SkillType.TRANSLATION: TranslationResolver(),
    SkillType.PRAESENS: SimpleConjugationResolver(),
    SkillType.PRAETERITUM: SimpleConjugationResolver(),
    SkillType.PERFEKT: PerfektResolver(),
    # Если завтра добавишь SkillType.PREPOSITIONS, просто допишешь одну строку здесь
}