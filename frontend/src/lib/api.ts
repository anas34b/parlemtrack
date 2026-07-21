// Client HTTP vers l'API FastAPI réelle (jamais de données statiques).
import type {
  Actualite,
  DeputeFiche,
  GroupeDetail,
  Health,
  Page,
  Depute,
  Groupe,
  RechercheResultat,
  Scrutin,
  ScrutinDetail,
} from "@/types/api";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function getJson<T>(chemin: string, revalidateS = 60): Promise<T> {
  const reponse = await fetch(`${API_URL}${chemin}`, { next: { revalidate: revalidateS } });
  if (!reponse.ok) {
    throw new Error(`Échec de l'appel API ${chemin} : HTTP ${reponse.status}`);
  }
  return reponse.json() as Promise<T>;
}

export function getHealth(): Promise<Health> {
  return getJson<Health>("/api/health", 0);
}

export function listerScrutins(params: {
  page?: number;
  tailePage?: number;
  groupe?: string;
  dateMin?: string;
  dateMax?: string;
  type?: string;
  q?: string;
}): Promise<Page<Scrutin>> {
  const recherche = new URLSearchParams();
  if (params.page) recherche.set("page", String(params.page));
  if (params.tailePage) recherche.set("taille_page", String(params.tailePage));
  if (params.groupe) recherche.set("groupe", params.groupe);
  if (params.dateMin) recherche.set("date_min", params.dateMin);
  if (params.dateMax) recherche.set("date_max", params.dateMax);
  if (params.type) recherche.set("type", params.type);
  if (params.q) recherche.set("q", params.q);
  return getJson<Page<Scrutin>>(`/api/scrutins?${recherche.toString()}`);
}

export function obtenirScrutin(uid: string): Promise<ScrutinDetail> {
  return getJson<ScrutinDetail>(`/api/scrutins/${encodeURIComponent(uid)}`);
}

export function listerDeputes(params: {
  page?: number;
  tailePage?: number;
  groupe?: string;
  departement?: string;
  actif?: boolean;
}): Promise<Page<Depute>> {
  const recherche = new URLSearchParams();
  if (params.page) recherche.set("page", String(params.page));
  if (params.tailePage) recherche.set("taille_page", String(params.tailePage));
  if (params.groupe) recherche.set("groupe", params.groupe);
  if (params.departement) recherche.set("departement", params.departement);
  if (params.actif !== undefined) recherche.set("actif", String(params.actif));
  return getJson<Page<Depute>>(`/api/deputes?${recherche.toString()}`);
}

export function obtenirDepute(idAn: string, pageVotes = 1): Promise<DeputeFiche> {
  return getJson<DeputeFiche>(
    `/api/deputes/${encodeURIComponent(idAn)}?page_votes=${pageVotes}`
  );
}

export function listerGroupes(): Promise<Groupe[]> {
  return getJson<Groupe[]>("/api/groupes");
}

export function obtenirGroupe(idAn: string): Promise<GroupeDetail> {
  return getJson<GroupeDetail>(`/api/groupes/${encodeURIComponent(idAn)}`);
}

export function rechercher(q: string): Promise<RechercheResultat> {
  return getJson<RechercheResultat>(`/api/recherche?q=${encodeURIComponent(q)}`);
}

export function listerActualites(): Promise<Actualite[]> {
  return getJson<Actualite[]>("/api/actualites", 300);
}
