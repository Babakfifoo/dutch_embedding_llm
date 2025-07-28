import streamlit as st
from typing import Dict, List
from ollama import ChatResponse, chat
from pydantic import BaseModel

LLM_MODEL: str = "gemma3:4b"


def colorise(s: str) -> str:
    for k, v in COLOR_DICT.items():
        s = s.replace(k, f'<span class="{v}">{k}</span>')
        s = s.replace("story", "recovery")
    return s


def setup_colors() -> None:
    st.set_page_config(layout="wide")

    st.markdown(
        """
    <style>
    .orangeHighlight {
        color: #FFA500;
    }
    .initHighlight {
        color: #FFFF00;
    }
    .redHighlight {
        color:  #FF0000;
    }
    .sellHighlight {
        color:  #ff00ff ;
    }
    .issueHighlight {
        color:  #168f9c ;
    }
    .buildingplanHighlight {
        color:  #afc87d;
    }
    .damageHighligh {
        color: #90a955;
    }
    .purpleHighlight {
        color:  #2f6e5e;
    }
    .greenHighlight {
        color:  #00ff00;
    }
    .anteriorHighlight {
        color:  #00dd66;
    }
    .coopHighlight {
        color:  #e9ff70;
    }
    .plabHighlight {
        color: #9dd9d2
    }
    .ownHighlight {
        color:  #7dafc8;
    }
    .schemeHighlight {
        color:  #00a0c8;
    }
    .budgetHighlight {
        color:  #FF0088;
    }
    .conservativeHighlight {
        color: #999999;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    return None


COLOR_DICT: Dict[str, str] = {
    " plan ": "coopHighlight",
    "land": "orangeHighlight",
    "initiator": "initHighlight",
    "applicant": "initHighlight",
    "developer": "initHighlight",
    "proposer": "initHighlight",
    "cost": "redHighlight",
    "expense": "redHighlight",
    "fee": "redHighlight",
    "emptying": "redHighlight",
    "empty ": "redHighlight",
    "regulation": "orangeHighlight",
    "risk": "redHighlight",
    "operating plan": "purpleHighlight",
    "operating": "purpleHighlight",
    "exploitation": "purpleHighlight",
    "agreement": "greenHighlight",
    "Agreement": "greenHighlight",
    "contract": "greenHighlight",
    "sell": "sellHighlight",
    "sold": "sellHighlight",
    "sale": "sellHighlight",
    "price": "sellHighlight",
    "buy": "sellHighlight",
    "purchase": "sellHighlight",
    " owned": "ownHighlight",
    " owns ": "ownHighlight",
    " owner ": "ownHighlight",
    " owners ": "ownHighlight",
    "ownership ": "ownHighlight",
    "issuance": "issueHighlight",
    " issue": "issueHighlight",
    " issuing": "issueHighlight",
    "building plan": "buildingplanHighlight",
    "anterior": "anteriorHighlight",
    "Anterior": "anteriorHighlight",
    "Anterieure": "anteriorHighlight",
    "anterieure": "anteriorHighlight",
    "private-law": "anteriorHighlight",
    "scheme": "schemeHighlight",
    "project": "schemeHighlight",
    "budget": "budgetHighlight",
    "municipality": "budgetHighlight",
    "Municipality": "budgetHighlight",
    "conservative": "conservativeHighlight",
    "conservation": "conservativeHighlight",
    "already": "conservativeHighlight",
    "developed": "conservativeHighlight",
    "cooperation": "coopHighlight",
    "Cooperation": "coopHighlight",
    "damage": "damageHighligh",
    "damages": "damageHighligh",
    " plan-damaging ": "damageHighligh",
    "space for space": "budgetHighlight",
    "space-for-space": "budgetHighlight",
    "Space for Space": "budgetHighlight",
    "Space-for-Space": "budgetHighlight",
    "realisation ": "purpleHighlight",
    "Realisation ": "purpleHighlight",
    "promoter": "initHighlight",
    "will": "redHighlight",
    "borne ": "redHighlight",
    "expence": "redHighlight",
    "foundation": "coopHighlight",
    "association": "coopHighlight",
    "housing corporation": "coopHighlight",
    "housing foundation": "coopHighlight",
    "Housing Foundation": "coopHighlight",
    "Housing Corporation": "coopHighlight",
}

DAS: Dict[str, str] = {
    "AA": "Anterior agreement",
    "EA": "Exploitation agreement",
    "PDA": "Plan damage agreement",
    "GA": "General agreement",
    "CRA": "Cost recovery agreement",
    "RA": "Realisation agreement",
    "PA": "Private buys public land, Purchase agreement",
    "PPA": "Public buys, Purchase agreement",
    "LSA": "Land sale agreement",
    "CA": "Cooperation agreement",
    "SFS": "Space-for-Space agreement",
    "DAA": "Area agreement",
    "BLP": "Building Plan",
    "PHD": "Private housing development",
    "MHD": "Municipality housing development",
}

INDICATORS: Dict[str, str] = {
    "DCP": "Development Contributions Plans (DCP)",
    "LI": "Municipal land issue",
    "LS": "Municipal land/plot sale",
    "LP": "Municipal land price",
    "MUL": "Municipality land / land development",
    "INI": "Initiator/private party covers costs",
    "FEE": "Levies and Fees",
    "PPP": "Public Private Partnership (PPP)",
    "PB": "Public Budget",
    "MUN": "Municipality budget",
    "MDF": "Municipality land dev. financing",
    "HS": "Housing association",
    "CO": "Conservative / no development / update plan",
    "LES": "Land Exploitation Scheme",
    "K10": "Less than 10,00€ cost",
    "PDP": "Partly PLD",
    "DUO": "Both DA and PLD",
    "INV": "Invalid",
}


def ask_LLM(
    prompt: str,
    response_format="",
    model: str = LLM_MODEL,
) -> ChatResponse:
    return chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=dict(
            temperature=0.0,  # reducing the variability of the answer
            seed=2025,  # Setting the Seed for prediction and reproducability
            top_k=10,  # More conservative answer
            min_p=0.9,  # minimum probability of token to be considered.
            main_gpu=2,
            num_thread=4,
        ),
        format=response_format,
    )


def bool_cleaner(s: str) -> bool | None:
    # Validates and corrects the answer to Bool. None values are also returned False.
    if not isinstance(s, str):
        return None
    if "true" in s.lower():
        return True
    if "false" in s.lower():
        return False
    return None


class BoolAnswer(BaseModel):
    ans: bool
