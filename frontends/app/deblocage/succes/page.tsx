"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

function SuccessContent() {
  const searchParams = useSearchParams();
  const [encadreurId, setEncadreurId] = useState<string | null>(null);

  useEffect(() => {
    const id = sessionStorage.getItem("credit_encadreur_id");
    sessionStorage.removeItem("credit_encadreur_id");
    setEncadreurId(id);
  }, []);

  const profilUrl = encadreurId ? `/encadreurs/${encadreurId}` : "/encadreurs";

  return (
    <div className="max-w-md mx-auto px-4 py-16 text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-zinc-900 mb-2">Paiement réussi !</h1>
      <p className="text-zinc-500 mb-2">
        Vous avez obtenu <strong>3 crédits de contact</strong>.
      </p>
      <p className="text-sm text-zinc-400 mb-8">
        Utilisez ces crédits pour contacter les encadreurs de votre choix.
      </p>
      <div className="flex flex-col gap-3">
        <Link
          href={profilUrl}
          className="w-full bg-orange-500 text-white py-3 rounded-xl font-medium hover:bg-orange-600 transition"
        >
          {profilUrl !== "/encadreurs" ? "Retourner au profil" : "Parcourir les encadreurs"}
        </Link>
        <Link
          href="/encadreurs"
          className="w-full border border-zinc-300 text-zinc-700 py-3 rounded-xl font-medium hover:bg-zinc-50 transition"
        >
          Parcourir les encadreurs
        </Link>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500" />
      </div>
    }>
      <SuccessContent />
    </Suspense>
  );
}
