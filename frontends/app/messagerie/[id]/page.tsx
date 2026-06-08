"use client";

import { use, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getMessages, sendMessage, markAsRead, Message } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

type MessageAvecStatut = Message & { statut?: "envoye" | "envoi" | "erreur" };

export default function ConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();
  const [messages, setMessages] = useState<MessageAvecStatut[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchMessages = async () => {
    try {
      const data = await getMessages(Number(id));
      setMessages(data);
      await markAsRead(Number(id));
    } catch {
      router.push("/messagerie");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      fetchMessages();
      let interval = setInterval(fetchMessages, 5000);

      const handleVisibility = () => {
        if (document.hidden) {
          clearInterval(interval);
        } else {
          fetchMessages();
          interval = setInterval(fetchMessages, 5000);
        }
      };

      document.addEventListener("visibilitychange", handleVisibility);

      return () => {
        clearInterval(interval);
        document.removeEventListener("visibilitychange", handleVisibility);
      };
    } else if (!isLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [id, isAuthenticated, isLoading]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    const content = input.trim();
    setInput("");
    setSending(true);

    const tempId = -Date.now();
    const tempMsg: MessageAvecStatut = {
      id: tempId, sender: user!.id, sender_email: user!.email,
      sender_nom: user!.email, content, created_at: new Date().toISOString(),
      is_read: false, statut: "envoi",
    };

    setMessages((prev) => [...prev, tempMsg]);

    try {
      const sent = await sendMessage(Number(id), content);
      setMessages((prev) =>
        prev.map((m) => (m.id === tempId ? { ...m, ...sent, statut: "envoye" as const } : m))
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempId ? { ...m, statut: "erreur" as const } : m
        )
      );
    } finally {
      setSending(false);
    }
  };

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
      <Link href="/messagerie" className="text-orange-500 hover:underline text-sm inline-flex items-center gap-1">
        &larr; Retour aux conversations
      </Link>

      <div className="mt-4 border border-gray-200 rounded-xl overflow-hidden flex flex-col h-[65vh]">
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
          {messages.length === 0 && (
            <p className="text-center text-gray-400 py-8">Aucun message. Envoyez le premier message !</p>
          )}
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex ${m.sender === user?.id ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] rounded-xl px-4 py-2 text-sm ${
                  m.sender === user?.id
                    ? "bg-orange-500 text-white rounded-br-sm"
                    : "bg-white border border-gray-200 rounded-bl-sm"
                } ${m.statut === "envoi" ? "opacity-60" : ""}`}
              >
                <p>{m.content}</p>
                <div className={`flex items-center gap-1 mt-1 ${m.sender === user?.id ? "text-orange-100" : "text-gray-400"}`}>
                  <span className="text-xs">
                    {new Date(m.created_at).toLocaleTimeString("fr-FR", {
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </span>
                  {m.sender === user?.id && m.statut !== "erreur" && (
                    m.statut === "envoi" ? (
                      <svg className="w-3.5 h-3.5 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                      </svg>
                    ) : m.is_read ? (
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M18 4l-8 8-3-3" stroke="currentColor" strokeWidth="2" fill="none" />
                        <path d="M14 4l-8 8-3-3" stroke="currentColor" strokeWidth="2" fill="none" transform="translate(2, 0)" />
                      </svg>
                    ) : (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 20 20">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )
                  )}
                  {m.statut === "erreur" && (
                    <svg className="w-3 h-3 text-red-300" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 18a8 8 0 100-16 8 8 0 000-16zM11 5a1 1 0 10-2 0v6a1 1 0 102 0V5zm-1 9a1 1 0 100 2 1 1 0 000-2z" clipRule="evenodd" fillRule="evenodd" />
                    </svg>
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-gray-200 p-3 bg-white flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Écrivez un message..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition text-sm font-medium disabled:opacity-50"
          >
            {sending ? "..." : "Envoyer"}
          </button>
        </div>
      </div>
    </div>
  );
}
