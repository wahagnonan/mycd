"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

const VILLES = ["Abidjan", "Bouaké", "Korhogo", "Yamoussoukro", "San-Pédro", "Gagnoa", "Man", "Daloa"];

const QUARTIERS_ABIDJAN = [
  "Cocody", "Plateau", "Treichville", "Adjamé", "Yopougon",
  "Abobo", "Marcory", "Koumassi", "Port-Bouët", "Attécoubé",
];

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
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
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
            <input
              id="phone" type="tel" required
              value={form.phone}
              onChange={(e) => update("phone", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="+2250102030405"
            />
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
              {VILLES.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          {form.ville === "Abidjan" && (
            <div>
              <label htmlFor="quartier" className="block text-sm font-medium text-zinc-700">
                Quartier
              </label>
              <select
                id="quartier"
                value={form.quartier}
                onChange={(e) => update("quartier", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              >
                <option value="">Sélectionnez un quartier</option>
                {QUARTIERS_ABIDJAN.map((q) => <option key={q} value={q}>{q}</option>)}
              </select>
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
            <input
              id="password" type="password" required minLength={6}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="••••••••"
            />
          </div>
          <div>
            <label htmlFor="password2" className="block text-sm font-medium text-zinc-700">
              Confirmer le mot de passe
            </label>
            <input
              id="password2" type="password" required minLength={6}
              value={form.password2}
              onChange={(e) => update("password2", e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="••••••••"
            />
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
