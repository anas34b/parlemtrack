"use client";

import { useEffect } from "react";

/** Enregistre le service worker (PWA installable, cache réseau-d'abord). */
export default function EnregistrerServiceWorker() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        // échec silencieux : le site reste fonctionnel sans le service worker
      });
    }
  }, []);
  return null;
}
