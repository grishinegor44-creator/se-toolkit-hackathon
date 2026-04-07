import type { Cocktail, HistoryEntry, Favorite } from "@shared/schema";

const API_BASE = "http://localhost:8000";

// Simple user ID stored in localStorage
const getUid = (): string => {
  let uid = localStorage.getItem("cbuid");
  if (!uid) {
    uid = String(Math.floor(Math.random() * 1e9));
    localStorage.setItem("cbuid", uid);
  }
  return uid;
};

export const uid = getUid();

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

// Search cocktails by name
export async function searchByName(name: string): Promise<Cocktail[]> {
  return apiFetch<Cocktail[]>(
    `/cocktails/by-name?name=${encodeURIComponent(name)}&user_id=${uid}`
  );
}

// Search cocktails by ingredients
export async function searchByIngredients(
  ingredients: string
): Promise<Cocktail[]> {
  return apiFetch<Cocktail[]>(
    `/cocktails/by-ingredients?ingredients=${encodeURIComponent(ingredients)}&user_id=${uid}`
  );
}

// Get a random cocktail
export async function getRandomCocktail(): Promise<Cocktail> {
  return apiFetch<Cocktail>(`/cocktails/random?user_id=${uid}`);
}

// Get user history
export async function getHistory(limit = 20): Promise<HistoryEntry[]> {
  return apiFetch<HistoryEntry[]>(
    `/history?user_id=${uid}&limit=${limit}`
  );
}

// Get favorites
export async function getFavorites(): Promise<Favorite[]> {
  return apiFetch<Favorite[]>(`/favorites?user_id=${uid}`);
}

// Add favorite
export async function addFavorite(
  cocktailId: string,
  cocktailName: string
): Promise<Favorite> {
  return apiFetch<Favorite>("/favorites", {
    method: "POST",
    body: JSON.stringify({
      telegram_user_id: Number(uid),
      cocktail_id: cocktailId,
      cocktail_name: cocktailName,
    }),
  });
}

// Remove favorite
export async function removeFavorite(cocktailId: string): Promise<void> {
  await fetch(`${API_BASE}/favorites/${cocktailId}?user_id=${uid}`, {
    method: "DELETE",
  });
}
