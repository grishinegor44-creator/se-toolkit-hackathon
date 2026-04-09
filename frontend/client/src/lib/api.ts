import type { Cocktail, HistoryEntry, Favorite } from "@shared/schema";

const API_BASE = "http://localhost:8000";

// Get authenticated user ID
const getUserId = (): number | null => {
  const userStr = localStorage.getItem("user");
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      return user.id;
    } catch {
      return null;
    }
  }
  return null;
};

// Fallback to anonymous user ID if not authenticated
const getUid = (): string => {
  const userId = getUserId();
  if (userId !== null) {
    return String(userId);
  }
  
  // Fallback to anonymous ID
  let uid = localStorage.getItem("cbuid");
  if (!uid) {
    uid = String(Math.floor(Math.random() * 1e9));
    localStorage.setItem("cbuid", uid);
  }
  return uid;
};

export const uid = getUid();

// Helper to refresh UID before each API call
export const refreshUid = () => {
  return getUid();
};

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
    `/cocktails/by-name?name=${encodeURIComponent(name)}&user_id=${refreshUid()}`
  );
}

// Search cocktails by ingredients
export async function searchByIngredients(
  ingredients: string
): Promise<Cocktail[]> {
  return apiFetch<Cocktail[]>(
    `/cocktails/by-ingredients?ingredients=${encodeURIComponent(ingredients)}&user_id=${refreshUid()}`
  );
}

// Get a random cocktail
export async function getRandomCocktail(): Promise<Cocktail> {
  return apiFetch<Cocktail>(`/cocktails/random?user_id=${refreshUid()}`);
}

// Get user history
export async function getHistory(limit = 20): Promise<HistoryEntry[]> {
  return apiFetch<HistoryEntry[]>(
    `/history?user_id=${refreshUid()}&limit=${limit}`
  );
}

// Get favorites
export async function getFavorites(): Promise<Favorite[]> {
  return apiFetch<Favorite[]>(`/favorites?user_id=${refreshUid()}`);
}

// Add favorite
export async function addFavorite(
  cocktailId: string,
  cocktailName: string
): Promise<Favorite> {
  return apiFetch<Favorite>("/favorites", {
    method: "POST",
    body: JSON.stringify({
      telegram_user_id: Number(refreshUid()),
      cocktail_id: cocktailId,
      cocktail_name: cocktailName,
    }),
  });
}

// Remove favorite
export async function removeFavorite(cocktailId: string): Promise<void> {
  await fetch(`${API_BASE}/favorites/${cocktailId}?user_id=${refreshUid()}`, {
    method: "DELETE",
  });
}
