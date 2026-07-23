# Cahier de recettes — ParlemTrack

Environnement de test : **http://91.134.88.221:3000** (frontend de production).

Les colonnes **Résultat obtenu** et **Verdict** (✅ OK / ❌ KO) sont à
remplir en exécutant chaque scénario sur l'environnement ci-dessus.

## Méthodologie

- Les cas **fonctionnels** (F0x) se testent intégralement depuis un
  navigateur, sur l'URL publique.
- Les cas **structurels** (S0x) et **sécurité** (SEC0x) qui portent sur
  l'API directement ne sont **pas** accessibles depuis l'extérieur : le
  backend n'expose aucun port sur l'hôte (voir `docker-compose.prod.yml`
  et `docs/manuels/deploiement.md`, choix de sécurité volontaire). Pour
  ces cas, se connecter en SSH au VPS puis exécuter depuis
  `~/parlemtrack` :
  ```bash
  # Appel direct à l'API depuis le réseau Docker interne
  docker compose -f docker-compose.prod.yml exec -T backend python3 -c \
    "import httpx; r = httpx.get('http://localhost:8000/<route>'); print(r.status_code, r.headers, r.text)"
  ```
  Ces cas sont marqués **[SSH]** dans la colonne Étapes ; les autres sont
  marqués **[Navigateur]**.

## Cas fonctionnels

| ID | Scénario | Étapes | Résultat attendu | Résultat obtenu | Verdict |
|---|---|---|---|---|---|
| F01 | Accueil conforme aux données AN | [Navigateur] Ouvrir `/`. | La page liste des scrutins réels (titre, date, n° de scrutin, décompte pour/contre/abstention, badge Adopté/Rejeté) cohérents avec le site de l'AN (vérifier un scrutin via son lien "Voir sur le site de l'Assemblée nationale"). | Scrutins réels affichés, cohérents avec le lien vers l'AN | ✅ OK |
| F02 | Détail scrutin — vote par groupe segmenté | [Navigateur] Ouvrir un scrutin depuis l'accueil. | Une barre segmentée par groupe politique (pour/contre/abstention/non-votant), avec pastille de couleur par groupe et nom du groupe toujours affiché en texte. | Texte, lien vers le scrutin AN, barre segmentée par groupe et pastilles conformes | ✅ OK |
| F03 | Détail scrutin — analyse IA présente | [Navigateur] Ouvrir un scrutin dont l'analyse IA a été générée. | Un résumé factuel, un badge "Cohérence macro : Aligné/Mitigé/Contradictoire", et les sources indiquées en bas de bloc. | Analyse visible, badge "Mitigé", sources affichées en bas | ✅ OK |
| F04 | Arguments pour/contre symétriques | [Navigateur] Sur un scrutin avec analyse IA, comparer les deux colonnes. | Colonnes "Arguments pour" et "Arguments contre" de structure, largeur et style strictement identiques (seule la couleur diffère). | Structure et style strictement symétriques, vérifié sur plusieurs scrutins | ✅ OK |
| F05 | Scrutin sans analyse IA | [Navigateur] Ouvrir un scrutin récent sans analyse encore générée. | Message "Analyse IA non encore disponible pour ce scrutin." affiché, aucune erreur ni page cassée. | Scrutin VTANR5L17V3070 (identifié en base, sans analyse) : message "Analyse IA non encore disponible" propre, aucune erreur | ✅ OK |
| F06 | Recherche — résultat existant | [Navigateur] Sur `/recherche`, chercher un terme présent en base (ex. "agricole" ou le nom d'un député). | Résultats groupés par section (Députés / Groupes / Scrutins), chacun cliquable vers sa fiche. | Recherche par terme présent : résultats groupés par section, cliquables | ✅ OK |
| F07 | Recherche — terme absent | [Navigateur] Chercher un terme absent (ex. "xyzabc123"). | Message "Aucun résultat pour « xyzabc123 »." sans erreur. | Recherche "xyzabc123" : message "Aucun résultat", pas d'erreur | ✅ OK |
| F08 | Recherche insensible casse/accents | [Navigateur] Chercher un même terme en majuscules, minuscules, avec/sans accents (ex. "SECURITE SOCIALE" puis "sécurité sociale"). | Mêmes résultats renvoyés dans les deux cas. | Insensible à la casse mais pas aux accents : "SÉCURITÉ SOCIALE" (maj+accents) fonctionne, "SECURITE SOCIALE" (maj sans accents) ne remonte rien | ❌ KO |
| F09 | Fiche député complète | [Navigateur] Ouvrir la fiche d'un député depuis une liste ou une recherche. | Identité, groupe (avec lien), jauges de participation/loyauté (ou "N/A" si absentes), historique de votes paginé. | Identité, groupe, jauges participation/loyauté, historique de votes paginé, tous présents | ✅ OK |
| F10 | Position de vote icône + texte | [Navigateur] Sur une fiche député, observer l'historique de votes. | Chaque position de vote (pour/contre/abstention/non-votant) affichée avec une icône ET un libellé texte, jamais la couleur seule. | Icône + texte sur chaque position de vote | ✅ OK |
| F11 | Liste Députés exclut mandat terminé par défaut | [Navigateur] Ouvrir `/deputes`. | Seuls les députés en exercice (`actif: true`) apparaissent dans la liste par défaut. | Liste /deputes exclut les mandats terminés par défaut | ✅ OK |
| F12 | Badge "Mandat terminé" | [Navigateur] Ouvrir la fiche d'un député ayant quitté son mandat en cours de législature (via la recherche si besoin, ces députés étant exclus des listes par défaut). | Badge "Mandat terminé" visible à côté de son nom. | Testé sur André Chassaigne (PA267306) : badge "Mandat terminé" visible, jauges à "N/A", historique conservé | ✅ OK |
| F13 | Filtre scrutins par groupe | [Navigateur] Sur `/scrutins`, filtrer par un groupe (paramètre d'URL `?groupe=<id>` en l'absence de sélecteur visuel). | Seuls les scrutins où ce groupe a voté apparaissent. | Le code (`scrutins/page.tsx`) ne lit ni ne transmet le paramètre `groupe` à l'API — le test manuel initial était non concluant (quasi tous les groupes votent sur quasi tous les scrutins, donc l'observation ne distinguait pas filtre actif de filtre absent). | ❌ KO |
| F14 | Filtre scrutins par période | [Navigateur] Ajouter `date_min`/`date_max` à l'URL de `/scrutins`. | Seuls les scrutins dans la période demandée apparaissent. | Le filtre de date (date_min/date_max) est perdu lors du passage à la page suivante de la pagination | ❌ KO |
| F15 | Menu burger accessible au clavier (mobile) | [Navigateur, largeur < 721px ou outils dev] Naviguer au clavier jusqu'au bouton burger, ouvrir avec Entrée, fermer avec Échap. | Le menu s'ouvre/se ferme au clavier, `aria-expanded` change, le focus revient sur le bouton après fermeture par Échap. | Retest avec protocole précis (focus confirmé visuellement) : Tab+Entrée ouvre bien le burger, cohérent avec le test Playwright en CI. | ✅ OK |
| F16 | Installation PWA | [Navigateur, Chrome/Edge desktop ou mobile] Observer la barre d'adresse ou le menu du navigateur. | Une proposition d'installation de l'application apparaît (icône, nom "ParlemTrack") ; l'app installée s'ouvre en mode standalone. | Installation PWA confirmée sur Android/Chrome (pas de bannière sur iOS/Safari, comportement natif attendu de la plateforme, non un défaut de l'app) | ✅ OK |
| F17 | Rubrique "Comprendre" complète | [Navigateur] Parcourir `/comprendre` et ses 4 sous-pages (scrutin, législature, parcours-loi, votes-main-levée). | Chaque page explique clairement son sujet, sans lien mort ni contenu manquant. | Les 4 pages de /comprendre sont complètes, aucun lien mort | ✅ OK |
| F18 | Vue Groupe — composition | [Navigateur] Ouvrir la fiche d'un groupe politique. | Effectif en exercice, cohésion moyenne de vote (ou "N/A"), liste des députés du groupe (mandat terminé exclu par défaut). | Fiche groupe : effectif, cohésion, liste des députés, tous présents | ✅ OK |

## Cas structurels

| ID | Scénario | Étapes | Résultat attendu | Résultat obtenu | Verdict |
|---|---|---|---|---|---|
| S01 | Pipeline rejouable sans doublon | [SSH] Relancer `docker compose exec backend python -m pipeline.run` deux fois de suite, comparer le nombre de lignes de `scrutins` et `votes` avant/après le 2e run. | Aucun doublon créé (upsert idempotent) ; seuls les scrutins réellement nouveaux ou modifiés changent. | Pipeline rejoué en réel : 8434 scrutins / 1 270 476 votes avant et après (identique), run "0 nouveaux, 0 erreurs, 164.1s" | ✅ OK |
| S02 | Cache Redis invalidé après collecte | [SSH] Consulter une route API (ex. `/api/scrutins`) avant un run, relancer le pipeline, reconsulter la même route. | Les données reflètent le nouveau run sans attendre l'expiration du TTL du cache (`invalider_prefixe` déclenché en fin de run). | Log "cache API invalidé" confirmé en fin de run | ✅ OK |
| S03 | Healthcheck applicatif | [SSH] `GET /api/health`. | Réponse `200` avec `statut: "ok"`, `base_de_donnees: true`, `redis: true`, `derniere_collecte` renseignée. | GET /api/health : 200, statut ok, base_de_donnees true, redis true, derniere_collecte renseignée | ✅ OK |
| S04 | Migration Alembic à vide | [SSH] Sur un schéma déjà à jour, relancer `alembic upgrade head` dans le conteneur backend. | Sortie sans erreur, aucune modification de schéma (déjà "up to date"), code de sortie `0`. | alembic upgrade head : sortie sans erreur, déjà à jour, aucune migration appliquée | ✅ OK |
| S05 | Bascule actif/inactif d'un député | [SSH] Comparer la base avant/après un run où un député présent précédemment n'apparaît plus dans le fichier AN source. | Le député concerné passe `actif: false` (jamais supprimé), disparaît des listes filtrées par défaut, reste consultable via sa fiche. | Bascule testée en conditions réelles sur PA267306 (réinitialisation ciblée de sources_meta puis relance de _collecter_deputes_et_groupes) : passage de actif=True à actif=False confirmé, avec log "député remplacé, passage à actif=False : André Chassaigne (PA267306)" | ✅ OK |
| S06 | Détection ETag/Last-Modified | [SSH] Relancer le pipeline deux fois de suite sans changement côté AN, observer les logs. | Le 2e run logue "source ... inchangée depuis la dernière collecte, téléchargement sauté" pour chaque source inchangée. | La détection "source inchangée" fonctionne pour deputes et deputes_historique, mais l'archive scrutins et les scores Datan sont retéléchargés/recalculés à chaque run sans cette détection, malgré 0 scrutin nouveau constaté | 🟡 PARTIEL |

## Cas sécurité

| ID | Scénario | Étapes | Résultat attendu | Résultat obtenu | Verdict |
|---|---|---|---|---|---|
| SEC01 | Recherche — tentative d'injection | [Navigateur ou SSH] Chercher `' OR '1'='1` ou `%'; DROP TABLE scrutins;--` via `/recherche?q=...` ou `/api/recherche?q=...`. | Traité comme texte littéral (requête paramétrée SQLAlchemy) : aucun résultat pertinent, aucune erreur serveur, aucune donnée supprimée/modifiée. | Injection ' OR '1'='1' traitée comme texte littéral, aucun résultat, aucune erreur serveur | ✅ OK |
| SEC02 | Rate limiting à la limite | [SSH] Envoyer plus de `60` requêtes/minute (valeur de `RATE_LIMIT`) sur une même route depuis la même IP. | Les requêtes au-delà de la limite reçoivent `429 Too Many Requests`. | Rate limit : bascule de 200 à 429 exactement à la 61e requête/minute (limite configurée à 60) | ✅ OK |
| SEC03 | Headers de sécurité présents | [SSH] `GET /api/health`, inspecter les en-têtes de réponse. | Présence de `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: geolocation=(), microphone=(), camera=()`. | En-têtes présents sur /api/health : X-Content-Type-Options, X-Frame-Options: DENY, Referrer-Policy, Permissions-Policy | ✅ OK |
| SEC04 | Clé API Mistral absente du frontend | [Navigateur] Ouvrir les outils dev, onglet Réseau/Sources, chercher `MISTRAL` dans le HTML/JS servi au navigateur. | Aucune occurrence de la clé Mistral (ni d'aucun secret) dans le code servi au client — l'appel Mistral n'a lieu que côté pipeline/serveur. | Aucune occurrence de "MISTRAL" dans les sources ni le réseau côté client | ✅ OK |
| SEC05 | CORS refuse une origine inconnue | [SSH] Requête vers l'API avec un en-tête `Origin: https://site-inconnu.example` non listé dans `CORS_ORIGINS`. | Pas d'en-tête `Access-Control-Allow-Origin` correspondant dans la réponse — le navigateur bloquerait la lecture de la réponse depuis cette origine. | Origin inconnue : 200 renvoyé mais Access-Control-Allow-Origin absent de la réponse | ✅ OK |
| SEC06 | `.env` absent du dépôt | [Local, avant tout déploiement] `git ls-files` sur le dépôt cloné, chercher une ligne exactement égale à `.env`. | Aucune correspondance : `.env` n'a jamais été commité. `.env.example` est présent, avec uniquement des valeurs factices (aucun vrai mot de passe/clé). | git ls-files ne retourne aucune ligne ".env" | ✅ OK |

## Synthèse

Exécution réelle le **23 juillet 2026**, sur **http://91.134.88.221:3000**
(+ SSH sur le VPS pour les cas `[SSH]`) :

| Verdict | Nombre |
|---|---|
| ✅ OK | 26 |
| ❌ KO | 3 |
| 🟡 Partiel | 1 |
| **Total** | **30 (~87 % de réussite)** |

**Aucune anomalie bloquante.** Les 3 échecs confirmés (F08, F13, F14)
ont donné lieu à deux fiches de bug dédiées (BUG-015 pour F08,
BUG-016 pour F13 et F14 — même cause racine, la page liste des
scrutins ne transmet aucun filtre à l'API), de même qu'une observation
faite librement pendant la recette, hors grille de cas (barre de vote
par groupe écrasée en mobile, BUG-018) — voir `docs/bugs/`. F15 (menu
burger au clavier), initialement noté KO,
s'est révélé être un faux positif du premier test manuel (focus pas
encore posé sur le bouton) : un retest avec protocole précis confirme
que ça fonctionne, cohérent avec le test automatisé Playwright — pas
de fiche de bug pour ce cas. Le cas partiel S06 (détection
ETag/Last-Modified incomplète pour les scrutins et les scores Datan)
n'a pas encore de fiche dédiée. Aucun de ces points ne remet en cause
le fonctionnement
global de l'application.
