"use client";

import Link from "next/link";

export default function PaiementAnnulePage() {
  return (
    <div className="max-w-md mx-auto px-4 py-16 text-center">
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h1 className="text-xl font-bold text-zinc-900 mb-2">Paiement annulé</h1>
      <p className="text-zinc-500 mb-6">Vous avez annulé le paiement. Aucun montant n'a été débité.</p>
      <div className="flex justify-center gap-4">
        <Link href="/encadreurs" className="border border-zinc-300 px-5 py-2 rounded-lg text-sm font-medium hover:bg-zinc-50 transition">
          Retour aux encadreurs
        </Link>
        <Link href="/messagerie" className="bg-orange-500 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition">
          Messagerie
        </Link>
      </div>
    </div>
  );
}
