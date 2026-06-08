"use client";

import { useState } from "react";
import { ProfilEncadreurUpdate, updateMonProfil } from "@/lib/api";

const NIVEAU_ETUDES_OPTIONS = [
  { value: "bac_en_cours", label: "BAC en cours" },
  { value: "bac", label: "BAC" },
  { value: "bac_plus_1", label: "BAC+1" },
  { value: "bac_plus_2", label: "BAC+2" },
  { value: "bac_plus_3", label: "BAC+3" },
  { value: "bac_plus_4", label: "BAC+4" },
  { value: "bac_plus_5", label: "BAC+5" },
  { value: "doctorat", label: "Doctorat" },
  { value: "autre", label: "Autre" },
];

const NIVEAUX_ENSEIGNEMENT_OPTIONS = [
  { value: "primaire", label: "Primaire" },
  { value: "college", label: "Collège" },
  { value: "lycee", label: "Lycée" },
  { value: "superieur", label: "Supérieur" },
];

const EXPERIENCE_OPTIONS = [
  { value: "regulier", label: "Oui, régulièrement" },
  { value: "occasionnel", label: "Oui, occasionnellement" },
  { value: "premiere_fois", label: "Non, ce sera ma première fois" },
];

const JOURS_OPTIONS = [
  { value: "lun", label: "Lundi" },
  { value: "mar", label: "Mardi" },
  { value: "mer", label: "Mercredi" },
  { value: "jeu", label: "Jeudi" },
  { value: "ven", label: "Vendredi" },
  { value: "sam", label: "Samedi" },
  { value: "dim", label: "Dimanche" },
];

const CRENEAUX_OPTIONS = [
  { value: "matin", label: "Matin (8h-12h)" },
  { value: "apres_midi", label: "Après-midi (12h-17h)" },
  { value: "soir", label: "Soir (17h-20h)" },
];

interface ChampsFormulaire {
  niveau_etudes: string;
  niveaux_enseignement: string[];
  experience_cours: string;
  jours_disponibles: string[];
  creneaux_preferes: string[];
  accepte_deplacement: boolean;
  cgu_acceptees: boolean;
}

export default function QuestionnaireEncadreur({
  onComplete,
}: {
  onComplete: () => void;
}) {
  const [champs, setChamps] = useState<ChampsFormulaire>({
    niveau_etudes: "",
    niveaux_enseignement: [],
    experience_cours: "",
    jours_disponibles: [],
    creneaux_preferes: [],
    accepte_deplacement: false,
    cgu_acceptees: false,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validations côté client
    if (!champs.niveau_etudes) {
      setError("Veuillez sélectionner votre niveau d'études");
      return;
    }
    if (champs.niveaux_enseignement.length === 0) {
      setError("Veuillez sélectionner au moins un niveau d'enseignement");
      return;
    }
    if (!champs.experience_cours) {
      setError("Veuillez préciser votre expérience en cours particuliers");
      return;
    }
    if (champs.jours_disponibles.length === 0) {
      setError("Veuillez sélectionner au moins un jour de disponibilité");
      return;
    }
    if (!champs.accepte_deplacement) {
      setError("Vous devez accepter de vous déplacer au domicile de l'élève");
      return;
    }
    if (!champs.cgu_acceptees) {
      setError("Vous devez accepter les conditions générales d'utilisation");
      return;
    }

    setSaving(true);
    try {
      const data: ProfilEncadreurUpdate = {
        niveau_etudes: champs.niveau_etudes,
        niveaux_enseignement: champs.niveaux_enseignement,
        experience_cours: champs.experience_cours,
        jours_disponibles: champs.jours_disponibles,
        creneaux_preferes: champs.creneaux_preferes,
        accepte_deplacement: champs.accepte_deplacement,
        cgu_acceptees: champs.cgu_acceptees,
      };
      await updateMonProfil(data);
      onComplete();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Erreur lors de l'enregistrement";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const toggleMultiSelect = (
    field: "niveaux_enseignement" | "jours_disponibles" | "creneaux_preferes",
    value: string,
  ) => {
    setChamps((prev) => {
      const current = prev[field];
      const next = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];
      return { ...prev, [field]: next };
    });
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-zinc-800">
          Questionnaire post-inscription
        </h1>
        <p className="text-zinc-500 mt-1 text-sm">
          Avant d&apos;accéder à votre profil, nous avons besoin de quelques
          informations complémentaires.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* 1. Niveau d'études */}
        <section>
          <label className="block text-sm font-medium text-zinc-700 mb-2">
            Niveau d&apos;études actuel <span className="text-red-500">*</span>
          </label>
          <select
            value={champs.niveau_etudes}
            onChange={(e) =>
              setChamps((prev) => ({ ...prev, niveau_etudes: e.target.value }))
            }
            className="w-full border border-zinc-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-white"
          >
            <option value="">Sélectionnez votre niveau</option>
            {NIVEAU_ETUDES_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </section>

        {/* 2. Niveaux d'enseignement */}
        <section>
          <span className="block text-sm font-medium text-zinc-700 mb-2">
            Niveaux acceptés pour enseigner{" "}
            <span className="text-red-500">*</span>
          </span>
          <div className="flex flex-wrap gap-2">
            {NIVEAUX_ENSEIGNEMENT_OPTIONS.map((opt) => {
              const estSelectionne = champs.niveaux_enseignement.includes(
                opt.value,
              );
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() =>
                    toggleMultiSelect("niveaux_enseignement", opt.value)
                  }
                  className={`px-4 py-2 rounded-full text-sm border transition ${
                    estSelectionne
                      ? "bg-orange-500 text-white border-orange-500"
                      : "bg-white text-zinc-700 border-zinc-300 hover:border-orange-400"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* 3. Expérience cours particuliers */}
        <section>
          <span className="block text-sm font-medium text-zinc-700 mb-2">
            Expérience en cours particuliers{" "}
            <span className="text-red-500">*</span>
          </span>
          <div className="space-y-2">
            {EXPERIENCE_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition ${
                  champs.experience_cours === opt.value
                    ? "border-orange-500 bg-orange-50"
                    : "border-zinc-200 bg-white hover:border-orange-300"
                }`}
              >
                <input
                  type="radio"
                  name="experience_cours"
                  value={opt.value}
                  checked={champs.experience_cours === opt.value}
                  onChange={(e) =>
                    setChamps((prev) => ({
                      ...prev,
                      experience_cours: e.target.value,
                    }))
                  }
                  className="h-4 w-4 text-orange-500 focus:ring-orange-500"
                />
                <span className="text-sm text-zinc-700">{opt.label}</span>
              </label>
            ))}
          </div>
        </section>

        {/* 4. Jours disponibles */}
        <section>
          <span className="block text-sm font-medium text-zinc-700 mb-2">
            Jours disponibles <span className="text-red-500">*</span>
          </span>
          <div className="flex flex-wrap gap-2">
            {JOURS_OPTIONS.map((opt) => {
              const estSelectionne = champs.jours_disponibles.includes(
                opt.value,
              );
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() =>
                    toggleMultiSelect("jours_disponibles", opt.value)
                  }
                  className={`px-4 py-2 rounded-full text-sm border transition ${
                    estSelectionne
                      ? "bg-orange-500 text-white border-orange-500"
                      : "bg-white text-zinc-700 border-zinc-300 hover:border-orange-400"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* 5. Créneaux préférés */}
        <section>
          <span className="block text-sm font-medium text-zinc-700 mb-2">
            Créneaux préférés{" "}
            <span className="text-zinc-400 text-xs">(optionnel)</span>
          </span>
          <div className="flex flex-wrap gap-2">
            {CRENEAUX_OPTIONS.map((opt) => {
              const estSelectionne = champs.creneaux_preferes.includes(
                opt.value,
              );
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() =>
                    toggleMultiSelect("creneaux_preferes", opt.value)
                  }
                  className={`px-4 py-2 rounded-full text-sm border transition ${
                    estSelectionne
                      ? "bg-orange-500 text-white border-orange-500"
                      : "bg-white text-zinc-700 border-zinc-300 hover:border-orange-400"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* 6. Déplacement au domicile */}
        <section className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm text-amber-800 mb-3">
            En tant qu&apos;encadreur MYCD, vous serez amené à vous déplacer au
            domicile de l&apos;élève pour dispenser les cours. Cette
            modalité fait partie intégrante de notre service.
          </p>
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={champs.accepte_deplacement}
              onChange={(e) =>
                setChamps((prev) => ({
                  ...prev,
                  accepte_deplacement: e.target.checked,
                }))
              }
              className="mt-0.5 h-4 w-4 text-orange-500 focus:ring-orange-500 rounded"
            />
            <span className="text-sm text-zinc-700">
              J&apos;accepte de me déplacer au domicile de l&apos;élève{" "}
              <span className="text-red-500">*</span>
            </span>
          </label>
        </section>

        {/* 7. CGU */}
        <section className="bg-zinc-50 border border-zinc-200 rounded-xl p-4">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={champs.cgu_acceptees}
              onChange={(e) =>
                setChamps((prev) => ({
                  ...prev,
                  cgu_acceptees: e.target.checked,
                }))
              }
              className="mt-0.5 h-4 w-4 text-orange-500 focus:ring-orange-500 rounded"
            />
            <span className="text-sm text-zinc-700">
              J&apos;accepte les conditions générales d&apos;utilisation et la
              charte de confidentialité{" "}
              <span className="text-red-500">*</span>
            </span>
          </label>
        </section>

        {/* 8. Bouton Enregistrer */}
        <button
          type="submit"
          disabled={saving}
          className="w-full bg-orange-500 text-white py-3 rounded-lg font-medium hover:bg-orange-600 transition disabled:opacity-50 disabled:cursor-not-allowed text-base"
        >
          {saving ? "Enregistrement en cours..." : "Enregistrer"}
        </button>
      </form>
    </div>
  );
}
