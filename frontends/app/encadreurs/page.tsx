"use client";

import { useCallback, useEffect, useState } from "react";
import { getEncadreurs, Matiere, getMatieres, ProfilEncadreur } from "@/lib/api";
import Link from "next/link";

const COMMUNES = [
  "Abengourou", "Abobo", "Aboisso", "Adiaké", "Adjamé", "Adzopé",
  "Agboville", "Anyama", "Attécoubé", "Bingerville", "Bondoukou",
  "Bongouanou", "Bouaflé", "Bouaké", "Boundiali", "Cocody",
  "Dabou", "Daloa", "Daoukro", "Dimbokro", "Divo", "Duékoué",
  "Ferkessédougou", "Gagnoa", "Grand-Bassam", "Guiglo", "Issia",
  "Jacqueville", "Katiola", "Korhogo", "Koumassi", "Lakota",
  "Man", "Mankono", "Marcory", "Odienné", "Oumé", "Plateau",
  "Port-Bouët", "San-Pédro", "Sassandra", "Séguéla", "Sinfra",
  "Soubré", "Tiassalé", "Touba", "Toumodi", "Treichville",
  "Vavoua", "Yamoussoukro", "Yopougon", "Zuénoula",
];

const SUGGESTIONS = [
  { label: "Maths à Cocody", ville: "Cocody" },
  { label: "Français à Yopougon", ville: "Yopougon" },
  { label: "Anglais à Abidjan", ville: "Abidjan" },
];

export default function EncadreursPage() {
  const [encadreurs, setEncadreurs] = useState<ProfilEncadreur[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [matieres, setMatieres] = useState<Matiere[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [ville, setVille] = useState("");
  const [matiereFilter, setMatiereFilter] = useState("");
  const [activeVille, setActiveVille] = useState("");
  const [activeMatiere, setActiveMatiere] = useState("");

  useEffect(() => {
    getMatieres().then(setMatieres).catch(() => {});
  }, []);

  const lancerRecherche = () => {
    setActiveVille(ville);
    setActiveMatiere(matiereFilter);
    setPage(1);
  };

  const effacer = () => {
    setVille("");
    setMatiereFilter("");
    setActiveVille("");
    setActiveMatiere("");
    setPage(1);
  };

  const suggerer = (s: typeof SUGGESTIONS[number]) => {
    setVille(s.ville);
    setMatiereFilter("");
    setActiveVille(s.ville);
    setActiveMatiere("");
    setPage(1);
  };

  const fetchEncadreurs = useCallback(
    async (currentPage: number) => {
      setLoading(true);
      setError("");
      try {
        const data = await getEncadreurs({
          ville: activeVille || undefined,
          matiere: activeMatiere || undefined,
          page: currentPage,
        });
        setEncadreurs(data.results);
        setTotal(data.count);
        setHasMore(!!data.next);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Erreur de chargement");
      } finally {
        setLoading(false);
      }
    },
    [activeVille, activeMatiere],
  );

  useEffect(() => {
    fetchEncadreurs(page);
  }, [page, fetchEncadreurs]);

  const aUnFiltre = activeVille || activeMatiere;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Trouver un encadreur</h1>

      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
        <div className="flex flex-wrap items-end gap-3">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-gray-500 mb-1">Matière</label>
            <select
              value={matiereFilter}
              onChange={(e) => setMatiereFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">Toutes les matières</option>
              {matieres.map((m) => (
                <option key={m.id} value={m.id}>{m.nom}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-gray-500 mb-1">Commune</label>
            <select
              value={ville}
              onChange={(e) => setVille(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">Toutes les communes</option>
              {COMMUNES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <button
            onClick={lancerRecherche}
            className="bg-orange-500 text-white px-5 py-2 rounded-lg hover:bg-orange-600 transition text-sm font-medium"
          >
            Rechercher
          </button>
          {aUnFiltre && (
            <button
              onClick={effacer}
              className="px-4 py-2 text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Effacer
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-400">Suggestions :</span>
          {SUGGESTIONS.map((s) => (
            <button
              key={s.label}
              onClick={() => suggerer(s)}
              className="text-xs bg-orange-50 text-orange-700 px-3 py-1 rounded-full hover:bg-orange-100 transition"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-500 mb-2">{error}</p>
          <button
            onClick={() => fetchEncadreurs(page)}
            className="text-orange-500 hover:underline text-sm"
          >
            Réessayer
          </button>
        </div>
      ) : encadreurs.length === 0 ? (
        <p className="text-center text-gray-500 py-12">
          Aucun encadreur trouvé
        </p>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">{total} encadreur(s) trouvé(s)</p>
          <div className="grid gap-4 md:grid-cols-2">
            {encadreurs.map((e) => (
              <Link
                key={e.id}
                href={`/encadreurs/${e.id}`}
                className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{e.nom}</h3>
                    <p className="text-sm text-gray-500">
                      {e.email} &middot; {e.phone}
                    </p>
                  </div>
                  {e.verified && (
                    <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                      Vérifié
                    </span>
                  )}
                </div>
                {e.bio && (
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">{e.bio}</p>
                )}
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {e.matieres.map((m) => (
                    <span
                      key={m.id}
                      className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded-full"
                    >
                      {m.nom}
                    </span>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-3 text-sm text-gray-500">
                  <span>
                    {e.tarif_mois
                      ? `${e.tarif_mois.toLocaleString()} FCFA/mois`
                      : e.tarif_horaire
                        ? `${e.tarif_horaire.toLocaleString()} FCFA/h`
                        : "Tarif non défini"}
                  </span>
                  <span>{e.note_moyenne > 0 ? `★ ${e.note_moyenne.toFixed(1)}` : ""}</span>
                </div>
              </Link>
            ))}
          </div>
          {hasMore && (
            <div className="flex justify-center mt-6">
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={loading}
                className="bg-orange-500 text-white px-6 py-2 rounded-lg hover:bg-orange-600 transition disabled:opacity-50"
              >
                {loading ? "Chargement..." : "Voir plus"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
