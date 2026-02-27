from src.common.choices import SkillType
from src.personal_forms.services.resolvers.translation import TranslationResolver
from src.personal_forms.services.resolvers.conjugation import SimpleConjugationResolver
from src.personal_forms.services.resolvers.perfekt import PerfektResolver


SKILL_RESOLVERS = {
    SkillType.TRANSLATION: TranslationResolver(),
    SkillType.PRAESENS: SimpleConjugationResolver(),
    SkillType.PRAETERITUM: SimpleConjugationResolver(),
    SkillType.PERFEKT: PerfektResolver(),
    # Если завтра добавишь SkillType.PREPOSITIONS, просто допишешь одну строку здесь
}