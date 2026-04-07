import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Star, Wine } from "lucide-react";
import { getFavorites, searchByName } from "@/lib/api";
import CocktailCard, {
  CocktailCardSkeleton,
} from "@/components/cocktail-card";
import CocktailDetail from "@/components/cocktail-detail";
import type { Cocktail, Favorite } from "@shared/schema";

export default function FavoritesPage() {
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(
    null
  );
  const [detailOpen, setDetailOpen] = useState(false);

  const {
    data: favorites = [],
    isLoading,
    error,
  } = useQuery<Favorite[]>({
    queryKey: ["/favorites"],
    queryFn: getFavorites,
  });

  // For each favorite, we fetch the cocktail details for display
  // We'll use individual queries for each favorite cocktail
  const cocktailQueries = favorites.map((fav) => ({
    queryKey: ["/cocktail-detail", fav.cocktail_name],
    queryFn: () => searchByName(fav.cocktail_name),
    enabled: !!fav.cocktail_name,
  }));

  // Use a single query that fetches all favorite cocktails
  const { data: cocktailsData = [], isLoading: cocktailsLoading } = useQuery({
    queryKey: ["/favorites-cocktails", favorites.map((f) => f.cocktail_id).join(",")],
    queryFn: async () => {
      if (favorites.length === 0) return [];
      const results = await Promise.all(
        favorites.map(async (fav) => {
          try {
            const cocktails = await searchByName(fav.cocktail_name);
            return cocktails.find((c) => c.id === fav.cocktail_id) || cocktails[0] || null;
          } catch {
            return null;
          }
        })
      );
      return results.filter(Boolean) as Cocktail[];
    },
    enabled: favorites.length > 0,
  });

  const loading = isLoading || cocktailsLoading;

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
            <Star className="w-5 h-5 text-primary" />
            Favorites
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Your saved cocktails
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="text-center py-12 text-destructive text-sm" data-testid="text-error">
            Could not load favorites. Please try again.
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4" data-testid="loading-skeletons">
            {Array.from({ length: 4 }).map((_, i) => (
              <CocktailCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Grid */}
        {!loading && !error && cocktailsData.length > 0 && (
          <div
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
            data-testid="grid-favorites"
          >
            {cocktailsData.map((cocktail, i) => (
              <CocktailCard
                key={cocktail.id}
                cocktail={cocktail}
                index={i}
                onClick={() => {
                  setSelectedCocktail(cocktail);
                  setDetailOpen(true);
                }}
              />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && favorites.length === 0 && (
          <div className="text-center py-16 space-y-3" data-testid="empty-favorites">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center">
              <Wine className="w-8 h-8 text-primary" />
            </div>
            <p className="text-sm text-muted-foreground">
              Your bar is empty. Start searching!
            </p>
          </div>
        )}
      </div>

      {/* Detail sheet */}
      <CocktailDetail
        cocktail={selectedCocktail}
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
      />
    </div>
  );
}
