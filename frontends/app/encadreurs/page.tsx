"use client";

import { useCallback, useEffect, useState } from "react";
import { getEncadreurs, Matiere, getMatieres, ProfilEncadreur } from "@/lib/api";
import Link from "next/link";

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

  useEffect(() => {
    getMatieres().then(setMatieres).catch(() => {});
  }, []);

  const fetchEncadreurs = useCallback(async (currentPage: number) => {
    setLoading(true);
    setError("");
    try {
      const data = await getEncadreurs({
        ville: ville || undefined,
        matiere: matiereFilter || undefined,
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
  }, [ville, matiereFilter]);

  useEffect(() => {
    setPage(1);
    fetchEncadreurs(1);
  }, [fetchEncadreurs]);

  useEffect(() => {
    fetchEncadreurs(page);
  }, [page, fetchEncadreurs]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Trouver un encadreur</h1>

      <div className="flex gap-4 mb-6">
        <input
          type="text"
          value={ville}
          onChange={(e) => setVille(e.target.value)}
          placeholder="Ville..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
        />
        <select
          value={matiereFilter}
          onChange={(e) => setMatiereFilter(e.target.value)}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value="">Toutes les matières</option>
          {matieres.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nom}
            </option>
          ))}
        </select>
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
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                    {e.bio}
                  </p>
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
