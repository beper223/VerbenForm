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
