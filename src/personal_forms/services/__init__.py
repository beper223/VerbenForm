# src/personal_forms/services/
# ├── resolvers/             # Папка со стратегиями
# │   ├── registry.py        # Реестр SKILL_RESOLVERS
# │   ├── base.py
# │   ├── translation.py
# │   ├── conjugation.py
# │   └── perfekt.py
# ├── training_engine.py      # Выбор следующего слова (Engine)
# ├── training_service.py     # Оркестратор процесса
# ├── card_factory.py         # Сборка карточки из резолверов
# ├── progress_service.py     # Запись ответов в БД + сброс кеша
# └── learning_unit_progress_service.py  # (Для UI) Показ общей статистики

from src.personal_forms.services.learning_unit_progress_service import LearningUnitProgressService
from src.personal_forms.services.progress_service import ProgressService
from src.personal_forms.services.training_engine import CachedTrainingEngine
from src.personal_forms.services.training_service import TrainingService
from src.personal_forms.services.card_factory import CardFactory
from src.personal_forms.services.resolvers.registry import SKILL_RESOLVERS

__all__ = [
    "LearningUnitProgressService",
    "ProgressService",
    "CachedTrainingEngine",
    "TrainingService",
    "CardFactory",
    "SKILL_RESOLVERS",
]