"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getNotifications, markAllNotificationsRead, markNotificationRead, Notification } from "@/lib/api";

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const ref = useRef<HTMLDivElement>(null);

  const nonLus = notifications.filter((n) => !n.is_read).length;

  const fetchNotifs = async () => {
    try {
      setNotifications(await getNotifications());
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchNotifs();
    let interval = setInterval(fetchNotifs, 15000);

    const handleVisibility = () => {
      if (document.hidden) {
        clearInterval(interval);
      } else {
        fetchNotifs();
        interval = setInterval(fetchNotifs, 15000);
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleClick = async (n: Notification) => {
    if (!n.is_read) {
      try { await markNotificationRead(n.id); } catch { /* ignore */ }
      setNotifications((prev) =>
        prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x))
      );
    }
    setOpen(false);
    if (n.link) router.push(n.link);
  };

  const handleReadAll = async () => {
    try { await markAllNotificationsRead(); } catch { /* ignore */ }
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-1.5 rounded-lg hover:bg-zinc-100 transition"
        aria-label="Notifications"
      >
        <svg className="w-5 h-5 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {nonLus > 0 && (
          <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
            {nonLus > 9 ? "9+" : nonLus}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-semibold text-gray-800">Notifications</span>
            {nonLus > 0 && (
              <button onClick={handleReadAll} className="text-xs text-orange-500 hover:underline">
                Tout marquer lu
              </button>
            )}
          </div>
          <div className="max-h-72 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-center text-gray-400 text-sm py-6">Aucune notification</p>
            ) : (
              notifications.slice(0, 10).map((n) => (
                <button
                  key={n.id}
                  onClick={() => handleClick(n)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition border-b border-gray-50 last:border-0 ${
                    !n.is_read ? "bg-orange-50/50" : ""
                  }`}
                >
                  <p className={`text-sm ${!n.is_read ? "font-semibold text-gray-800" : "text-gray-600"}`}>
                    {n.title}
                  </p>
                  {n.message && (
                    <p className="text-xs text-gray-400 mt-0.5 truncate">{n.message}</p>
                  )}
                  <p className="text-[10px] text-gray-300 mt-1">
                    {new Date(n.created_at).toLocaleDateString("fr-FR", {
                      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
                    })}
                  </p>
                </button>
              ))
            )}
          </div>
          <Link
            href="/notifications"
            onClick={() => setOpen(false)}
            className="block text-center text-sm text-orange-500 py-3 border-t border-gray-100 hover:bg-gray-50 rounded-b-xl"
          >
            Voir toutes les notifications
          </Link>
        </div>
      )}
    </div>
  );
}
