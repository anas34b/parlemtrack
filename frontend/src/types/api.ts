// Types miroir des schémas Pydantic de l'API FastAPI (backend/app/schemas/).

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  taille_page: number;
}

export interface Groupe {
  id_an: string;
  nom: string;
  nom_court: string;
  actif: boolean;
  couleur: string | null;
}

export interface GroupeDetail extends Groupe {
  effectif: number;
  cohesion_moyenne: number | null;
}

export interface Depute {
  id_an: string;
  nom: string;
  prenom: string;
  actif: boolean;
  departement: string | null;
  circonscription: string | null;
  groupe: Groupe | null;
}

export interface DeputeDetail extends Depute {
  score_participation: number | null;
  score_loyaute: number | null;
  score_majorite: number | null;
}

export type PositionVote =
  | "pour"
  | "contre"
  | "abstention"
  | "nonVotant"
  | "nonVotantVolontaire";

export interface VoteHistorique {
  scrutin_uid: string;
  scrutin_titre: string;
  scrutin_date: string;
  position: PositionVote;
  par_delegation: boolean;
}

export interface DeputeFiche {
  depute: DeputeDetail;
  historique_votes: Page<VoteHistorique>;
}

export interface Scrutin {
  uid: string;
  numero: number;
  date_scrutin: string;
  titre: string;
  type_vote: string;
  sort: string;
  nb_pour: number;
  nb_contre: number;
  nb_abstention: number;
  nb_non_votants: number;
  lien_an: string | null;
}

export interface VoteParGroupe {
  groupe_id: string;
  groupe_nom: string;
  pour: number;
  contre: number;
  abstention: number;
  non_votant: number;
}

export interface AnalyseIA {
  resume_factuel: string;
  arguments_pour: string[];
  arguments_contre: string[];
  coherence_macro: "aligne" | "mitige" | "contradictoire";
  indicateurs_ref: string[];
  modele_utilise: string;
  genere_le: string;
}

export interface ScrutinDetail extends Scrutin {
  dossier_ref: string | null;
  votes_par_groupe: VoteParGroupe[];
  analyse_ia: AnalyseIA | null;
}

export interface Actualite {
  source: string;
  titre: string;
  lien: string;
  date_publication: string;
}

export interface RechercheResultat {
  deputes: Depute[];
  groupes: Groupe[];
  scrutins: Scrutin[];
}

export interface Health {
  statut: string;
  base_de_donnees: boolean;
  redis: boolean;
  derniere_collecte: string | null;
}
