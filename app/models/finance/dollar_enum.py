
from enum import Enum


class DollarCategory(Enum):
    MAYORISTA = 'mayorista'
    OFICIAL = 'oficial'
    AHORRO = 'ahorro'
    TARJETA = 'tarjeta'
    BLUE = 'blue'
    CRIPTO = 'cripto'
    MEP = 'mep'
    CCL = 'ccl'

class Bond(Enum):
    AL30 = 'al30'
    GD30 = 'gd30'

class BondTime(Enum):
    DAY = '24hs'
    CI = 'ci'