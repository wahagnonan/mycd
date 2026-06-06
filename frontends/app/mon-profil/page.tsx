"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import {
  getMatieres,
  getMonProfil,
  Matiere,
  ProfilEncadreur,
  updateMonProfil,
} from "@/lib/api";
import QuestionnaireEncadreur from "@/components/QuestionnaireEncadreur";

export default function MonProfilPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [profil, setProfil] = useState<ProfilEncadreur | null>(null);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const [bio, setBio] = useState("");
  const [tarifMois, setTarifMois] = useState("");
  const [tarifHoraire, setTarifHoraire] = useState("");
  const [typeTarif, setTypeTarif] = useState("mois");
  const [disponible, setDisponible] = useState(true);
  const [selectedMatieres, setSelectedMatieres] = useState<number[]>([]);
  const [autreMatiere, setAutreMatiere] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const [p, m] = await Promise.all([getMonProfil(), getMatieres()]);
      setProfil(p);
      setMatieres(m);
      setBio(p.bio || "");
      setTarifMois(p.tarif_mois?.toString() || "");
      setTarifHoraire(p.tarif_horaire?.toString() || "");
      setTypeTarif(p.type_tarif || "mois");
      setDisponible(p.disponible);
      setSelectedMatieres(p.matieres.map((m) => m.id));
      setAutreMatiere(p.autre_matiere || "");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Erreur de chargement";
      setError(msg);
      if (msg.includes("authentifié") || msg.includes("Session expirée")) {
        router.push("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user && user.role !== "encadreur") {
      router.push("/");
      return;
    }
    if (user) load();
  }, [user, authLoading, router, load]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await updateMonProfil({
        bio,
        tarif_mois: tarifMois ? Number(tarifMois) : null,
        tarif_horaire: tarifHoraire ? Number(tarifHoraire) : null,
        type_tarif: typeTarif,
        disponible,
        matiere_ids: selectedMatieres,
        autre_matiere: autreMatiere,
      } as any);
      setMessage("Profil mis à jour avec succès");
    } catch (err: any) {
      setMessage(err.message || "Erreur lors de la mise à jour");
    } finally {
      setSaving(false);
    }
  };

  const toggleMatiere = (id: number) => {
    setSelectedMatieres((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id],
    );
  };

  // Rechargement complet après avoir rempli le questionnaire
  const handleQuestionnaireComplete = () => {
    setLoading(true);
    load();
  };

  // Affichage du questionnaire si l'utilisateur ne l'a pas encore rempli
  if (!authLoading && !loading && profil && !profil.questionnaire_rempli) {
    return (
      <QuestionnaireEncadreur onComplete={handleQuestionnaireComplete} />
    );
  }

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md text-center">
          <p className="text-red-700 font-medium mb-2">Erreur</p>
          <p className="text-red-600 text-sm">{error}</p>
          <button
            onClick={() => { setError(""); setLoading(true); load(); }}
            className="mt-4 text-sm text-orange-500 hover:underline"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Mon Profil Encadreur</h1>

      {message && (
        <div
          className={`p-3 rounded mb-4 text-sm ${
            message.includes("succès")
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bio / Présentation
          </label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={4}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Parlez de vous, de votre expérience..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Matières enseignées
          </label>
          <div className="flex flex-wrap gap-2">
            {matieres.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => toggleMatiere(m.id)}
                className={`px-3 py-1.5 rounded-full text-sm border transition ${
                  selectedMatieres.includes(m.id)
                    ? "bg-orange-500 text-white border-orange-500"
                    : "bg-white text-gray-700 border-gray-300 hover:border-orange-400"
                }`}
              >
                {m.nom}
              </button>
            ))}
          </div>
          {selectedMatieres.includes(
            matieres.find((m) => m.nom === "Autre")?.id ?? -1,
          ) && (
            <div className="mt-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Précisez la/les matière(s)
              </label>
              <input
                type="text"
                value={autreMatiere}
                onChange={(e) => setAutreMatiere(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Ex: Arabe, Programmation, Danse..."
              />
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tarif mensuel (FCFA)
            </label>
            <input
              type="number"
              value={tarifMois}
              onChange={(e) => setTarifMois(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="50000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tarif horaire (FCFA)
            </label>
            <input
              type="number"
              value={tarifHoraire}
              onChange={(e) => setTarifHoraire(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="5000"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type de tarif par défaut
          </label>
          <select
            value={typeTarif}
            onChange={(e) => setTypeTarif(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="mois">Par mois</option>
            <option value="horaire">À l'heure</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="disponible"
            checked={disponible}
            onChange={(e) => setDisponible(e.target.checked)}
            className="h-4 w-4 text-orange-500 focus:ring-orange-500"
          />
          <label htmlFor="disponible" className="text-sm text-gray-700">
            Disponible pour de nouveaux élèves
          </label>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-orange-500 text-white py-2.5 rounded-lg font-medium hover:bg-orange-600 transition disabled:opacity-50"
        >
          {saving ? "Enregistrement..." : "Enregistrer le profil"}
        </button>
      </form>
    </div>
  );
}
