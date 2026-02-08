from enum import Enum

class VerbType(Enum):
    REGULAR = "regular"
    STRONG = "strong"
    MIXED = "mixed"

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

class Tense(Enum):
    PRAESENS = "Präsens"
    PRAETERITUM = "Präteritum"
    PERFEKT = "Perfekt"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]

class AuxiliaryVerb(Enum):
    HABEN = "haben"
    SEIN = "sein"

    @classmethod
    def choices(cls):
        return [(i.value, i.value) for i in cls]
