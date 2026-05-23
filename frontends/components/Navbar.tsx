"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import NotificationBell from "./NotificationBell";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-xl font-bold tracking-tight text-zinc-900">
          MYCD
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-zinc-600 sm:flex">
          <Link href="/" className="hover:text-zinc-900">Accueil</Link>
          <Link href="/encadreurs" className="hover:text-zinc-900">Encadreurs</Link>
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link href="/messagerie" className="hover:text-zinc-900">Messagerie</Link>
              {user?.role === "encadreur" && (
                <Link href="/mon-profil" className="hover:text-zinc-900">Mon profil</Link>
              )}
              <NotificationBell />
              <span className="text-zinc-900">{user?.email}</span>
              <button
                onClick={logout}
                className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm text-white hover:bg-zinc-800"
              >
                Déconnexion
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="rounded-lg px-3 py-1.5 hover:bg-zinc-100"
              >
                Connexion
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-zinc-900 px-3 py-1.5 text-white hover:bg-zinc-800"
              >
                Inscription
              </Link>
            </div>
          )}
        </nav>

        <button
          className="sm:hidden"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Menu"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {menuOpen ? (
              <path strokeLinecap="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-zinc-200 bg-white px-4 pb-4 pt-2 sm:hidden">
          <nav className="flex flex-col gap-3 text-sm font-medium text-zinc-600">
            <Link href="/" onClick={() => setMenuOpen(false)}>Accueil</Link>
            <Link href="/encadreurs" onClick={() => setMenuOpen(false)}>Encadreurs</Link>
            {isAuthenticated ? (
              <>
                <Link href="/messagerie" onClick={() => setMenuOpen(false)}>Messagerie</Link>
                {user?.role === "encadreur" && (
                  <Link href="/mon-profil" onClick={() => setMenuOpen(false)}>Mon profil</Link>
                )}
                <span className="text-zinc-900">{user?.email}</span>
                <button onClick={() => { logout(); setMenuOpen(false); }}
                  className="rounded-lg bg-zinc-900 px-3 py-1.5 text-white text-center">
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMenuOpen(false)}>Connexion</Link>
                <Link href="/register" onClick={() => setMenuOpen(false)}
                  className="rounded-lg bg-zinc-900 px-3 py-1.5 text-white text-center">
                  Inscription
                </Link>
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
