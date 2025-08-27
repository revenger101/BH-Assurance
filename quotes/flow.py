import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

@dataclass
class Field:
    key: str
    question: str
    parser: Any
    required: bool = True


def parse_choice(choices):
    mapping = {c.lower(): c for c in choices}
    def _parser(txt: str):
        if not txt:
            return None, "Merci de préciser votre choix."
        val = txt.strip().lower()
        # accept accents variations
        aliases = {
            'vie': 'vie',
            'santé': 'sante', 'sante': 'sante',
            'auto': 'auto',
            'habitation': 'habitation'
        }
        if val in mapping:
            return mapping[val], None
        if val in aliases and aliases[val] in mapping:
            return mapping[aliases[val]], None
        return None, f"Choix invalide. Options: {', '.join(choices)}."
    return _parser


def parse_int(min_v=None, max_v=None):
    def _parser(txt: str):
        if not txt:
            return None, "Valeur requise."
        try:
            v = int(re.sub(r"[^0-9]", "", txt))
        except Exception:
            return None, "Veuillez indiquer un nombre entier."
        if min_v is not None and v < min_v:
            return None, f"La valeur doit être ≥ {min_v}."
        if max_v is not None and v > max_v:
            return None, f"La valeur doit être ≤ {max_v}."
        return v, None
    return _parser


def parse_yes_no(txt: str):
    if not txt:
        return None, "Répondez par oui/non."
    v = txt.strip().lower()
    if v in {"oui", "o", "yes", "y"}:
        return True, None
    if v in {"non", "n", "no"}:
        return False, None
    return None, "Répondez par oui ou non."

# Conversation fields
FIELDS = [
    Field(
        key="produit",
        question="Quel produit souhaitez-vous assurer ? (vie, auto, sante, habitation)",
        parser=parse_choice(["vie", "auto", "sante", "habitation"]),
    ),
    Field(
        key="age",
        question="Quel est votre âge ?",
        parser=parse_int(18, 80),
    ),
    Field(
        key="capital",
        question="Quel capital à assurer (en TND) ?",
        parser=parse_int(1000, 1000000),
    ),
    Field(
        key="duree",
        question="Quelle durée d'assurance (en années) ?",
        parser=parse_int(1, 40),
    ),
    Field(
        key="fumeur",
        question="Êtes-vous fumeur ? (oui/non)",
        parser=parse_yes_no,
    ),
]


def get_next_field(collected: Dict[str, Any]) -> Optional[Field]:
    for f in FIELDS:
        if f.required and f.key not in collected:
            return f
    return None


def simulate_quote(payload: Dict[str, Any]) -> Dict[str, Any]:
    produit = payload["produit"].lower()
    age = payload["age"]
    capital = payload["capital"]
    duree = payload["duree"]
    fumeur = payload["fumeur"]

    # Very simple premium model per product
    base_rate = {
        "vie": 0.0025,
        "auto": 0.015,
        "sante": 0.010,
        "habitation": 0.006,
    }[produit]

    risk_factor = 1.0
    if produit == "vie":
        risk_factor *= 1.0 + max(0, age - 30) * 0.02
        if fumeur:
            risk_factor *= 1.25
    elif produit == "auto":
        risk_factor *= 1.0 + max(0, (age < 25) * 0.3)
    elif produit == "sante":
        risk_factor *= 1.0 + max(0, age - 40) * 0.015
    elif produit == "habitation":
        risk_factor *= 1.0

    duration_factor = 1.0 - min(duree, 20) * 0.01

    annual_premium = capital * base_rate * risk_factor * duration_factor
    monthly_premium = round(annual_premium / 12, 2)
    annual_premium = round(annual_premium, 2)

    return {
        "produit": produit,
        "capital": capital,
        "age": age,
        "duree": duree,
        "fumeur": fumeur,
        "prime_mensuelle": monthly_premium,
        "prime_annuelle": annual_premium,
        "devise": "TND",
        "hypotheses": {
            "taux_de_base": base_rate,
            "facteur_risque": round(risk_factor, 3),
            "facteur_duree": round(duration_factor, 3),
        }
    }

