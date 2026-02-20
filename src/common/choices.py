from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _


class LanguageCode(Enum):
    EN = "en"
    RU = "ru"
    UK = "uk"

    @classmethod
    def choices(cls):
        return [
            (cls.EN.value, _("Englisch")),
            (cls.RU.value, _("Russisch")),
            (cls.UK.value, _("Ukrainisch")),
        ]

    @classmethod
    def get_available_values(cls):
        return [attr.value for attr in cls]


class Tense(Enum):
    PRAESENS = "Präsens"
    PRAETERITUM = "Präteritum"
    PERFEKT = "Perfekt"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

class VerbType(Enum):
    REGULAR = "reg"
    STRONG = "str"
    MIXED = "mix"

    @classmethod
    def choices(cls):
        return [
            (cls.REGULAR.value, _("schwach")),
            (cls.STRONG.value, _("stark")),
            (cls.MIXED.value, _("gemischt")),
        ]

    @classmethod
    def get_available_values(cls):
        return [attr.value for attr in cls]

class Reflexiv(Enum):
    NREFL = "nrefl"
    REFL = "refl"
    EREFL = "erefl"

    @classmethod
    def choices(cls):
        return [
            (cls.NREFL.value, _("nicht reflexiv")),
            (cls.REFL.value, _("unechte reflexiv")),
            (cls.EREFL.value, _("echte reflexiv")),
        ]

    @classmethod
    def get_available_values(cls):
        return [attr.value for attr in cls]

class CEFRLevel(Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

class GermanCase(Enum):
    NOM = "Nominativ"
    AKK = "Akkusativ"
    DAT = "Dativ"
    GEN = "Genitiv"

    @classmethod
    def choices(cls):
        return [(i.name, i.value) for i in cls]

class PrepositionCaseRequirement(Enum):
    AKK = "Akkusativ"
    DAT = "Dativ"
    GEN = "Genitiv"
    MIXED = "gemischt"

    @classmethod
    def choices(cls):
        return [(i.name, i.value) for i in cls]

class AuxiliaryVerb(Enum):
    HABEN = "haben"
    SEIN = "sein"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

class Pronoun(Enum):
    ICH = "ich"
    DU = "du"
    ER = "er/sie/es"
    WIR = "wir"
    IHR = "ihr"
    SIE = "sie"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

    @classmethod
    def get_attr_by_value(cls, value: str):
        for attr in cls:
            if attr.value == value:
                return attr
        return None

    @classmethod
    def get_available_values(cls):
        return [attr.value for attr in cls]

class AuxiliaryConjugation:
    _forms = {
        AuxiliaryVerb.HABEN: {
            Pronoun.ICH: "habe",
            Pronoun.DU: "hast",
            Pronoun.ER: "hat",
            Pronoun.WIR: "haben",
            Pronoun.IHR: "habt",
            Pronoun.SIE: "haben",
        },
        AuxiliaryVerb.SEIN: {
            Pronoun.ICH: "bin",
            Pronoun.DU: "bist",
            Pronoun.ER: "ist",
            Pronoun.WIR: "sind",
            Pronoun.IHR: "seid",
            Pronoun.SIE: "sind",
        }
    }

    @classmethod
    def get(cls, auxiliary: AuxiliaryVerb, pronoun: Pronoun) -> str:
        return cls._forms[auxiliary][pronoun]

# class SkillType(Enum):
#     TRANS = "translation"
#     RU = "praesens"
#     UK = "uk"
#
#     @classmethod
#     def choices(cls):
#         return [
#             (cls.EN.value, _("Englisch")),
#             (cls.RU.value, _("Präsens")),
#             (cls.UK.value, _("Ukrainisch")),
#             (cls.UK.value, _("Ukrainisch")),
#         ]
#
#     @classmethod
#     def get_available_values(cls):
#         return [attr.value for attr in cls]

class SkillType(models.TextChoices):
    TRANSLATION = "translation", "Translation"
    PRAESENS = "praesens", "Präsens"
    PRAETERITUM = "praeteritum", "Präteritum"
    PERFEKT = "perfekt", "Perfekt"