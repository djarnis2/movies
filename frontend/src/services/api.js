// services/api.js
const API_BASE =
  import.meta.env.VITE_MOVIES_API || "http://localhost:8000";

/* Henter ALLE film fra dit FastAPI-backend */
export async function getMyMovies() {
  const res = await fetch(`${API_BASE}/movies`);
  if (!res.ok) throw new Error("Backend unreachable");
  return await res.json();               // [{ id, title, … }]
}

/* Lokal søgning i et allerede hentet array */
export function searchMovies(list, term) {
  if (!term.trim()) return list;         // tom søgning → vis alt
  const t = term.toLowerCase();
  return list.filter((m) =>
    m.title.toLowerCase().includes(t)
  );
}

/* ───────── seen-funktioner ───────── */
export async function getSeenIds() {
  const res = await fetch(`${API_BASE}/seen`);
  return await res.json();          // [123, 456, …]
}

export async function addSeen(id) {
  await fetch(`${API_BASE}/seen/${id}`, { method: "POST" });
}

export async function removeSeen(id) {
  await fetch(`${API_BASE}/seen/${id}`, { method: "DELETE" });
}

