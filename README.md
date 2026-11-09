# optimalSwitchPoint

Projet d'optimisation qui détermine combien de robots A produire avant
de passer à la production de robots B, moins coûteux. L'objectif est de tenir
compte du stock de pièces spécifiques à A, qui ne pourra plus être utilisé
après l'arrêt de cette production, ainsi que des achats de pièces par lots.

Le problème est formulé comme un programme linéaire en nombres entiers mixtes
(MILP), avec Pyomo et le solveur HiGHS.

## Modèle

Pour chaque pièce spécifique \(i\), les données comprennent :

- \(q_i\) : quantité nécessaire à la production d'un robot A ;
- \(p_i\) : coût unitaire de la pièce ;
- \(s_i\) : stock initial ;
- \(L_i\) : quantité de pièces dans un lot commandé.

Les variables de décision sont :

- \(x\) : nombre entier non négatif de robots A produits ;
- \(y_i\) : nombre entier non négatif de lots commandés pour la pièce \(i\).

La quantité restante de chaque pièce est :

$$
r_i = s_i + L_i y_i - q_i x
$$

La contrainte de disponibilité impose \(r_i \geq 0\). Le modèle minimise le
coût relatif de production de A par rapport à B, auquel s'ajoutent le coût des
pièces restantes et celui des lots commandés :

$$
\min\ (c_A-c_B)x + \sum_i p_i r_i + \sum_i p_i L_i y_i
$$

où \(c_A\) et \(c_B\) sont les coûts de production unitaires des robots A et B.

## Installation

Depuis la racine du projet, créez un environnement virtuel et installez les
dépendances :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Il faut également disposer d'une installation de Python compatible avec les
versions des dépendances indiquées dans `requirements.txt`.

## Exécution

Depuis la racine du projet, lancez le module :

```powershell
python -m src.model
```

Le comportement est configuré directement en haut de
[`src/model/__main__.py`](src/model/__main__.py), sans arguments de ligne de
commande.

### Options principales

| Variable | Valeur par défaut | Rôle |
| --- | --- | --- |
| `CREATE_NEW_INSTANCE` | `False` | Génère une nouvelle instance aléatoire. |
| `READ_INSTANCE_FROM_FILE` | `True` | Charge `src/inputs/instance.json`. |
| `SAVE_INSTANCE` | `False` | Enregistre l'instance dans `src/inputs/instance.json`. |
| `DISPLAY_INSTANCE` | `True` | Affiche l'instance et le coût des pièces spécifiques par robot A. |
| `SOLVE_MILP` | `True` | Construit et résout le MILP. |
| `VERIFY_MILP_WITH_EVALUATION` | `True` | Compare la solution du MILP au calcul direct pour le nombre optimal de robots A. |
| `SAVE_SOLUTION` | `True` | Enregistre la solution dans `src/outputs/solution.json`. |
| `GENERATE_GRAPHICS` | `True` | Génère et affiche le graphique des coûts. |

Activez exactement une source d'instance : `CREATE_NEW_INSTANCE` ou
`READ_INSTANCE_FROM_FILE`. `SAVE_SOLUTION` nécessite que `SOLVE_MILP` soit
activé.

Les paramètres numériques de génération et de graphique se trouvent au même
endroit :

- `SPECIFIC_PART_COUNT` et `RANDOM_SEED` contrôlent la génération d'instance ;
- `MAX_ROBOT_A_COUNT` et `ROBOT_A_COUNT_STEP` définissent la plage évaluée
  pour le graphique.

Si une solution MILP est disponible, le graphique inclut son optimum et adapte
la plage pour l'inclure.

## Fichiers générés

- `src/inputs/instance.json` : données de l'instance ;
- `src/outputs/solution.json` : nombre optimal de robots A, lots à commander,
  quantités restantes et coûts (valeurs monétaires arrondies à deux décimales) ;
- `src/graphics/graphic.png` : courbes des différentes composantes du coût et
  marqueur de l'optimum.

Les dossiers nécessaires sont créés automatiquement au moment de
l'enregistrement.

## Organisation du code

- `src/model/__main__.py` : configuration et orchestration de l'exécution ;
- `src/model/create_instance.py` : création, lecture et sauvegarde des instances ;
- `src/model/optimize.py` : construction et résolution du modèle Pyomo ;
- `src/model/evaluate.py` : calcul direct du coût pour un nombre donné de robots A ;
- `src/model/solution.py` : vérification et sauvegarde de la solution ;
- `src/model/plot_solution.py` : génération du graphique.
