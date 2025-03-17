import streamlit as st


def setup_colors():
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
        color: #555555;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    return None


COLOR_DICT = {
    " plan ": "coopHighlight",
    "land": "orangeHighlight",
    "initiator": "initHighlight",
    "applicant": "initHighlight",
    "developer": "initHighlight",
    "cost": "redHighlight",
    "expense": "redHighlight",
    "fee": "redHighlight",
    "risk": "redHighlight",
    "operating plan": "purpleHighlight",
    "operating": "purpleHighlight",
    "exploitation": "purpleHighlight",
    "agreement": "greenHighlight",
    "Agreement": "greenHighlight",
    "contract": "greenHighlight",
    "sell": "sellHighlight",
    "sale": "sellHighlight",
    "price": "sellHighlight",
    "buy": "sellHighlight",
    "purchase": "sellHighlight",
    " owned": "ownHighlight",
    " owns ": "ownHighlight",
    " owner ": "ownHighlight",
    " owners ": "ownHighlight",
    "issuance": "issueHighlight",
    " issue": "issueHighlight",
    " issuing": "issueHighlight",
    "building plan": "buildingplanHighlight",
    "anterior": "anteriorHighlight",
    "Anterior": "anteriorHighlight",
    "Anterieure": "anteriorHighlight",
    "anterieure": "anteriorHighlight",
    "scheme": "schemeHighlight",
    "project": "schemeHighlight",
    "budget": "budgetHighlight",
    "municipality": "budgetHighlight",
    "conservative": "conservativeHighlight",
    "cooperation": "coopHighlight",
    "Cooperation": "coopHighlight",
    "damage": "damageHighligh",
    "damages": "damageHighligh",
    "space for space": "budgetHighlight",
    "Space for Space": "budgetHighlight",
    " realisation ": "purpleHighlight",
    "Realisation ": "purpleHighlight",
}
