"use client";

import { use } from "react";
import { useEffect, useState } from "react";
import { acheterCredits, createConversation, debloquerEncadreur, getCreditStatus, getEncadreur, ProfilEncadreur } from "@/lib/api";
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
  const [creditsRestants, setCreditsRestants] = useState<number | null>(null);
  const [deblocageLoading, setDeblocageLoading] = useState(false);

  useEffect(() => {
    getEncadreur(Number(id))
      .then(setProfil)
      .catch(() => setError("Encadreur introuvable"))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (isAuthenticated && user?.role === "parent") {
      getCreditStatus()
        .then(s => setCreditsRestants(s.credits_restants))
        .catch(() => setCreditsRestants(0));
    } else {
      setCreditsRestants(null);
    }
  }, [isAuthenticated, user]);

  const handleContact = async () => {
    setContactError("");
    setContactLoading(true);

    if (!isAuthenticated) { router.push("/login"); return; }
    if (user?.role !== "parent") {
      router.push("/messagerie");
      return;
    }
    if (!profil) {
      setContactError("Impossible de contacter cet encadreur");
      setContactLoading(false);
      return;
    }

    try {
      // Si déjà débloqué, créer directement la conversation
      if (profil.debloque) {
        const conv = await createConversation(profil.user_id);
        router.push(`/messagerie/${conv.id}`);
        return;
      }

      // Sinon, tenter de débloquer
      const result = await debloquerEncadreur(profil.id);
      router.push(`/messagerie/${result.conversation_id}`);
    } catch (err) {
      if (err instanceof Error) {
        // Crédits insuffisants → rediriger vers achat
        if (err.message.includes("402") || err.message.includes("Crédits insuffisants") || err.message.includes("credits")) {
          setContactError("Crédits insuffisants. Achetez des crédits pour contacter cet encadreur.");
          setContactLoading(false);
          return;
        }
        setContactError(err.message);
      } else {
        setContactError("Erreur réseau");
      }
    } finally {
      setContactLoading(false);
    }
  };

  const handleDebloquer = async () => {
    setDeblocageLoading(true);
    try {
      sessionStorage.setItem("credit_encadreur_id", id);
      const result = await acheterCredits();
      window.location.href = result.invoice_url;
    } catch {
      setDeblocageLoading(false);
      setContactError("Erreur de paiement. Veuillez réessayer.");
    }
  };

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

  const showBlur = isAuthenticated && user?.role === "parent" && creditsRestants === 0;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <Link href="/encadreurs" className="text-orange-500 hover:underline text-sm inline-flex items-center gap-1">
        &larr; Retour à la liste
      </Link>

      <div className="relative mt-4">

        <div className={`${showBlur ? "filter blur-md pointer-events-none select-none" : ""}`}>
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-8 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center text-2xl font-bold text-white/80 shrink-0">
                    {profil.nom.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold">{profil.nom}</h1>
                    {profil.email && <p className="text-orange-100 text-sm mt-0.5">{profil.email}</p>}
                    {profil.phone && <p className="text-orange-100 text-sm">{profil.phone}</p>}
                    <button
                      onClick={handleContact}
                      disabled={contactLoading}
                      className="mt-2 bg-white text-orange-600 px-3 py-1 rounded text-sm font-medium hover:bg-orange-50 transition disabled:opacity-50"
                    >
                      {contactLoading ? "..." : "Contacter"}
                    </button>
                  </div>
                </div>
                {profil.verified && (
                  <span className="bg-white/20 text-white text-xs px-2 py-0.5 rounded-full shrink-0">
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
                <button
                  onClick={handleContact}
                  disabled={contactLoading}
                  className={`px-5 py-2 rounded-lg transition font-medium text-sm disabled:opacity-50 ${
                    user?.role === "parent" && !profil.debloque
                      ? "bg-green-600 text-white hover:bg-green-700"
                      : "bg-orange-500 text-white hover:bg-orange-600"
                  }`}
                >
                  {contactLoading ? "..." : user?.role === "parent" && !profil.debloque ? "Débloquer & Contacter" : user?.role === "parent" ? "Contacter" : "Messagerie"}
                </button>
              </div>
            </div>
          </div>
        </div>

        {showBlur && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/5 rounded-xl">
            <div className="bg-white/95 backdrop-blur rounded-2xl p-8 text-center shadow-xl max-w-xs mx-4">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-zinc-900 mb-1">Profil verrouillé</h3>
              <p className="text-sm text-zinc-500 mb-6">
                Débloquez l&apos;accès aux profils et à la messagerie pour 1 000 FCFA
              </p>
              <button
                onClick={handleDebloquer}
                disabled={deblocageLoading}
                className="w-full bg-orange-500 text-white py-3 rounded-xl font-medium hover:bg-orange-600 transition disabled:opacity-50"
              >
                {deblocageLoading ? "Redirection..." : "Débloquer — 1 000 FCFA"}
              </button>
              <p className="text-xs text-zinc-400 mt-3">
                1 000 FCFA = 3 crédits · Paiement sécurisé via PayDunya
              </p>
            </div>
          </div>
        )}
      </div>

      <AvisSection encadreurId={profil.id} />
    </div>
  );
}
