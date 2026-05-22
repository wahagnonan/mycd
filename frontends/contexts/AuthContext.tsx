"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthError, getMe, login as apiLogin, logout as apiLogout, register as apiRegister } from "@/lib/api";

export interface User {
  id: number;
  email: string;
  phone: string;
  role: string;
  ville: string;
  quartier: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  register: (data: {
    email: string;
    phone: string;
    password: string;
    password2: string;
    role: string;
    ville?: string;
    quartier?: string;
  }) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function AuthProviderInner({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== "undefined" && localStorage.getItem("access_token");
    if (!token) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    getMe()
      .then((u) => { if (!cancelled) setUser(u); })
      .catch((err) => {
        if (err instanceof AuthError && err.redirect) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const handleRegister = async (data: {
    email: string; phone: string; password: string; password2: string;
    role: string; ville?: string; quartier?: string;
  }) => {
    const u = await apiRegister(data);
    setUser(u);
    router.push("/");
  };

  const handleLogin = async (email: string, password: string) => {
    const u = await apiLogin(email, password);
    setUser(u);
    router.push("/");
  };

  const handleLogout = () => {
    setUser(null);
    apiLogout();
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user, isLoading, isAuthenticated: !!user,
        register: handleRegister, login: handleLogin, logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <AuthProviderInner>
      {children}
    </AuthProviderInner>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
