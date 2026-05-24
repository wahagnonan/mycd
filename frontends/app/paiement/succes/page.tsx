"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { verifierPaiement, Paiement } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

function SuccesContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const { isAuthenticated, isLoading } = useAuth();
  const [paiement, setPaiement] = useState<Paiement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) { setLoading(false); setError("Vous devez être connecté"); return; }
    if (!isLoading && token) {
      verifierPaiement(token)
        .then((p) => { setPaiement(p); setLoading(false); })
        .catch(() => { setError("Erreur lors de la vérification du paiement"); setLoading(false); });
    } else if (!isLoading && !token) {
      setError("Aucune information de paiement");
      setLoading(false);
    }
  }, [token, isAuthenticated, isLoading]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500" />
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 py-16 text-center">
      {error ? (
        <div>
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-zinc-900 mb-2">Paiement non confirmé</h1>
          <p className="text-zinc-500 mb-6">{error}</p>
          <Link href="/encadreurs" className="text-orange-500 hover:underline">Retour aux encadreurs</Link>
        </div>
      ) : paiement?.statut === "complete" ? (
        <div>
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-zinc-900 mb-2">Paiement réussi !</h1>
          <p className="text-zinc-500 mb-2">
            {paiement.montant.toLocaleString()} FCFA — {paiement.description || "Cours"}
          </p>
          <div className="flex justify-center gap-4 mt-6">
            <Link href="/messagerie" className="bg-orange-500 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition">
              Voir mes messages
            </Link>
            <Link href="/encadreurs" className="border border-zinc-300 px-5 py-2 rounded-lg text-sm font-medium hover:bg-zinc-50 transition">
              Retour aux encadreurs
            </Link>
          </div>
        </div>
      ) : (
        <div>
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-zinc-900 mb-2">Paiement en attente</h1>
          <p className="text-zinc-500 mb-6">Le statut sera mis à jour automatiquement.</p>
          <Link href="/paiement/historique" className="text-orange-500 hover:underline">Voir l'historique</Link>
        </div>
      )}
    </div>
  );
}

export default function PaiementSuccesPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500" />
      </div>
    }>
      <SuccesContent />
    </Suspense>
  );
}
