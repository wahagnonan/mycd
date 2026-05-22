const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

let refreshPromise: Promise<string | null> | null = null;

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
  if (refreshPromise) return refreshPromise;

  refreshPromise = fetch(`${API_URL}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  })
    .then(async (res) => {
      if (!res.ok) return null;
      const data = await res.json();
      setTokens(data.access, refresh);
      return data.access;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const tokens = getTokens();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (tokens) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${tokens.access}`;
  }

  let res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (res.status === 401 && tokens?.refresh) {
    const newAccess = await refreshAccessToken(tokens.refresh);
    if (newAccess) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${newAccess}`;
      res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    } else {
      clearTokens();
      throw new AuthError("Session expirée", true);
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      throw new AuthError("Non authentifié", false);
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
  const res = await fetch(`${API_URL}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      err.email?.[0] || err.phone?.[0] || err.detail || "Erreur lors de l'inscription",
    );
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

export function logout(): boolean {
  clearTokens();
  return true;
}
