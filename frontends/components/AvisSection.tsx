"use client";

import { useEffect, useState } from "react";
import { getAvis, createAvis, Avis } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import RatingStars from "./RatingStars";

export default function AvisSection({ encadreurId }: { encadreurId: number }) {
  const { user, isAuthenticated } = useAuth();
  const [avisList, setAvisList] = useState<Avis[]>([]);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState(0);
  const [commentaire, setCommentaire] = useState("");
  const [sending, setSending] = useState(false);
  const [hover, setHover] = useState(0);

  const fetchAvis = async () => {
    try {
      setAvisList(await getAvis(encadreurId));
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAvis(); }, [encadreurId]);

  const monAvis = avisList.find((a) => a.parent === user?.id);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (note === 0) return;
    setSending(true);
    try {
      const avis = await createAvis(encadreurId, { note, commentaire: commentaire || undefined });
      setAvisList((prev) => [avis, ...prev]);
      setNote(0);
      setCommentaire("");
    } catch {
      // ignore
    } finally {
      setSending(false);
    }
  };

  const StarInput = ({ value }: { value: number }) => (
    <button
      type="button"
      onClick={() => setNote(value)}
      onMouseEnter={() => setHover(value)}
      onMouseLeave={() => setHover(0)}
      className="p-0.5"
    >
      <svg className={`w-6 h-6 ${value <= (hover || note) ? "text-amber-400" : "text-gray-200"} transition-colors`} fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    </button>
  );

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold text-zinc-900 mb-4">Avis</h3>

      {isAuthenticated && user?.role === "parent" && !monAvis && (
        <form onSubmit={handleSubmit} className="bg-white border border-zinc-200 rounded-xl p-4 mb-6">
          <label className="block text-sm font-medium text-zinc-700 mb-2">Votre note</label>
          <div className="flex mb-3">
            {[1, 2, 3, 4, 5].map((i) => <StarInput key={i} value={i} />)}
          </div>
          <textarea
            value={commentaire}
            onChange={(e) => setCommentaire(e.target.value)}
            placeholder="Votre commentaire (optionnel)..."
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 mb-3"
            rows={3}
          />
          <button
            type="submit"
            disabled={note === 0 || sending}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 transition disabled:opacity-50"
          >
            {sending ? "..." : "Publier l'avis"}
          </button>
        </form>
      )}

      {isAuthenticated && monAvis && (
        <p className="text-sm text-zinc-500 mb-4">
          Vous avez déjà laissé un avis. <RatingStars note={monAvis.note} /> &mdash; {monAvis.commentaire}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-zinc-400">Chargement...</p>
      ) : avisList.length === 0 ? (
        <p className="text-sm text-zinc-400">Aucun avis pour le moment.</p>
      ) : (
        <div className="space-y-3">
          {avisList.map((a) => (
            <div key={a.id} className="bg-white border border-zinc-200 rounded-xl px-4 py-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium text-zinc-800">{a.parent_nom}</span>
                <RatingStars note={a.note} />
              </div>
              {a.commentaire && <p className="text-sm text-zinc-600">{a.commentaire}</p>}
              <p className="text-xs text-zinc-400 mt-1">
                {new Date(a.created_at).toLocaleDateString("fr-FR", {
                  day: "numeric", month: "long", year: "numeric",
                })}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
