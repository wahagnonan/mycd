"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { getVilles, VilleData } from "@/lib/api";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    phone: "",
    password: "",
    password2: "",
    role: "parent",
    ville: "",
    quartier: "",
  });
  const [villeAutre, setVilleAutre] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [villes, setVilles] = useState<VilleData[]>([]);
  const { register, isLoading, isAuthenticated, redirectIfAuthenticated } = useAuth();

  useEffect(() => {
    getVilles().then(setVilles).catch(() => {});
  }, []);

  const villeData = villes.find((v) => v.ville === form.ville);

  const villeFinale = form.ville === "Autre" ? villeAutre : form.ville;

  // Rediriger vers / si déjà connecté
  useEffect(() => {
    redirectIfAuthenticated();
  }, [redirectIfAuthenticated]);

  // Ne pas afficher le formulaire pendant le chargement ou si déjà connecté
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-zinc-900"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return null; // la redirection est en cours
  }

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ ...form, ville: villeFinale });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Une erreur est survenue");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-4">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-2xl font-bold text-center">Inscription</h1>
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-zinc-700">
              Email
            </label>
            <input
              id="email" type="email" required
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="exemple@email.com"
            />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-zinc-700">
              Téléphone
            </label>
            <div className="mt-1 flex rounded-lg border border-zinc-300 focus-within:border-zinc-500">
              <span className="flex items-center px-3 text-sm text-zinc-500 bg-zinc-50 rounded-l-lg border-r border-zinc-300">
                +225
              </span>
              <input
                id="phone" type="tel" required maxLength={10}
                value={form.phone.replace("+225", "")}
                onChange={(e) => {
                  const digits = e.target.value.replace(/\D/g, "").slice(0, 10);
                  update("phone", `+225${digits}`);
                }}
                className="block w-full px-3 py-2 text-sm focus:outline-none rounded-r-lg"
                placeholder="0102030405"
              />
            </div>
          </div>
          <div>
            <label htmlFor="ville" className="block text-sm font-medium text-zinc-700">
              Ville
            </label>
            <select
              id="ville"
              value={form.ville}
              onChange={(e) => update("ville", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            >
              <option value="">Sélectionnez une ville</option>
              {villes.map((v) => <option key={v.ville} value={v.ville}>{v.ville}</option>)}
            </select>
          </div>
          {villeData && villeData.quartiers.length > 0 && (
            <div>
              <label htmlFor="quartier" className="block text-sm font-medium text-zinc-700">
                Quartier / Commune
              </label>
              <select
                id="quartier"
                value={form.quartier}
                onChange={(e) => update("quartier", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              >
                <option value="">Sélectionnez un quartier / une commune</option>
                {villeData.quartiers.map((q) => <option key={q} value={q}>{q}</option>)}
              </select>
            </div>
          )}
          {form.ville === "Autre" && (
            <div>
              <label htmlFor="ville_autre" className="block text-sm font-medium text-zinc-700">
                Précisez votre ville
              </label>
              <input
                id="ville_autre" type="text" required
                value={villeAutre}
                onChange={(e) => setVilleAutre(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
                placeholder="Nom de votre ville"
              />
            </div>
          )}
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-zinc-700">
              Je suis
            </label>
            <select
              id="role"
              value={form.role}
              onChange={(e) => update("role", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            >
              <option value="parent">Parent</option>
              <option value="encadreur">Encadreur</option>
            </select>
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-zinc-700">
              Mot de passe
            </label>
            <div className="mt-1 flex rounded-lg border border-zinc-300 focus-within:border-zinc-500">
              <input
                id="password" type={showPassword ? "text" : "password"} required minLength={6}
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                className="block w-full rounded-l-lg px-3 py-2 text-sm focus:outline-none"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="flex items-center px-3 text-zinc-400 hover:text-zinc-600"
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
          <div>
            <label htmlFor="password2" className="block text-sm font-medium text-zinc-700">
              Confirmer le mot de passe
            </label>
            <div className="mt-1 flex rounded-lg border border-zinc-300 focus-within:border-zinc-500">
              <input
                id="password2" type={showPassword2 ? "text" : "password"} required minLength={6}
                value={form.password2}
                onChange={(e) => update("password2", e.target.value)}
                className="block w-full rounded-l-lg px-3 py-2 text-sm focus:outline-none"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword2(!showPassword2)}
                className="flex items-center px-3 text-zinc-400 hover:text-zinc-600"
                tabIndex={-1}
              >
                {showPassword2 ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
          >
            {loading ? "Inscription..." : "S'inscrire"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-zinc-500">
          Déjà un compte ?{" "}
          <Link href="/login" className="font-medium text-zinc-900 hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}
