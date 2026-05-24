"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Conversation, getConversations } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function MessageriePage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      getConversations()
        .then(setConversations)
        .catch(() => {})
        .finally(() => setLoading(false));
    } else if (!isLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [isAuthenticated, isLoading]);

  if (isLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500">Connectez-vous pour accéder à vos messages.</p>
        <Link href="/login" className="text-orange-500 hover:underline mt-2 inline-block">Connexion</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Mes conversations</h1>

      {conversations.length === 0 ? (
        <p className="text-gray-500 text-center py-12">Aucune conversation pour le moment.</p>
      ) : (
        <div className="space-y-2">
          {conversations.map((c) => (
              <Link
                key={c.id}
                href={`/messagerie/${c.id}`}
                className="block border border-gray-200 rounded-xl p-4 transition hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-800 truncate">{c.correspondant_nom}</h3>
                      {c.nb_non_lus > 0 && (
                      <span className="bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">
                        {c.nb_non_lus}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{c.correspondant_email}</p>
                  {c.dernier_message && (
                    <p className="text-sm text-gray-600 mt-1 truncate">
                      {c.dernier_message.est_moi ? "Vous : " : ""}
                      {c.dernier_message.content}
                    </p>
                  )}
                </div>
                <span className="text-xs text-gray-400 ml-4">
                  {new Date(c.updated_at).toLocaleDateString("fr-FR", {
                    day: "numeric", month: "short",
                  })}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
