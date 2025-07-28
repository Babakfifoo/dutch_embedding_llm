# %%

active_plan = {
    "IMRO": "t_NL.IMRO.0342.BPSTB0019-0301",
    "id": [
        "3: 0",
        "3: 1",
        "3: 2",
        "3: 3",
        "3: 4",
        "5: 0",
        "5: 1",
        "7: 0",
        "7: 1",
        "7: 2",
        "9: 0",
        "9: 1",
        "9: 2",
        "11: 0",
        "13: 0",
    ],
    "nl": [
        "Bij de voorbereiding van een ontwerp voor een bestemmingsplan dient op grond van artikel 3.1.6 van het Besluit ruimtelijke ordening (Bro) in de plantoelichting van een bestemmingsplan minimaal inzicht te worden gegeven in de uitvoerbaarheid van het plan.",
        "Tevens is ingevolge de Wet ruimtelijke ordening (Wro) verplicht om, indien sprake is van ontwikkelingen waarvoor de gemeente redelijkerwijs kosten moet maken, onder meer voor de aanleg van voorzieningen van openbaar nut, deze moeten kunnen worden verhaald op de initiatiefnemer c.q. ontwikkelaar.",
        "Een en ander dient vast te worden gelegd in een grondexploitatie.",
        "De ontwikkeling van het braakliggende terrein in Soesterberg is een initiatief van de gemeente Soest zoals vastgesteld in het Masterplan Soesterberg.",
        "De financiële uitvoerbaarheid en realisatie van de bestemmingswijzigingen in het bestemmingsplangebied zijn middels (intentie)overeenkomsten met deelnemende partijen beschikbaar en opgenomen in de grondexploitatie Masterplan Soesterberg.",
        "Mede met het oog op de financiële haalbaarheid van het plan is het terrein mede aangewezen voor woningbouw.",
        "In totaal wordt rekening gehouden met circa 122 grondgebonden en gestapelde woningen.",
        "De kosten zijn realistisch geraamd op basis van de globale inrichtingsschetsen van het plangebied.",
        "Daarin zijn begrepen de kosten van tijdelijk beheer, slopen, saneren, (her)inrichting van groen en verharding, bouwrijp en woonrijp maken van de woongebieden, planvorming en de rentelasten.",
        "De omvang en samenstelling van het bouwprogramma is afgestemd op een positief resultaat.",
        "De bouw van de woningen is gepland in de periode 2017 tot 2020.",
        "De fasering van het bouwrijp en woonrijp maken is hieraan gerelateerd.",
        "De financiële effecten van de fasering als gevolg van rentekosten en loon- en prijsstijgingen zijn in de kostenramingen verdisconteerd.",
        "In de grondexploitatie wordt uitgegaan van een positief resultaat.",
        "De grootste risico's voor de in dit plan genoemde ontwikkelingen zijn: ",
    ],
    "en": [
        "When preparing a plan for a zoning plan, a minimum understanding of the feasibility of the plan should be provided in the Explanatory Memorandum of a zoning plan pursuant to Article 3.1.6 of the zoning decision.",
        "In addition, if there are developments for which the municipality should reasonably incur costs, including for the construction of public utility facilities, the Regional Planning Act (Wro) also requires that these be recovered from the initiator and/or developer.",
        "This should be recorded in land exploitation.",
        "The development of the set-aside site in Soesterberg is an initiative of the municipality of Soest as established in the Masterplan Soesterberg.",
        "The financial feasibility and realisation of the land use changes in the zoning area are available through (intention) agreements with participating parties and included in the land exploitation Masterplan Soesterberg.",
        "In view of the financial feasibility of the plan, the site is also designated for housing.",
        "A total of some 122 land-related and stacked dwellings are taken into account.",
        "The cost has been realistically estimated on the basis of the overall layout sketches of the planning area.",
        "This includes the cost of temporary management, demolition, repairing, (re-) construction of green and pavement, preparation and housing of residential areas, planning and interest charges.",
        "The size and composition of the construction programme is geared to a positive result.",
        "The construction of the houses is planned for the period 2017 to 2020.",
        "The phasering of building and housing is related to this.",
        "The financial effects of phasing due to interest costs and wage and price increases have been taken into account in the cost estimates.",
        "Land exploitation is based on a positive result.",
        "The main risks to the developments identified in this plan are:",
    ],
}
# %%
para_id = [x.split(":")[0] for x in active_plan.get("id")]


# %%
def merge_sentences(paragraph_ids, sentences):
    merged_paragraphs = {}

    for pid, sentence in zip(paragraph_ids, sentences):
        if pid in merged_paragraphs:
            merged_paragraphs[pid] += " " + sentence
        else:
            merged_paragraphs[pid] = sentence

    return merged_paragraphs


# %%
merge_sentences(para_id, active_plan.get("en"))
# %%
