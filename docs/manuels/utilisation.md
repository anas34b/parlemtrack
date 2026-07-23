# Manuel d'utilisation — ParlemTrack

Ce manuel décrit le parcours d'un citoyen sur ParlemTrack, écran par
écran, tel qu'il existe réellement dans l'application.

## Accueil (`/`)

La page d'accueil affiche le fil des derniers scrutins de l'Assemblée
nationale, du plus récent au plus ancien, paginé (20 par page). Un
bandeau d'actualités en tête de page présente les derniers titres des
flux RSS presse suivis (collectés par le pipeline).

Chaque scrutin est présenté sous forme de carte :
- la date et le numéro du scrutin,
- le titre du texte voté,
- un badge **Adopté** (vert) ou **Rejeté** (rouge),
- une barre de répartition des voix (pour / contre / abstention).

Cliquer sur une carte ouvre le détail du scrutin.

## Détail d'un scrutin (`/scrutins/<uid>`)

En haut : numéro, date, titre complet, badge Adopté/Rejeté, et un lien
« Voir le scrutin sur le site de l'Assemblée nationale » (source
officielle, permet de vérifier chaque donnée affichée).

Le décompte global (pour / contre / abstention) est affiché en gros,
suivi du **vote par groupe** : une barre segmentée par groupe politique
(pour / contre / abstention / non-votant), avec la pastille de couleur
du groupe et son nom toujours affiché en texte à côté (la couleur seule
ne porte jamais l'information, pour rester accessible).

Si une **analyse IA** a été générée pour ce scrutin, un bloc « Analyse »
apparaît :
- un **résumé factuel** neutre du scrutin,
- un badge **Cohérence macro** : *Aligné*, *Mitigé* ou *Contradictoire*.
  Il indique si le vote d'un groupe est cohérent avec ses positions
  affichées par ailleurs sur des sujets proches — un signal de lecture,
  pas un jugement de valeur ;
- deux colonnes **« Arguments pour »** / **« Arguments contre »**,
  volontairement symétriques (même structure, même style), qui
  résument les arguments avancés de chaque côté sans prendre parti ;
- les sources ayant servi de repère à l'analyse, en petit texte en bas
  du bloc.

Si aucune analyse n'est encore disponible pour ce scrutin, un message
neutre l'indique — ParlemTrack ne génère les analyses qu'une seule fois
par scrutin, progressivement.

Une note de bas de page rappelle qu'environ 40 % des votes à
l'Assemblée nationale ont lieu **à main levée** et ne sont pas
comptabilisés nominativement (voir la rubrique « Comprendre » pour le
détail) : ParlemTrack ne peut recenser que les **scrutins publics**, où
chaque position individuelle est enregistrée.

## Fiche d'un député (`/deputes/<id>`)

Identité du député (nom, prénom, avatar avec ses initiales dans la
couleur de son groupe), groupe politique (lien vers la fiche du
groupe), circonscription.

Si ce député a quitté son mandat en cours de législature (décès, entrée
au gouvernement, invalidation d'élection...), un badge **« Mandat
terminé »** apparaît à côté de son nom. Ces députés restent consultables
individuellement — leurs votes passés font partie de l'historique — mais
sont exclus par défaut des listes et annuaires.

Deux jauges : **Participation** (part des scrutins où le député a
effectivement voté) et **Loyauté au groupe** (part des votes alignés
avec la position majoritaire de son groupe). Une jauge affiche « N/A »
si la donnée n'est pas disponible plutôt qu'une fausse valeur.

En dessous, l'**historique des votes** du député, paginé, chaque ligne
donnant le titre du scrutin, sa date, et la position de vote — toujours
affichée avec une **icône et un texte** (jamais la couleur seule), pour
rester lisible en cas de daltonisme ou de niveaux de gris.

## Listes Députés et Groupes (`/deputes`, `/groupes`)

`/deputes` liste les 577 députés en exercice (mandat terminé exclu par
défaut), paginée, avec le nom, le groupe et la circonscription de
chacun.

`/groupes` liste les groupes politiques actifs de la législature, puis,
séparément, les groupes dissous en cours de législature. Cliquer sur un
groupe ouvre sa fiche : effectif en exercice, cohésion moyenne de vote
du groupe, et composition (liste des députés du groupe, mandat terminé
exclu par défaut).

## Recherche (`/recherche`)

La barre de recherche, accessible depuis l'en-tête sur toutes les
pages, interroge en une seule fois les scrutins, les députés et les
groupes. Les résultats sont regroupés par catégorie. La recherche est
insensible à la casse et fonctionne sur une simple sous-chaîne du titre
(un scrutin sur "sécurité sociale" ne remonte pas forcément avec le mot
"budget", même si le sujet s'y rapporte — voir le titre officiel exact
du scrutin sur le site de l'AN).

## Rubrique « Comprendre » (`/comprendre`)

Quatre articles pédagogiques, écrits en langage simple, pour donner le
contexte nécessaire à la lecture des données :
- **Qu'est-ce qu'un scrutin ?** — différence entre scrutin public
  ordinaire et solennel, et pourquoi ParlemTrack ne recense que les
  scrutins publics.
- **Qu'est-ce qu'une législature ?** — durée du mandat, numérotation,
  et pourquoi des députés « mandat terminé » restent visibles.
- **Le parcours d'une loi** — les étapes qu'un texte traverse avant
  d'être adopté.
- **Pourquoi ~40 % des votes ne sont pas enregistrés** — le
  fonctionnement du vote à main levée, et ses conséquences sur ce que
  ParlemTrack peut effectivement montrer.

## Installation en application (PWA)

ParlemTrack est une PWA installable : dans un navigateur compatible
(Chrome, Edge, Safari mobile...), une proposition d'installation
apparaît dans la barre d'adresse ou le menu du navigateur. Une fois
installée, l'application s'ouvre en plein écran, sans barre d'adresse,
comme une application native, et reste utilisable hors connexion pour
les pages déjà visitées (grâce au service worker).

## Accessibilité

Le site est navigable entièrement au clavier (focus toujours visible),
utilise des éléments sémantiques (`<nav>`, `<main>`, boutons réels), et
n'utilise jamais la couleur seule pour porter une information — les
badges, positions de vote et pastilles de groupe sont toujours doublés
d'un texte. Un lien d'évitement en tout début de page permet d'aller
directement au contenu principal sans repasser par la navigation.
