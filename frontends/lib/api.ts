const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

let refreshPromise: Promise<string | null> | null = null;

/**
 * Décode un JWT sans vérifier la signature (uniquement pour lire l'expiration).
 * Retourne `null` si le token est mal formé.
 */
function decodeTokenPayload(token: string): Record<string, unknown> | null {
  try {
    const base64 = token.split(".")[1];
    if (!base64) return null;
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

/** Vérifie si un token JWT est expiré (basé sur la date dans le payload). */
function isTokenExpired(token: string): boolean {
  const payload = decodeTokenPayload(token);
  if (!payload || typeof payload.exp !== "number") return true;
  return Date.now() >= payload.exp * 1000;
}

function getTokens() {
  if (typeof window === "undefined") return null;
  const access = localStorage.getItem("access_token");
  const refresh = localStorage.getItem("refresh_token");
  if (!access) return null;
  return { access, refresh };
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function refreshAccessToken(refresh: string): Promise<string | null> {
  // Éviter les appels concurrents au refresh
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_URL}/auth/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });

      if (!res.ok) {
        // 401 sur refresh = refresh token invalide ou blacklisté
        clearTokens();
        return null;
      }

      const data = await res.json();
      setTokens(data.access, refresh);
      return data.access;
    } catch {
      // Erreur réseau — ne pas clear les tokens, on réessaiera
      return null;
    }
  })();

  const result = await refreshPromise;
  refreshPromise = null;
  return result;
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const tokens = getTokens();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  // Si le token access est déjà expiré, tenter un refresh avant l'appel
  if (tokens?.access && tokens.refresh && isTokenExpired(tokens.access)) {
    const newAccess = await refreshAccessToken(tokens.refresh);
    if (newAccess) {
      tokens.access = newAccess;
      headers["Authorization"] = `Bearer ${newAccess}`;
    } else {
      clearTokens();
      throw new AuthError("Session expirée", true);
    }
  } else if (tokens) {
    headers["Authorization"] = `Bearer ${tokens.access}`;
  }

  let res = await fetch(`${API_URL}${endpoint}`, { ...options, headers }).catch(() => {
    throw new Error("Erreur réseau — vérifiez votre connexion");
  });

  // Tentative de refresh automatique en cas de 401
  if (res.status === 401 && tokens?.refresh && !refreshPromise) {
    const newAccess = await refreshAccessToken(tokens.refresh);
    if (newAccess) {
      headers["Authorization"] = `Bearer ${newAccess}`;
      res = await fetch(`${API_URL}${endpoint}`, { ...options, headers }).catch(() => {
        throw new Error("Erreur réseau — vérifiez votre connexion");
      });
    } else {
      clearTokens();
      throw new AuthError("Session expirée — veuillez vous reconnecter", true);
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      clearTokens();
      throw new AuthError("Non authentifié", true);
    }
    if (res.status === 403) {
      throw new AuthError("Accès refusé", false);
    }
    if (res.status === 429) {
      throw new Error("Trop de requêtes — veuillez réessayer plus tard");
    }
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.email?.[0] || err.phone?.[0] || "Erreur serveur");
  }

  return res.json();
}

export class AuthError extends Error {
  redirect: boolean;
  constructor(message: string, redirect: boolean) {
    super(message);
    this.redirect = redirect;
  }
}

export async function register(data: {
  email: string;
  phone: string;
  password: string;
  password2: string;
  role: string;
  ville?: string;
  quartier?: string;
}) {
  const body = {
    ...data,
    phone: data.phone.startsWith("+225") ? data.phone : `+225${data.phone}`,
  };
  const res = await fetch(`${API_URL}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const message = (
      Object.values(err).flat() as string[]
    ).find(Boolean) || "Erreur lors de l'inscription";
    throw new Error(message);
  }
  const json = await res.json();
  setTokens(json.access, json.refresh);
  return json.user;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Email ou mot de passe incorrect");
  }
  const json = await res.json();
  setTokens(json.access, json.refresh);
  return json.user;
}

export async function getMe() {
  return apiFetch<{
    id: number;
    email: string;
    phone: string;
    role: string;
    ville: string;
    quartier: string;
  }>("/auth/me/");
}

export interface ProfilEncadreurPublic {
  id: number;
  user_id: number;
  nom: string;
  bio: string;
  ville: string;
  quartier: string;
  matieres: { id: number; nom: string }[];
  tarif_mois: number | null;
  tarif_horaire: number | null;
  type_tarif: string;
  disponible: boolean;
  verified: boolean;
  note_moyenne: number;
  nombre_avis: number;
  date_inscription: string;
  debloque: boolean;
  autre_matiere: string;
}

export interface ProfilEncadreur extends ProfilEncadreurPublic {
  email?: string;
  phone?: string;

  // Questionnaire post-inscription
  accepte_deplacement?: boolean;
  niveau_etudes?: string;
  niveaux_enseignement?: string[];
  experience_cours?: string;
  jours_disponibles?: string[];
  creneaux_preferes?: string[];
  cgu_acceptees?: boolean;
  questionnaire_rempli?: boolean;
}

export interface Matiere {
  id: number;
  nom: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export async function getEncadreurs(params?: {
  ville?: string; quartier?: string; matiere?: string;
  matiere_nom?: string;
  page?: number; search?: string; note_min?: number;
  niveau_etudes?: string; niveaux_enseignement?: string[];
  jours_disponibles?: string[]; tarif_max_mois?: number;
  tarif_max_horaire?: number; ordering?: string;
}): Promise<PaginatedResponse<ProfilEncadreurPublic>> {
  const qs = new URLSearchParams();
  if (params?.ville) qs.set("ville", params.ville);
  if (params?.quartier) qs.set("quartier", params.quartier);
  if (params?.matiere) qs.set("matiere", params.matiere);
  if (params?.matiere_nom) qs.set("matiere_nom", params.matiere_nom);
  if (params?.page) qs.set("page", String(params.page));
  if (params?.search) qs.set("search", params.search);
  if (params?.note_min) qs.set("note_min", String(params.note_min));
  if (params?.niveau_etudes) qs.set("niveau_etudes", params.niveau_etudes);
  if (params?.ordering) qs.set("ordering", params.ordering);
  params?.niveaux_enseignement?.forEach((n) => qs.append("niveaux_enseignement", n));
  params?.jours_disponibles?.forEach((j) => qs.append("jours_disponibles", j));
  if (params?.tarif_max_mois) qs.set("tarif_max_mois", String(params.tarif_max_mois));
  if (params?.tarif_max_horaire) qs.set("tarif_max_horaire", String(params.tarif_max_horaire));
  const qstr = qs.toString();
  return apiFetch<PaginatedResponse<ProfilEncadreur>>(`/encadreurs/${qstr ? `?${qstr}` : ""}`);
}

export async function getEncadreur(id: number): Promise<ProfilEncadreur> {
  return apiFetch<ProfilEncadreur>(`/encadreurs/${id}/`);
}

export async function getMonProfil(): Promise<ProfilEncadreur> {
  return apiFetch<ProfilEncadreur>("/mon-profil/");
}

export interface ProfilEncadreurUpdate {
  bio?: string;
  tarif_mois?: number | null;
  tarif_horaire?: number | null;
  type_tarif?: string;
  disponible?: boolean;
  matiere_ids?: number[];
  autre_matiere?: string;
  accepte_deplacement?: boolean;
  niveau_etudes?: string;
  niveaux_enseignement?: string[];
  experience_cours?: string;
  jours_disponibles?: string[];
  creneaux_preferes?: string[];
  cgu_acceptees?: boolean;
}

export async function updateMonProfil(data: ProfilEncadreurUpdate): Promise<ProfilEncadreur> {
  return apiFetch<ProfilEncadreur>("/mon-profil/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export interface VilleData {
  ville: string;
  quartiers: string[];
}

export async function getVilles(): Promise<VilleData[]> {
  return apiFetch<VilleData[]>("/villes/");
}

export async function getMatieres(): Promise<Matiere[]> {
  return apiFetch<Matiere[]>("/matieres/");
}

export function logout(): boolean {
  clearTokens();
  return true;
}

// ─── Messagerie ───────────────────────────────────────────

export interface Conversation {
  id: number;
  correspondant_nom: string;
  correspondant_email: string;
  dernier_message: { content: string; created_at: string; est_moi: boolean } | null;
  nb_non_lus: number;
  updated_at: string;
}

export interface Message {
  id: number;
  sender: number;
  sender_email: string;
  sender_nom: string;
  content: string;
  created_at: string;
  is_read: boolean;
}

export async function getConversations(): Promise<Conversation[]> {
  return apiFetch<Conversation[]>("/messagerie/conversations/");
}

export async function createConversation(encadreurId: number): Promise<{ id: number; created: boolean }> {
  return apiFetch<{ id: number; created: boolean }>("/messagerie/conversations/create/", {
    method: "POST",
    body: JSON.stringify({ encadreur_id: encadreurId }),
  });
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  return apiFetch<Message[]>(`/messagerie/conversations/${conversationId}/`);
}

export async function sendMessage(conversationId: number, content: string): Promise<Message> {
  return apiFetch<Message>(`/messagerie/conversations/${conversationId}/`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function markAsRead(conversationId: number): Promise<{ marques_lus: number }> {
  return apiFetch<{ marques_lus: number }>(`/messagerie/conversations/${conversationId}/read/`, {
    method: "POST",
  });
}

// ─── Notifications ─────────────────────────────────────────

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at: string;
}

export async function getNotifications(): Promise<Notification[]> {
  return apiFetch<Notification[]>("/notifications/");
}

export async function markNotificationRead(id: number): Promise<void> {
  await apiFetch(`/notifications/${id}/read/`, { method: "POST" });
}

export async function markAllNotificationsRead(): Promise<{ marques_lus: number }> {
  return apiFetch<{ marques_lus: number }>("/notifications/read-all/", { method: "POST" });
}

// ─── Avis ───────────────────────────────────────────────────

export interface Avis {
  id: number;
  parent: number;
  parent_nom: string;
  parent_email: string;
  note: number;
  commentaire: string;
  created_at: string;
}

export async function getAvis(encadreurId: number): Promise<Avis[]> {
  return apiFetch<Avis[]>(`/encadreurs/${encadreurId}/avis/liste/`);
}

export async function createAvis(encadreurId: number, data: { note: number; commentaire?: string }): Promise<Avis> {
  return apiFetch<Avis>(`/encadreurs/${encadreurId}/avis/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAvis(encadreurId: number, avisId: number, data: { note: number; commentaire?: string }): Promise<Avis> {
  return apiFetch<Avis>(`/encadreurs/${encadreurId}/avis/${avisId}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteAvis(encadreurId: number, avisId: number): Promise<void> {
  await apiFetch(`/encadreurs/${encadreurId}/avis/${avisId}/`, { method: "DELETE" });
}

// ─── Paiement ──────────────────────────────────────────────

export interface Paiement {
  id: number;
  parent: number;
  parent_nom: string;
  encadreur: number;
  encadreur_nom: string;
  montant: number;
  type: "cours_mois" | "cours_horaire";
  statut: "en_attente" | "complete" | "echoue" | "rembourse";
  token_paydunya: string;
  receipt_url: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export async function initierPaiement(
  encadreurId: number,
  data: { montant: number; type: string; description?: string }
): Promise<{ paiement_id: number; invoice_url: string; token: string }> {
  return apiFetch(`/paiement/initier/${encadreurId}/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function verifierPaiement(token: string): Promise<Paiement> {
  return apiFetch<Paiement>(`/paiement/verifier/${token}/`);
}

export async function getHistoriquePaiements(): Promise<Paiement[]> {
  return apiFetch<Paiement[]>("/paiement/historique/");
}

// ─── Crédits ──────────────────────────────────────────────

export interface CreditStatus {
  credits_restants: number;
  total_achetes: number;
  total_utilises: number;
  debloque_ids: number[];
}

export interface CreditAchat {
  id: number;
  parent: number;
  credits_achetes: number;
  montant: number;
  token_paydunya: string;
  receipt_url: string;
  statut: "en_attente" | "complete" | "echoue";
  created_at: string;
}

export async function getCreditStatus(): Promise<CreditStatus> {
  return apiFetch<CreditStatus>("/credits/statut/");
}

export async function acheterCredits(): Promise<{ credit_achat_id: number; invoice_url: string }> {
  return apiFetch<{ credit_achat_id: number; invoice_url: string }>("/credits/acheter/", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function debloquerEncadreur(encadreurPk: number): Promise<{ conversation_id: number; credit_consomme: boolean }> {
  return apiFetch<{ conversation_id: number; credit_consomme: boolean }>(`/credits/debloquer/${encadreurPk}/`, {
    method: "POST",
  });
}
