"""Génère docs/erd.png depuis le schéma réel des modèles SQLAlchemy.

Usage (nécessite matplotlib, non listé dans requirements.txt car outil de
documentation ponctuel, pas une dépendance d'exécution) :

    pip install matplotlib
    python scripts/generate_erd.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Table -> colonnes affichées (marqueur PK/FK en préfixe)
COLONNES = {
    "groupes": ["PK id_an", "nom", "nom_court", "actif", "couleur"],
    "deputes": ["PK id_an", "nom", "prenom", "actif", "FK groupe_id", "departement",
                "circonscription", "score_participation", "score_loyaute", "score_majorite"],
    "scrutins": ["PK uid", "numero", "date_scrutin", "titre", "type_vote", "sort",
                 "nb_pour", "nb_contre", "nb_abstention", "nb_non_votants", "dossier_ref", "lien_an"],
    "votes": ["PK id", "FK scrutin_uid", "FK depute_id", "position", "par_delegation",
              "UNIQUE(scrutin_uid, depute_id)"],
    "analyses_ia": ["PK/FK scrutin_uid", "resume_factuel", "arguments_pour", "arguments_contre",
                     "coherence_macro", "indicateurs_ref", "modele_utilise", "tokens_utilises", "genere_le"],
    "collectes_log": ["PK id", "date_run", "nb_scrutins_traites", "nb_nouveaux",
                       "nb_analyses_generees", "nb_erreurs", "duree_s", "statut"],
    "sources_meta": ["PK source", "etag", "last_modified", "derniere_collecte"],
}

# Colonne (x) -> liste de tables empilées de haut en bas
COLONNES_LAYOUT = [
    ["groupes", "deputes"],
    ["scrutins", "votes"],
    ["analyses_ia", "collectes_log", "sources_meta"],
]

RELATIONS = [
    ("deputes", "groupes", "groupe_id -> id_an"),
    ("votes", "scrutins", "scrutin_uid -> uid"),
    ("votes", "deputes", "depute_id -> id_an"),
    ("analyses_ia", "scrutins", "scrutin_uid -> uid (1-1)"),
]

LARGEUR = 4.2
LIGNE_H = 0.32
GAP_X = 1.0
GAP_Y = 1.3
MARGE_HAUT = 0.6


def hauteur_table(nom):
    return LIGNE_H * (len(COLONNES[nom]) + 1)


def calculer_positions():
    """Empile chaque colonne de haut en bas, aligné sur le sommet le plus haut."""
    hauteurs_colonnes = [sum(hauteur_table(t) for t in col) + GAP_Y * (len(col) - 1) for col in COLONNES_LAYOUT]
    hauteur_max = max(hauteurs_colonnes)

    positions = {}
    for i, col in enumerate(COLONNES_LAYOUT):
        x = i * (LARGEUR + GAP_X)
        y = hauteur_max - MARGE_HAUT  # sommet de la colonne
        for nom in col:
            h = hauteur_table(nom)
            y -= h
            positions[nom] = (x, y)
            y -= GAP_Y
    return positions, hauteur_max


def dessiner_table(ax, nom, position):
    colonnes = COLONNES[nom]
    x, y = position
    hauteur = hauteur_table(nom)
    ax.add_patch(FancyBboxPatch(
        (x, y), LARGEUR, hauteur,
        boxstyle="round,pad=0.02", linewidth=1.4,
        edgecolor="#18181b", facecolor="#ffffff", zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (x, y + hauteur - LIGNE_H), LARGEUR, LIGNE_H,
        boxstyle="round,pad=0.02", linewidth=1.4,
        edgecolor="#18181b", facecolor="#18181b", zorder=3,
    ))
    ax.text(x + LARGEUR / 2, y + hauteur - LIGNE_H / 2, nom,
            ha="center", va="center", fontsize=11, fontweight="bold", color="white", zorder=4)
    for i, col in enumerate(colonnes):
        cy = y + hauteur - LIGNE_H * (i + 2) + LIGNE_H / 2
        gras = col.startswith("PK") or col.startswith("FK")
        ax.text(x + 0.15, cy, col, ha="left", va="center", fontsize=8.5,
                fontweight="bold" if gras else "normal",
                color="#18181b" if gras else "#3f3f46", zorder=4)


def main():
    positions, hauteur_max = calculer_positions()

    largeur_totale = len(COLONNES_LAYOUT) * (LARGEUR + GAP_X)
    fig, ax = plt.subplots(figsize=(largeur_totale * 1.05, (hauteur_max + 1.2) * 1.05))

    for nom, position in positions.items():
        dessiner_table(ax, nom, position)

    for source, cible, label in RELATIONS:
        px, py = positions[source]
        cx, cy = positions[cible]
        hs, hc = hauteur_table(source), hauteur_table(cible)
        depart = (px + LARGEUR / 2, py + hs / 2)
        arrivee = (cx + LARGEUR / 2, cy + hc / 2)
        ax.annotate(
            "", xy=arrivee, xytext=depart,
            arrowprops=dict(arrowstyle="-|>", color="#2563eb", lw=1.6,
                             connectionstyle="arc3,rad=0.15",
                             shrinkA=15, shrinkB=15),
            zorder=1,
        )
        mx, my = (depart[0] + arrivee[0]) / 2, (depart[1] + arrivee[1]) / 2
        ax.text(mx, my, label, fontsize=7.5, color="#2563eb", ha="center", va="center",
                backgroundcolor="white", zorder=5)

    ax.set_xlim(-0.3, largeur_totale)
    ax.set_ylim(-0.3, hauteur_max + 1.0)
    ax.axis("off")
    ax.set_title("ParlemTrack — schéma relationnel (PostgreSQL)", fontsize=13, fontweight="bold", pad=16)
    fig.tight_layout()
    fig.savefig("docs/erd.png", dpi=150)
    print("docs/erd.png généré")


if __name__ == "__main__":
    main()
