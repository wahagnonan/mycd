"use client";

import { use, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getMessages, sendMessage, markAsRead, Message } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function ConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
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
      const interval = setInterval(fetchMessages, 5000);
      return () => clearInterval(interval);
    } else if (!isLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [id, isAuthenticated, isLoading]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    setSending(true);
    try {
      await sendMessage(Number(id), input.trim());
      setInput("");
      const data = await getMessages(Number(id));
      setMessages(data);
    } catch {
      // ignore
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
                }`}
              >
                <p>{m.content}</p>
                <p className={`text-xs mt-1 ${m.sender === user?.id ? "text-orange-100" : "text-gray-400"}`}>
                  {new Date(m.created_at).toLocaleTimeString("fr-FR", {
                    hour: "2-digit", minute: "2-digit",
                  })}
                </p>
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
