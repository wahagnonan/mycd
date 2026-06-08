import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

function validToken(): string {
  const payload = btoa(JSON.stringify({ exp: 9_999_999_999 }));
  return `header.${payload}.sig`;
}

beforeEach(() => {
  localStorage.clear();
  mockPush.mockClear();
  vi.restoreAllMocks();
});

async function setupTest() {
  const { AuthProvider, useAuth } = await import("@/contexts/AuthContext");
  function TestConsumer() {
    const auth = useAuth();
    return (
      <div>
        <span data-testid="auth-status">
          {auth.isLoading ? "loading" : auth.isAuthenticated ? "authenticated" : "anonymous"}
        </span>
        {auth.user && <span data-testid="user-email">{auth.user.email}</span>}
        <button data-testid="btn-login" onClick={() => auth.login("test@test.com", "pass")}>
          Login
        </button>
        <button data-testid="btn-register" onClick={() => auth.register({
          email: "new@test.com", phone: "+2250101010101",
          password: "pass123", password2: "pass123", role: "parent",
        })}>
          Register
        </button>
        <button data-testid="btn-logout" onClick={() => auth.logout()}>
          Logout
        </button>
      </div>
    );
  }
  render(
    <AuthProvider>
      <TestConsumer />
    </AuthProvider>
  );
}

describe("AuthContext", () => {
  it("shows anonymous when no token", async () => {
    vi.stubGlobal("fetch", vi.fn());
    await setupTest();

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("anonymous");
    });
  });

  it("loads user when token exists", async () => {
    localStorage.setItem("access_token", validToken());
    localStorage.setItem("refresh_token", "refresh-token");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        id: 1, email: "user@test.com", role: "parent",
        phone: "+2250101010101", ville: "", quartier: "",
      }),
    }));

    await setupTest();

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("authenticated");
    });
    expect(screen.getByTestId("user-email").textContent).toBe("user@test.com");
  });

  it("handles login", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        user: { id: 1, email: "test@test.com", role: "parent",
                phone: "+2250101010101", ville: "", quartier: "" },
        access: "access-tok",
        refresh: "refresh-tok",
      }),
    }));

    await setupTest();

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("anonymous");
    });

    await userEvent.click(screen.getByTestId("btn-login"));

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("authenticated");
    });
    expect(mockPush).toHaveBeenCalledWith("/encadreurs");
  });

  it("handles registration", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        user: { id: 1, email: "new@test.com", role: "parent",
                phone: "+2250101010101", ville: "", quartier: "" },
        access: "access-tok",
        refresh: "refresh-tok",
      }),
    }));

    await setupTest();

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("anonymous");
    });

    await userEvent.click(screen.getByTestId("btn-register"));

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("authenticated");
    });
    expect(screen.getByTestId("user-email").textContent).toBe("new@test.com");
  });

  it("handles logout", async () => {
    localStorage.setItem("access_token", validToken());
    localStorage.setItem("refresh_token", "tok");

    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        id: 1, email: "u@test.com", role: "parent",
        phone: "+2250101010101", ville: "", quartier: "",
      }),
    }));

    await setupTest();

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("authenticated");
    });

    await userEvent.click(screen.getByTestId("btn-logout"));

    await waitFor(() => {
      expect(screen.getByTestId("auth-status").textContent).toBe("anonymous");
    });
    expect(mockPush).toHaveBeenCalledWith("/login");
  });
});
