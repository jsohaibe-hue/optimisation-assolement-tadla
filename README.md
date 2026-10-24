# Optimisation de l'assolement d'une exploitation irriguée du Tadla (Maroc)

Modèle de programmation linéaire (Python, PuLP) qui détermine l'assolement maximisant la
marge brute d'une exploitation type de 10 ha dans le périmètre irrigué du Tadla (ORMVAT),
puis teste des scénarios de sécheresse, de prix et de politique agricole.

> **Statut : version 0.1, données partiellement sourcées.**
> Chaque paramètre de `data/parametres.csv` porte sa source, son année et un statut de qualité.
> Les résultats ne doivent pas être interprétés tant que les paramètres `hypothese` et
> `ancien` n'ont pas été remplacés (voir « Qualité des données »).

## Problème
Face à la baisse de la dotation en eau d'irrigation, comment une exploitation de 10 ha du
Tadla doit-elle adapter son assolement, et quelle est la valeur économique d'un m³ d'eau
supplémentaire ?

## Modèle
- **Variables :** surface x_c (ha) de chaque culture c.
- **Objectif :** maximiser Σ MB_c · x_c, avec MB_c = rendement × (prix + prime de l'État) − charges.
- **Contraintes :** surface ≤ 10 ha ; eau ≤ volume disponible ; betterave ≤ plafond de rotation ;
  céréales ≥ 20 % de la surface (hypothèse).
- **Cultures :** blé tendre, betterave à sucre, luzerne, maïs ensilage.

## Qualité des données
Statuts : `source` (valeur lue dans la source), `derive` (calcul à partir de sources),
`ancien` (sourcé mais daté de 2005-2007, à actualiser), `hypothese` (à valider).

| Culture | Paramètre | Statut | Origine |
|---|---|---|---|
| Blé tendre | prix 2 800 MAD/t | source | ONICL, prix référentiel 2026 (280 DH/q) |
| Blé tendre | rendement 5,2 t/ha, eau 4 536 m³/ha | source | FAO 2017 (présentation ORMVA) |
| Blé tendre | charges | **hypothèse** | à remplacer (fiche technico-économique ORMVAT) |
| Betterave | rendement 58,7 t/ha | dérivé | Cosumar 2024/25 : 2 005 380 t / 34 150 ha |
| Betterave | prime de l'État 80 DH/t | source | FIMASUCRE, décembre 2023 |
| Betterave | prix, charges, eau | **hypothèse** | à remplacer (Cosumar, ORMVAT) |
| Luzerne, maïs | rendements, charges, eau | **ancien** | Sraïri et Kuper (2007), Tadla 2005/06 |
| Luzerne, maïs | prix | dérivé | valeur de remplacement en UFL (2007) |
| Ressources | surface 10 ha, eau 60 000 m³ | **hypothèse** | exploitation type |
| Scénario | dotation de sécheresse 3 000 m³/ha | source | Médias24 |
| Scénario | blé à 270 DH/q | source | prix de référence ONICL 2024/25 |

**Limite majeure :** les cultures fourragères reposent sur des données de 2005-2007 alors que
le blé est à des prix de 2026. Les marges ne sont donc pas comparables tant que ces données
ne sont pas actualisées.

## Utilisation
```bash
pip install -r requirements.txt
python src/modele.py
```
Le script affiche un rapport de qualité des données, écrit `results/scenarios.csv` et trace
`results/assolement.png`.

## Résultats
[À rédiger après actualisation des données : assolement optimal, marge, évolution par scénario.]

## Interprétation économique
[À rédiger : valeur de l'eau (prix dual), culture qui disparaît quand l'eau diminue et pourquoi,
effet de la prime de l'État sur la betterave, limites du prix dual.]

## Limites
- Modèle statique, sans risque ni variabilité des prix ; linéarité des rendements et des charges.
- Exploitation type, non calibrée sur une exploitation réelle.
- Main-d'œuvre non modélisée faute de données sourcées.

## Sources
- ONICL / presse : prix référentiel du blé tendre, campagne 2026 (280 DH/q) ; 270 DH/q en 2024/25.
- Cosumar : bilan de la campagne sucrière 2024/25 ; FIMASUCRE : appui de 80 DH/t.
- Sraïri M.T. et Kuper M., « Valorisation de l'eau en agriculture », PNTTA bulletin n°157, 2007.
- FAO, « Productivity country experience Morocco », 2017.
- Médias24 : dotation moyenne actuelle de 3 000 m³/ha dans les périmètres irrigués.
