"use client";

import { use } from "react";
import { useEffect, useState } from "react";
import { createConversation, getEncadreur, ProfilEncadreur } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { useRouter } from "next/navigation";
import RatingStars from "@/components/RatingStars";
import AvisSection from "@/components/AvisSection";

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "numeric", month: "long", year: "numeric",
  });
}

function TarifLabel({ type }: { type: string }) {
  const labels: Record<string, string> = {
    mois: "Au mois",
    horaire: "À l'heure",
    les_deux: "Les deux",
  };
  return <span className="text-xs text-gray-400">({labels[type] || type})</span>;
}

export default function EncadreurDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const [profil, setProfil] = useState<ProfilEncadreur | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [contactLoading, setContactLoading] = useState(false);
  const [contactError, setContactError] = useState("");

  useEffect(() => {
    getEncadreur(Number(id))
      .then(setProfil)
      .catch(() => setError("Encadreur introuvable"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (error || !profil) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500">{error || "Encadreur introuvable"}</p>
        <Link href="/encadreurs" className="text-orange-500 hover:underline mt-2 inline-block">
          Retour à la liste
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <Link href="/encadreurs" className="text-orange-500 hover:underline text-sm inline-flex items-center gap-1">
        &larr; Retour à la liste
      </Link>

      <div className="mt-4 bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-8 text-white">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold">{profil.nom}</h1>
              <p className="text-orange-100 mt-1">{profil.email}</p>
              <p className="text-orange-100">{profil.phone}</p>
            </div>
            {profil.verified && (
              <span className="bg-white/20 text-white text-sm px-3 py-1 rounded-full flex items-center gap-1">
                Vérifié
              </span>
            )}
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex flex-wrap gap-6">
            {profil.ville && (
              <div className="flex items-center gap-2 text-gray-600">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {profil.ville}{profil.quartier ? `, ${profil.quartier}` : ""}
              </div>
            )}
            <div className="flex items-center gap-2 text-gray-600">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Membre depuis {formatDate(profil.date_inscription)}
            </div>
          </div>

          {profil.bio && (
            <div>
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Présentation</h2>
              <p className="text-gray-600 leading-relaxed whitespace-pre-line">{profil.bio}</p>
            </div>
          )}

          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-2">Matières enseignées</h2>
            <div className="flex flex-wrap gap-2">
              {profil.matieres.map((m) => (
                <span
                  key={m.id}
                  className="bg-orange-50 text-orange-700 border border-orange-200 px-3 py-1 rounded-full text-sm font-medium"
                >
                  {m.nom}
                </span>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-500 mb-1">Note moyenne</p>
              {profil.note_moyenne > 0 ? (
                <>
                  <div className="flex justify-center mb-1">
                    <RatingStars note={profil.note_moyenne} size="md" />
                  </div>
                  <p className="text-sm font-semibold text-gray-800">{profil.note_moyenne.toFixed(1)}</p>
                  <p className="text-xs text-gray-400">{profil.nombre_avis} avis</p>
                </>
              ) : (
                <p className="text-2xl font-bold text-gray-800">—</p>
              )}
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-500 mb-1">Tarif mensuel</p>
              <p className="text-2xl font-bold text-gray-800">
                {profil.tarif_mois ? `${profil.tarif_mois.toLocaleString()} FCFA` : "—"}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-500 mb-1">Tarif horaire</p>
              <p className="text-2xl font-bold text-gray-800">
                {profil.tarif_horaire ? `${profil.tarif_horaire.toLocaleString()} FCFA` : "—"}
              </p>
            </div>
          </div>

          {profil.type_tarif && (
            <p className="text-sm text-gray-500 text-center">
              Type de tarif : <span className="font-medium">{profil.type_tarif}</span>
              <TarifLabel type={profil.type_tarif} />
            </p>
          )}

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2">
              <span
                className={`h-3 w-3 rounded-full ${
                  profil.disponible ? "bg-green-500" : "bg-red-400"
                }`}
              />
              <span className="text-sm font-medium text-gray-700">
                {profil.disponible ? "Disponible" : "Non disponible"}
              </span>
            </div>
            {contactError && (
              <p className="text-red-500 text-sm">{contactError}</p>
            )}
            <div className="flex items-center gap-2">
              {user?.role === "parent" && (
                <Link
                  href={`/paiement/${profil.id}`}
                  className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition font-medium text-sm"
                >
                  Payer
                </Link>
              )}
              <button
                onClick={async () => {
                  setContactError("");
                  if (!isAuthenticated) { router.push("/login"); return; }
                  if (user?.role !== "parent") {
                    router.push("/messagerie");
                    return;
                  }
                  if (!profil.user_id) {
                    setContactError("Impossible de contacter cet encadreur");
                    return;
                  }
                  setContactLoading(true);
                  try {
                    const conv = await createConversation(profil.user_id);
                    router.push(`/messagerie/${conv.id}`);
                  } catch (err) {
                    setContactError(
                      err instanceof Error ? err.message : "Erreur réseau"
                    );
                    setContactLoading(false);
                  }
                }}
                disabled={contactLoading}
                className="bg-orange-500 text-white px-5 py-2 rounded-lg hover:bg-orange-600 transition font-medium text-sm disabled:opacity-50"
              >
                {contactLoading ? "..." : user?.role === "parent" ? "Contacter" : "Messagerie"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <AvisSection encadreurId={profil.id} />
    </div>
  );
}
