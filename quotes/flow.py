import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

@dataclass
class Field:
    key: str
    question: str
    parser: Any
    required: bool = True
    product_specific: Optional[str] = None  # 'auto', 'vie', etc.


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


def parse_cin(txt: str):
    """Parse Tunisian CIN number"""
    if not txt:
        return None, "Numéro CIN requis."
    # Remove spaces and non-digits
    cin = re.sub(r"[^0-9]", "", txt.strip())
    if len(cin) != 8:
        return None, "Le numéro CIN doit contenir 8 chiffres."
    return cin, None


def parse_date(txt: str):
    """Parse date in various formats"""
    if not txt:
        return None, "Date requise."

    txt = txt.strip()
    # Try different date formats
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formats:
        try:
            date_obj = datetime.strptime(txt, fmt)
            return date_obj.strftime("%Y-%m-%d"), None
        except ValueError:
            continue

    return None, "Format de date invalide. Utilisez: YYYY-MM-DD, DD/MM/YYYY, ou DD-MM-YYYY."


def parse_contract_nature(txt: str):
    """Parse contract nature"""
    if not txt:
        return None, "Nature du contrat requise."

    val = txt.strip().lower()
    mapping = {
        'r': 'r',  # renouvellement
        'renouvellement': 'r',
        'nouveau': 'n',
        'n': 'n'
    }

    if val in mapping:
        return mapping[val], None

    return None, "Nature du contrat: 'r' pour renouvellement, 'n' pour nouveau contrat."

# Conversation fields - now product-specific
FIELDS = [
    # Common field - product selection
    Field(
        key="produit",
        question="Quel produit souhaitez-vous assurer ? (auto, vie, sante, habitation)",
        parser=parse_choice(["auto", "vie", "sante", "habitation"]),
    ),

    # AUTO INSURANCE FIELDS (for real API)
    Field(
        key="n_cin",
        question="Quel est votre numéro CIN (8 chiffres) ?",
        parser=parse_cin,
        product_specific="auto"
    ),
    Field(
        key="valeur_venale",
        question="Quelle est la valeur vénale du véhicule (en TND) ?",
        parser=parse_int(1000, 500000),
        product_specific="auto"
    ),
    Field(
        key="nature_contrat",
        question="Nature du contrat ? (r = renouvellement, n = nouveau)",
        parser=parse_contract_nature,
        product_specific="auto"
    ),
    Field(
        key="nombre_place",
        question="Nombre de places du véhicule ?",
        parser=parse_int(2, 9),
        product_specific="auto"
    ),
    Field(
        key="valeur_a_neuf",
        question="Quelle est la valeur à neuf du véhicule (en TND) ?",
        parser=parse_int(1000, 500000),
        product_specific="auto"
    ),
    Field(
        key="date_premiere_mise_en_circulation",
        question="Date de première mise en circulation (YYYY-MM-DD) ?",
        parser=parse_date,
        product_specific="auto"
    ),
    Field(
        key="capital_bris_de_glace",
        question="Capital bris de glace souhaité (en TND) ? (ex: 900)",
        parser=parse_int(100, 5000),
        product_specific="auto"
    ),
    Field(
        key="capital_dommage_collision",
        question="Capital dommage collision (en TND) ? (généralement = valeur vénale)",
        parser=parse_int(1000, 500000),
        product_specific="auto"
    ),
    Field(
        key="puissance",
        question="Puissance du véhicule (en CV) ?",
        parser=parse_int(3, 20),
        product_specific="auto"
    ),
    Field(
        key="classe",
        question="Classe du véhicule ? (1-5, généralement 3 pour véhicule standard)",
        parser=parse_int(1, 5),
        product_specific="auto"
    ),

    # LIFE INSURANCE FIELDS (simplified for other products)
    Field(
        key="age",
        question="Quel est votre âge ?",
        parser=parse_int(18, 80),
        product_specific="vie"
    ),
    Field(
        key="capital",
        question="Quel capital à assurer (en TND) ?",
        parser=parse_int(1000, 1000000),
        product_specific="vie"
    ),
    Field(
        key="duree",
        question="Quelle durée d'assurance (en années) ?",
        parser=parse_int(1, 40),
        product_specific="vie"
    ),
    Field(
        key="fumeur",
        question="Êtes-vous fumeur ? (oui/non)",
        parser=parse_yes_no,
        product_specific="vie"
    ),

    # HEALTH INSURANCE FIELDS
    Field(
        key="age",
        question="Quel est votre âge ?",
        parser=parse_int(18, 80),
        product_specific="sante"
    ),
    Field(
        key="capital",
        question="Quel capital santé souhaité (en TND) ?",
        parser=parse_int(5000, 100000),
        product_specific="sante"
    ),

    # HOME INSURANCE FIELDS
    Field(
        key="valeur_bien",
        question="Quelle est la valeur du bien à assurer (en TND) ?",
        parser=parse_int(10000, 2000000),
        product_specific="habitation"
    ),
    Field(
        key="superficie",
        question="Superficie du logement (en m²) ?",
        parser=parse_int(20, 1000),
        product_specific="habitation"
    ),
]


def get_next_field(collected: Dict[str, Any]) -> Optional[Field]:
    """Get the next required field based on collected data and product type"""
    selected_product = collected.get("produit")

    for f in FIELDS:
        if not f.required:
            continue

        # Skip if field already collected
        if f.key in collected:
            continue

        # If no product selected yet, only return the product field
        if not selected_product and f.key != "produit":
            continue

        # If product is selected, only return fields for that product or common fields
        if selected_product and f.product_specific and f.product_specific != selected_product:
            continue

        return f

    return None


def simulate_quote(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate quote for non-auto products or fallback"""
    produit = payload["produit"].lower()

    if produit == "auto":
        # For auto, return a basic structure since real API should be used
        return {
            "produit": "auto",
            "message": "Devis auto simulé - API externe recommandée",
            "prime_estimee": "À calculer via API externe",
            "parametres": payload
        }

    # For other products, use simple calculation
    age = payload.get("age", 30)
    capital = payload.get("capital", payload.get("valeur_bien", 50000))
    duree = payload.get("duree", 10)
    fumeur = payload.get("fumeur", False)

    # Simple premium model for non-auto products
    base_rate = {
        "vie": 0.0025,
        "sante": 0.010,
        "habitation": 0.006,
    }.get(produit, 0.005)

    risk_factor = 1.0
    if produit == "vie":
        risk_factor *= 1.0 + max(0, age - 30) * 0.02
        if fumeur:
            risk_factor *= 1.25
    elif produit == "sante":
        risk_factor *= 1.0 + max(0, age - 40) * 0.015
    elif produit == "habitation":
        superficie = payload.get("superficie", 100)
        risk_factor *= 1.0 + (superficie / 1000)

    duration_factor = 1.0 - min(duree, 20) * 0.01 if duree else 1.0

    annual_premium = capital * base_rate * risk_factor * duration_factor
    monthly_premium = round(annual_premium / 12, 2)
    annual_premium = round(annual_premium, 2)

    return {
        "produit": produit,
        "capital": capital,
        "prime_mensuelle": monthly_premium,
        "prime_annuelle": annual_premium,
        "devise": "TND",
        "parametres_utilises": payload,
        "hypotheses": {
            "taux_de_base": base_rate,
            "facteur_risque": round(risk_factor, 3),
            "facteur_duree": round(duration_factor, 3),
        }
    }

