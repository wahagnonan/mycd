"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getEncadreur, initierPaiement, ProfilEncadreur } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function PaiementPage({ params }: { params: Promise<{ encadreurId: string }> }) {
  const { encadreurId } = use(params);
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();
  const [profil, setProfil] = useState<ProfilEncadreur | null>(null);
  const [loading, setLoading] = useState(true);
  const [montant, setMontant] = useState("");
  const [type, setType] = useState("cours_mois");
  const [description, setDescription] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) { router.push("/login"); return; }
    if (!isLoading && user?.role !== "parent") { router.push("/"); return; }
    getEncadreur(Number(encadreurId))
      .then(setProfil)
      .catch(() => setError("Encadreur introuvable"))
      .finally(() => setLoading(false));
  }, [encadreurId, isAuthenticated, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!montant || Number(montant) < 100) { setError("Montant minimum : 100 FCFA"); return; }
    setSending(true);
    try {
      const result = await initierPaiement(Number(encadreurId), {
        montant: Number(montant),
        type,
        description: description || undefined,
      });
      window.location.href = result.invoice_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors du paiement");
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500" />
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8">
      <Link href={`/encadreurs/${encadreurId}`} className="text-orange-500 hover:underline text-sm">
        &larr; Retour au profil
      </Link>

      <div className="mt-4 bg-white border border-zinc-200 rounded-xl p-6">
        <h1 className="text-xl font-bold text-zinc-900 mb-1">Paiement</h1>
        {profil && <p className="text-sm text-zinc-500 mb-6">Pour {profil.nom}</p>}

        {error && (
          <p className="text-red-500 text-sm mb-4 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Type de paiement</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="cours_mois">Cours au mois</option>
              <option value="cours_horaire">Cours à l'heure</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Montant (FCFA)</label>
            <input
              type="number"
              value={montant}
              onChange={(e) => setMontant(e.target.value)}
              placeholder="Ex: 25000"
              min="100"
              max="1000000"
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Description (optionnelle)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: Cours de maths - avril 2026"
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <button
            type="submit"
            disabled={sending}
            className="w-full bg-orange-500 text-white py-3 rounded-lg font-medium hover:bg-orange-600 transition disabled:opacity-50"
          >
            {sending ? "Redirection vers PayDunya..." : "Payer avec PayDunya"}
          </button>
        </form>

        <p className="text-xs text-zinc-400 mt-4 text-center">
          Paiement sécurisé via <a href="https://paydunya.com" target="_blank" className="underline">PayDunya</a>.
          Moyens acceptés : Orange Money, MTN, Wave, Moov, etc.
        </p>
      </div>
    </div>
  );
}
