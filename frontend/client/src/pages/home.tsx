import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Dice5, Wine } from "lucide-react";
import CocktailCard, {
  CocktailCardSkeleton,
} from "@/components/cocktail-card";
import CocktailDetail from "@/components/cocktail-detail";
import type { Cocktail } from "@shared/schema";
import {
  searchByName,
  searchByIngredients,
  getRandomCocktail,
} from "@/lib/api";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState<"name" | "ingredients">("name");
  const [randomTrigger, setRandomTrigger] = useState(0);
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(
    null
  );
  const [detailOpen, setDetailOpen] = useState(false);

  const detectType = (q: string): "name" | "ingredients" => {
    return q.includes(",") ? "ingredients" : "name";
  };

  const handleSearch = useCallback(() => {
    if (!query.trim()) return;
    setRandomTrigger(0);
    const type = detectType(query);
    setSearchType(type);
    setSearchTerm(query.trim());
  }, [query]);

  const handleRandom = useCallback(() => {
    setSearchTerm("");
    setRandomTrigger((v) => v + 1);
  }, []);

  // Search query
  const {
    data: searchResults,
    isLoading: searchLoading,
    error: searchError,
  } = useQuery({
    queryKey: ["/search", searchType, searchTerm],
    queryFn: () =>
      searchType === "ingredients"
        ? searchByIngredients(searchTerm)
        : searchByName(searchTerm),
    enabled: !!searchTerm && randomTrigger === 0,
  });

  // Random query
  const {
    data: randomResult,
    isLoading: randomLoading,
    error: randomError,
  } = useQuery({
    queryKey: ["/random", randomTrigger],
    queryFn: getRandomCocktail,
    enabled: randomTrigger > 0,
    retry: 1,
    retryDelay: 3000,
    staleTime: 0,
    gcTime: 0,
  });

  const isLoading = searchLoading || randomLoading;
  const error = searchError || randomError;

  const results: Cocktail[] = randomTrigger > 0
    ? randomResult
      ? [randomResult]
      : []
    : searchResults || [];

  const hasSearched = !!searchTerm || randomTrigger > 0;

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-xl font-bold text-foreground">
            Find your drink
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Search by name or type comma-separated ingredients
          </p>
        </div>

        {/* Search bar */}
        <div className="flex flex-col sm:flex-row gap-2 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search cocktail or type ingredients..."
              className="pl-9 h-10"
              data-testid="input-search"
            />
          </div>
          <div className="flex gap-2">
            <Button
              onClick={handleSearch}
              disabled={!query.trim()}
              className="flex-1 sm:flex-none"
              data-testid="button-search"
            >
              Search
            </Button>
            <Button
              variant="outline"
              onClick={handleRandom}
              className="flex-1 sm:flex-none"
              data-testid="button-random"
            >
              <Dice5 className="w-4 h-4 mr-1.5" />
              Random
            </Button>
          </div>
        </div>

        {/* Error state */}
        {error && (
          <div
            className="text-center py-12 text-destructive text-sm"
            data-testid="text-error"
          >
            Something went wrong. Please try again.
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
            data-testid="loading-skeletons"
          >
            {Array.from({ length: 8 }).map((_, i) => (
              <CocktailCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Results grid */}
        {!isLoading && !error && results.length > 0 && (
          <div
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
            data-testid="grid-results"
          >
            {results.map((cocktail, i) => (
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
        {!isLoading && !error && hasSearched && results.length === 0 && (
          <div
            className="text-center py-16 space-y-3"
            data-testid="empty-search"
          >
            <Wine className="w-10 h-10 mx-auto text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              No cocktails found. Try a different search.
            </p>
          </div>
        )}

        {/* Initial state */}
        {!isLoading && !hasSearched && (
          <div className="text-center py-16 space-y-3" data-testid="initial-state">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center">
              <Wine className="w-8 h-8 text-primary" />
            </div>
            <p className="text-sm text-muted-foreground">
              Search for your favorite cocktail or try a random pick
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
