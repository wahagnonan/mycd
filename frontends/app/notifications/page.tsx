"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getNotifications, markAllNotificationsRead, markNotificationRead, Notification } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const fetchNotifs = async () => {
    try {
      setNotifications(await getNotifications());
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (!isLoading && isAuthenticated) fetchNotifs();
    else if (!isLoading) setLoading(false);
  }, [isAuthenticated, isLoading]);

  const handleClick = async (n: Notification) => {
    if (!n.is_read) {
      try { await markNotificationRead(n.id); } catch { /* ignore */ }
      setNotifications((prev) =>
        prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x))
      );
    }
    if (n.link) router.push(n.link);
  };

  const handleReadAll = async () => {
    try { await markAllNotificationsRead(); } catch { /* ignore */ }
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const nonLus = notifications.filter((n) => !n.is_read).length;

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
        <p className="text-gray-500">Connectez-vous pour voir vos notifications.</p>
        <Link href="/login" className="text-orange-500 hover:underline mt-2 inline-block">Connexion</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Notifications</h1>
        {nonLus > 0 && (
          <button
            onClick={handleReadAll}
            className="text-sm text-orange-500 hover:underline font-medium"
          >
            Tout marquer comme lu ({nonLus})
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <p className="text-center text-gray-400 py-12">Aucune notification</p>
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => handleClick(n)}
              className={`w-full text-left border border-gray-200 rounded-xl p-4 hover:shadow-sm transition ${
                !n.is_read ? "bg-orange-50 border-orange-200" : "bg-white"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className={`text-sm ${!n.is_read ? "font-semibold text-gray-800" : "text-gray-600"}`}>
                      {n.title}
                    </p>
                    {!n.is_read && (
                      <span className="w-2 h-2 rounded-full bg-orange-500 flex-shrink-0" />
                    )}
                  </div>
                  {n.message && (
                    <p className="text-sm text-gray-400 mt-1">{n.message}</p>
                  )}
                  <p className="text-xs text-gray-300 mt-2">
                    {new Date(n.created_at).toLocaleDateString("fr-FR", {
                      day: "numeric", month: "long", year: "numeric",
                      hour: "2-digit", minute: "2-digit",
                    })}
                  </p>
                </div>
                {n.type === "new_message" && (
                  <svg className="w-5 h-5 text-orange-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
