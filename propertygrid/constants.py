from enum import Enum


class Undefined: pass
class UndefinedBool(Undefined): pass
class UndefinedInt(Undefined): pass
class UndefinedFloat(Undefined): pass
class UndefinedString(Undefined): pass
class UndefinedEnum(Undefined, Enum): pass
class UndefinedColour(Undefined): pass
class UndefinedImage(Undefined): pass
class UndefinedGradient(Undefined): pass
