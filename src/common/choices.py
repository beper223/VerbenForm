from enum import Enum


class Tense(Enum):
    PRAESENS = "Präsens"
    PRAETERITUM = "Präteritum"
    PERFEKT = "Perfekt"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

class VerbType(Enum):
    REGULAR = "schwach"
    STRONG = "stark"
    MIXED = "gemischt"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

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
