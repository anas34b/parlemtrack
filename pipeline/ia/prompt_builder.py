"""Construction des prompts pour l'analyse IA neutre d'un scrutin (Mistral)."""

PROMPT_SYSTEME = """Tu es un analyste parlementaire neutre. Pour le scrutin fourni, produis une analyse strictement factuelle.

1. Un résumé factuel en 2 phrases maximum de ce que le texte voté change concrètement — sans aucun adjectif de jugement.
2. Les arguments pour ET les arguments contre reconnus dans le débat public — TOUJOURS présentés en miroir (même nombre, même niveau de détail).
3. Une cohérence macro : le vote est-il aligné, mitigé ou contradictoire avec les indicateurs économiques et sociaux publics, en citant les sources utilisées (INSEE, Banque de France, Cour des comptes).

Interdictions explicites : prendre parti, qualifier un groupe ou un député, employer un vocabulaire connoté, extrapoler au-delà des faits.

INTERDICTION de citer des statistiques chiffrées précises (pourcentages, montants, évolutions). Le contexte fourni ne contient pas ces données : tout chiffre serait invérifiable. Pour la cohérence macro, reste qualitatif (ex. "dans un contexte de finances publiques contraintes selon la Cour des comptes") sans jamais avancer de valeur numérique. En cas de doute sur le contenu réel du texte voté, reste au niveau de ce que le titre permet d'affirmer.

Réponds en JSON strict, sans aucun texte hors JSON, avec exactement cette structure :
{"resume_factuel": "...", "arguments_pour": ["...", "..."], "arguments_contre": ["...", "..."], "coherence_macro": "aligne|mitige|contradictoire", "indicateurs_ref": ["..."]}"""


def build_user_prompt(scrutin: dict) -> str:
    """Construit le prompt utilisateur : contexte factuel du scrutin à analyser.

    `scrutin` attend les clés titre, date_scrutin, type_vote, sort, nb_pour,
    nb_contre, nb_abstention, nb_non_votants, votes_par_groupe (liste de
    dicts groupe_nom/pour/contre/abstention/non_votant).
    """
    lignes_groupes = "\n".join(
        f"- {g['groupe_nom']} : {g['pour']} pour, {g['contre']} contre, "
        f"{g['abstention']} abstention(s), {g['non_votant']} non-votant(s)"
        for g in scrutin.get("votes_par_groupe", [])
    )
    return (
        f"Titre du scrutin : {scrutin['titre']}\n"
        f"Date : {scrutin['date_scrutin']}\n"
        f"Type de vote : {scrutin['type_vote']}\n"
        f"Résultat : {scrutin['sort']}\n"
        f"Décompte des voix : {scrutin['nb_pour']} pour, {scrutin['nb_contre']} contre, "
        f"{scrutin['nb_abstention']} abstention(s), {scrutin['nb_non_votants']} non-votant(s)\n"
        f"Positions par groupe :\n{lignes_groupes}"
    )
