from .normalizers.tottus_normalizer import TottusNormalizer
from .normalizers.ripley_normalizer import RipleyNormalizer
from .normalizers.oechsle_normalizer import OechsleNormalizer
from .normalizers.tailoy_normalizer import TaiLoyNormalizer
from .normalizers.estilos_normalizer import EstilosNormalizer
from .normalizers.falabella_normalizer import FalabellaNormalizer
from .normalizers.cencosud_normalizer import CencosudNormalizer

class NormalizerFactory:
    @staticmethod
    def create_all():
        return {
            "TOTTUS": TottusNormalizer(),
            "RIPLEY": RipleyNormalizer(),
            "OECHSLE": OechsleNormalizer(),
            "TAI LOY": TaiLoyNormalizer(),
            "ESTILOS": EstilosNormalizer(),
            "SAGA FALABELLA": FalabellaNormalizer(),
            "CENCOSUD": CencosudNormalizer()
        }