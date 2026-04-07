// Cocktail API types — no database needed, purely frontend types

export interface Ingredient {
  ingredient: string;
  measure: string | null;
}

export interface Cocktail {
  id: string;
  name: string;
  category: string;
  alcoholic: string;
  glass: string;
  instructions: string;
  thumbnail: string;
  ingredients: Ingredient[];
}

export interface HistoryEntry {
  id?: number;
  user_id: number;
  query: string;
  query_type: string;
  result_count: number;
  timestamp?: string;
}

export interface Favorite {
  id?: number;
  telegram_user_id: number;
  cocktail_id: string;
  cocktail_name: string;
}
