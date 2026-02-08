// services/api.js
const API_BASE =
  import.meta.env.VITE_MOVIES_API || "http://localhost:8000";
console.log("VITE_MOVIES_API =", import.meta.env.VITE_MOVIES_API);
console.log("API_BASE =", API_BASE);
  

/* Henter ALLE film fra dit FastAPI-backend */
export async function getMyMovies() {
  const res = await fetch(`${API_BASE}/movies`);
  if (!res.ok) throw new Error("Backend unreachable");
  return await res.json();               // [{ id, title, … }]
}

export async function getMovie(id) {
  const res = await fetch(`${API_BASE}/movies/${id}`);
  if (!res.ok) throw new Error("Backend unreachable");
  return await res.json();
}

/* Lokal søgning i et allerede hentet array */
export function searchMovies(list, term) {
  if (!term.trim()) return list;         // tom søgning → vis alt
  const t = term.trim().toLowerCase();
  return list.filter((m) => {
    const title = m.title.toLowerCase();
    const description = m.description.toLowerCase();
    return title.includes(t) || description.includes(t);
  });
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

/* ───────── import-funktioner ───────── */
export async function import_cast(movieLimit = 50, castLimit = 10) {
  const res = await fetch(`${API_BASE}/admin/import/cast?movieLimit=${movieLimit}&castLimit=${castLimit}`, {
    method: "POST",
  });
  return res.json();
}
export async function import_bio(bioLimit = 50) {
  const res = await fetch(`${API_BASE}/admin/import/bio?bioLimit=${bioLimit}`, {
    method: "POST",
  });
  return res.json();
}
export async function import_list(listId, limit = 0) {
  const qs = new URLSearchParams();
  if (listId !== undefined) qs.set("listId", String(listId));
  qs.set("limit", String(limit));

  const res = await fetch(`${API_BASE}/admin/import/list?${qs.toString()}`,{
    method: "POST",
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || "import list failed");
  }
  return data;
}
