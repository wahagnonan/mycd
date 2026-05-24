"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getHistoriquePaiements, Paiement } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

const statutLabels: Record<string, { label: string; cls: string }> = {
  en_attente: { label: "En attente", cls: "bg-amber-100 text-amber-800" },
  complete: { label: "Complété", cls: "bg-green-100 text-green-800" },
  echoue: { label: "Échoué", cls: "bg-red-100 text-red-800" },
  rembourse: { label: "Remboursé", cls: "bg-blue-100 text-blue-800" },
};

export default function HistoriquePaiementsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const [paiements, setPaiements] = useState<Paiement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      getHistoriquePaiements()
        .then(setPaiements)
        .catch(() => {})
        .finally(() => setLoading(false));
    } else if (!isLoading) {
      setLoading(false);
    }
  }, [isAuthenticated, isLoading]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-zinc-900 mb-6">Historique des paiements</h1>

      {paiements.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-zinc-500 mb-4">Aucun paiement effectué.</p>
          <Link href="/encadreurs" className="text-orange-500 hover:underline">
            Trouver un encadreur
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {paiements.map((p) => (
            <div key={p.id} className="bg-white border border-zinc-200 rounded-xl px-5 py-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-900">{p.encadreur_nom}</p>
                <p className="text-xs text-zinc-500 mt-0.5">
                  {p.montant.toLocaleString()} FCFA
                  {p.description ? ` — ${p.description}` : ""}
                </p>
                <p className="text-xs text-zinc-400 mt-1">
                  {new Date(p.created_at).toLocaleDateString("fr-FR", {
                    day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit",
                  })}
                </p>
              </div>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statutLabels[p.statut]?.cls || "bg-zinc-100 text-zinc-700"}`}>
                {statutLabels[p.statut]?.label || p.statut}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
