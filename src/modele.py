"""Optimisation de l'assolement d'une exploitation irriguee du Tadla (Maroc).

Programmation lineaire : le modele choisit les surfaces (ha) de chaque culture pour
maximiser la marge brute, sous contraintes de surface, d'eau, de rotation et de part
minimale de cereales. Chaque parametre de data/parametres.csv est accompagne de sa
source et d'un statut de qualite (source, derive, ancien, hypothese).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pulp

RACINE = Path(__file__).resolve().parent.parent
PART_MIN_CEREALES = 0.20  # hypothese : au moins 20 % de la surface en cereales
EAU_SECHERESSE_M3_HA = 3000  # dotation moyenne actuelle (Medias24)


def charger_donnees():
    long = pd.read_csv(RACINE / "data" / "parametres.csv")
    cultures = long.pivot(index="culture", columns="parametre", values="valeur")
    cultures = cultures.join(pd.read_csv(RACINE / "data" / "cultures.csv", index_col="culture"))
    cultures["prime_etat_mad_t"] = cultures["prime_etat_mad_t"].fillna(0.0)
    ressources = pd.read_csv(RACINE / "data" / "ressources.csv", index_col="ressource")
    return cultures, ressources["disponibilite"].to_dict(), long


def rapport_qualite(long):
    """Resume la qualite des donnees : a lire avant toute interpretation."""
    resume = long.groupby("statut").size().rename("nb_parametres")
    a_valider = long[long["statut"].isin(["hypothese", "ancien"])]
    return resume, a_valider[["culture", "parametre", "valeur", "statut", "annee"]]


def marge_brute(cultures):
    """Marge brute par hectare = rendement x (prix + prime) - charges."""
    prix_effectif = cultures["prix_mad_t"] + cultures["prime_etat_mad_t"]
    return cultures["rendement_t_ha"] * prix_effectif - cultures["charges_mad_ha"]


def resoudre(cultures, ressources):
    mb = marge_brute(cultures)
    modele = pulp.LpProblem("assolement", pulp.LpMaximize)
    x = {c: pulp.LpVariable(f"x_{c}", lowBound=0) for c in cultures.index}

    modele += pulp.lpSum(mb[c] * x[c] for c in x), "marge_brute_totale"
    modele += pulp.lpSum(x.values()) <= ressources["surface"], "surface"
    modele += pulp.lpSum(cultures.loc[c, "eau_m3_ha"] * x[c] for c in x) <= ressources["eau"], "eau"
    cereales = [c for c in x if cultures.loc[c, "groupe"] == "cereale"]
    modele += (
        pulp.lpSum(x[c] for c in cereales) >= PART_MIN_CEREALES * ressources["surface"],
        "cereales_min",
    )
    for c in x:
        plafond = cultures.loc[c, "max_ha"]
        if pd.notna(plafond):
            modele += x[c] <= plafond, f"plafond_{c}"

    modele.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[modele.status] != "Optimal":
        raise RuntimeError(f"Pas de solution optimale : {pulp.LpStatus[modele.status]}")
    surfaces = {c: x[c].value() for c in x}
    duaux = {nom: ct.pi for nom, ct in modele.constraints.items()}
    return surfaces, pulp.value(modele.objective), duaux


def scenarios():
    cultures, ressources, long = charger_donnees()
    defs = {"base": (cultures, ressources)}

    secheresse = dict(ressources, eau=EAU_SECHERESSE_M3_HA * ressources["surface"])
    defs["secheresse_3000_m3_ha"] = (cultures, secheresse)

    ble = cultures.copy()
    ble.loc["ble_tendre", "prix_mad_t"] = 2700  # prix de reference 270 DH/q (campagne 2024/25)
    defs["ble_270_dh_q"] = (ble, ressources)

    sans_prime = cultures.copy()
    sans_prime.loc["betterave", "prime_etat_mad_t"] = 0.0
    defs["sans_prime_betterave"] = (sans_prime, ressources)

    lignes = []
    for nom, (cult, res) in defs.items():
        surfaces, marge, duaux = resoudre(cult, res)
        ligne = {"scenario": nom, "marge_brute_mad": round(marge)}
        ligne.update({f"ha_{c}": round(v, 2) for c, v in surfaces.items()})
        ligne["valeur_eau_mad_m3"] = round(duaux["eau"], 3) + 0.0
        ligne["valeur_terre_mad_ha"] = round(duaux["surface"]) + 0
        lignes.append(ligne)
    return pd.DataFrame(lignes)


def tracer(resultats):
    colonnes = [c for c in resultats.columns if c.startswith("ha_")]
    ax = resultats.set_index("scenario")[colonnes].rename(columns=lambda c: c[3:]).plot(
        kind="bar", stacked=True, figsize=(9, 5)
    )
    ax.set_ylabel("Surface (ha)")
    ax.set_title("Assolement optimal selon le scenario (exploitation type, Tadla)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(RACINE / "results" / "assolement.png", dpi=150)


if __name__ == "__main__":
    _, _, long = charger_donnees()
    resume, a_valider = rapport_qualite(long)
    print("QUALITE DES DONNEES\n", resume.to_string(), "\n")
    print("A valider / actualiser :\n", a_valider.to_string(index=False), "\n")
    resultats = scenarios()
    resultats.to_csv(RACINE / "results" / "scenarios.csv", index=False)
    tracer(resultats)
    pd.set_option("display.width", 220)
    print(resultats.T.to_string(header=False))
