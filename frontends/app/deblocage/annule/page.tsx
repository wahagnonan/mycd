"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function AnnulePage() {
  const [encadreurId, setEncadreurId] = useState<string | null>(null);

  useEffect(() => {
    const id = sessionStorage.getItem("credit_encadreur_id");
    sessionStorage.removeItem("credit_encadreur_id");
    setEncadreurId(id);
  }, []);

  const retryUrl = encadreurId ? `/encadreurs/${encadreurId}` : "/encadreurs";

  return (
    <div className="max-w-md mx-auto px-4 py-16 text-center">
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-zinc-900 mb-2">Paiement annulé</h1>
      <p className="text-zinc-500 mb-2">Aucun montant n&apos;a été débité.</p>
      <p className="text-sm text-zinc-400 mb-8">
        Vous pouvez réessayer quand vous le souhaitez.
      </p>
      <div className="flex flex-col gap-3">
        <Link
          href={retryUrl}
          className="w-full bg-orange-500 text-white py-3 rounded-xl font-medium hover:bg-orange-600 transition"
        >
          Réessayer
        </Link>
        <Link
          href="/encadreurs"
          className="w-full border border-zinc-300 text-zinc-700 py-3 rounded-xl font-medium hover:bg-zinc-50 transition"
        >
          Retour aux encadreurs
        </Link>
      </div>
    </div>
  );
}
