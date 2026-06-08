import { describe, it, expect, beforeEach, vi } from "vitest";

const API_URL = "http://localhost:8000/api";

function validToken(): string {
  const payload = btoa(JSON.stringify({ exp: 9_999_999_999 }));
  return `header.${payload}.sig`;
}

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("apiFetch", () => {
  it("adds auth header when token exists", async () => {
    const tok = validToken();
    localStorage.setItem("access_token", tok);
    localStorage.setItem("refresh_token", "test-refresh-token");

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: "ok" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { apiFetch } = await import("@/lib/api");
    await apiFetch("/test/");

    const callArgs = mockFetch.mock.calls[0];
    expect(callArgs[0]).toBe(`${API_URL}/test/`);
    expect(callArgs[1].headers.Authorization).toBe(`Bearer ${tok}`);
  });

  it("throws AuthError on 401", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Non authentifié" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { apiFetch, AuthError } = await import("@/lib/api");
    await expect(apiFetch("/test/")).rejects.toThrow(AuthError);
  });

  it("throws AuthError on 403", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: () => Promise.resolve({}),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { apiFetch, AuthError } = await import("@/lib/api");
    await expect(apiFetch("/test/")).rejects.toThrow(AuthError);
  });

  it("throws error on 429", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: () => Promise.resolve({}),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { apiFetch } = await import("@/lib/api");
    await expect(apiFetch("/test/")).rejects.toThrow("Trop de requêtes");
  });

  it("throws network error when fetch fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const { apiFetch } = await import("@/lib/api");
    await expect(apiFetch("/test/")).rejects.toThrow("Erreur réseau");
  });
});

describe("register", () => {
  it("sends registration data", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        user: { id: 1, email: "test@test.com", role: "parent" },
        access: "access-token",
        refresh: "refresh-token",
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { register } = await import("@/lib/api");
    const user = await register({
      email: "test@test.com",
      phone: "+2250101010101",
      password: "secret123",
      password2: "secret123",
      role: "parent",
    });

    expect(user.email).toBe("test@test.com");
    expect(localStorage.getItem("access_token")).toBe("access-token");
  });

  it("normalizes phone without +225 prefix", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        user: { id: 1, email: "test@test.com", role: "parent" },
        access: "a",
        refresh: "r",
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { register } = await import("@/lib/api");
    await register({
      email: "test@test.com",
      phone: "0101010101",
      password: "secret123",
      password2: "secret123",
      role: "parent",
    });

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.phone).toBe("+2250101010101");
  });

  it("throws error when registration fails", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ email: ["Cet email est déjà utilisé"] }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { register } = await import("@/lib/api");
    await expect(register({
      email: "existing@test.com",
      phone: "+2250101010101",
      password: "secret123",
      password2: "secret123",
      role: "parent",
    })).rejects.toThrow("Cet email est déjà utilisé");
  });
});

describe("login", () => {
  it("sends credentials and stores tokens", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        user: { id: 1, email: "test@test.com", role: "parent" },
        access: "access-token",
        refresh: "refresh-token",
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { login } = await import("@/lib/api");
    const user = await login("test@test.com", "secret123");

    expect(user.email).toBe("test@test.com");
    expect(localStorage.getItem("access_token")).toBe("access-token");
    expect(localStorage.getItem("refresh_token")).toBe("refresh-token");
  });

  it("throws on wrong credentials", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: "Email ou mot de passe incorrect" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { login } = await import("@/lib/api");
    await expect(login("wrong@test.com", "bad")).rejects.toThrow("Email ou mot de passe incorrect");
  });
});

describe("getVilles", () => {
  it("fetches and returns villes", async () => {
    const mockData = [{ ville: "Abidjan", quartiers: ["Cocody"] }];
    localStorage.setItem("access_token", validToken());
    localStorage.setItem("refresh_token", "tok");

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { getVilles } = await import("@/lib/api");
    const villes = await getVilles();

    expect(villes).toEqual(mockData);
    expect(mockFetch.mock.calls[0][0]).toContain("/villes/");
  });

  it("uses unauthenticated fetch when no token", async () => {
    const mockData = [{ ville: "Abidjan", quartiers: ["Cocody"] }];
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { getVilles } = await import("@/lib/api");
    const villes = await getVilles();

    expect(villes).toEqual(mockData);
    expect(mockFetch.mock.calls[0][1]?.headers?.Authorization).toBeUndefined();
  });
});

describe("getEncadreurs", () => {
  it("builds query string from params", async () => {
    localStorage.setItem("access_token", validToken());
    localStorage.setItem("refresh_token", "tok");
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ count: 0, next: null, previous: null, results: [] }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { getEncadreurs } = await import("@/lib/api");
    await getEncadreurs({ ville: "Abidjan", matiere: "1", page: 2 });

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("ville=Abidjan");
    expect(url).toContain("matiere=1");
    expect(url).toContain("page=2");
  });
});

describe("logout", () => {
  it("clears tokens from localStorage", async () => {
    localStorage.setItem("access_token", "tok");
    localStorage.setItem("refresh_token", "tok");

    const { logout } = await import("@/lib/api");
    const result = logout();

    expect(result).toBe(true);
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });
});

describe("getMe", () => {
  it("fetches current user profile", async () => {
    const mockUser = { id: 1, email: "user@test.com", role: "parent", phone: "+2250101010101", ville: "", quartier: "" };
    localStorage.setItem("access_token", validToken());
    localStorage.setItem("refresh_token", "tok");

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { getMe } = await import("@/lib/api");
    const user = await getMe();
    expect(user.email).toBe("user@test.com");
  });
});

