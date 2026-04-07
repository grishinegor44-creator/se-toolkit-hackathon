import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Star, Wine, GlassWater } from "lucide-react";
import type { Cocktail } from "@shared/schema";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addFavorite, removeFavorite, getFavorites } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface CocktailDetailProps {
  cocktail: Cocktail | null;
  open: boolean;
  onClose: () => void;
}

export default function CocktailDetail({
  cocktail,
  open,
  onClose,
}: CocktailDetailProps) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: favorites = [] } = useQuery({
    queryKey: ["/favorites"],
    queryFn: getFavorites,
  });

  const isFavorite = cocktail
    ? favorites.some((f) => f.cocktail_id === cocktail.id)
    : false;

  const addMutation = useMutation({
    mutationFn: () => addFavorite(cocktail!.id, cocktail!.name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/favorites"] });
      toast({ title: "Added to favorites", description: cocktail!.name });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Could not add to favorites",
        variant: "destructive",
      });
    },
  });

  const removeMutation = useMutation({
    mutationFn: () => removeFavorite(cocktail!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/favorites"] });
      toast({ title: "Removed from favorites", description: cocktail!.name });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Could not remove from favorites",
        variant: "destructive",
      });
    },
  });

  if (!cocktail) return null;

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-lg p-0 flex flex-col"
        data-testid="sheet-cocktail-detail"
      >
        <SheetHeader className="sr-only">
          <SheetTitle>{cocktail.name}</SheetTitle>
          <SheetDescription>Cocktail details</SheetDescription>
        </SheetHeader>

        <ScrollArea className="flex-1">
          {/* Image */}
          <div className="aspect-[4/3] bg-muted relative overflow-hidden">
            {cocktail.thumbnail ? (
              <img
                src={cocktail.thumbnail}
                alt={cocktail.name}
                className="w-full h-full object-cover"
                data-testid="img-cocktail-detail"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Wine className="w-16 h-16 text-muted-foreground/30" />
              </div>
            )}
          </div>

          <div className="p-5 space-y-5">
            {/* Title + badges */}
            <div>
              <h2
                className="text-xl font-bold text-foreground"
                data-testid="text-detail-name"
              >
                {cocktail.name}
              </h2>
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <Badge variant="secondary">{cocktail.category}</Badge>
                <Badge
                  variant={
                    cocktail.alcoholic === "Alcoholic" ? "default" : "outline"
                  }
                >
                  {cocktail.alcoholic}
                </Badge>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <GlassWater className="w-3 h-3" />
                  <span>{cocktail.glass}</span>
                </div>
              </div>
            </div>

            {/* Ingredients */}
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2">
                Ingredients
              </h3>
              <ul className="space-y-1.5" data-testid="list-ingredients">
                {cocktail.ingredients.map((ing, i) => (
                  <li
                    key={i}
                    className="flex items-center justify-between text-sm py-1.5 px-3 rounded-lg bg-muted/50"
                  >
                    <span className="text-foreground">{ing.ingredient}</span>
                    {ing.measure && (
                      <span className="text-muted-foreground text-xs">
                        {ing.measure}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>

            {/* Instructions */}
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2">
                Instructions
              </h3>
              <p
                className="text-sm text-muted-foreground leading-relaxed"
                data-testid="text-instructions"
              >
                {cocktail.instructions}
              </p>
            </div>

            {/* Favorite button */}
            <Button
              onClick={() =>
                isFavorite ? removeMutation.mutate() : addMutation.mutate()
              }
              variant={isFavorite ? "secondary" : "default"}
              className="w-full"
              disabled={addMutation.isPending || removeMutation.isPending}
              data-testid="button-favorite-toggle"
            >
              <Star
                className={`w-4 h-4 mr-2 ${isFavorite ? "fill-current" : ""}`}
              />
              {isFavorite ? "Saved" : "Add to Favorites"}
            </Button>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
