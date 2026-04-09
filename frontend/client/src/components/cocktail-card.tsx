import type { Cocktail } from "@shared/schema";
import { Badge } from "@/components/ui/badge";
import { Wine } from "lucide-react";

interface CocktailCardProps {
  cocktail: Cocktail;
  onClick: () => void;
  index?: number;
}

export default function CocktailCard({
  cocktail,
  onClick,
  index = 0,
}: CocktailCardProps) {
  return (
    <button
      onClick={onClick}
      className="group text-left rounded-xl border border-border bg-card overflow-hidden card-hover animate-fade-in focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      style={{ animationDelay: `${index * 50}ms` }}
      data-testid={`card-cocktail-${cocktail.id}`}
    >
      {/* Image */}
      <div className="aspect-square overflow-hidden bg-muted relative">
        {cocktail.thumbnail ? (
          <img
            src={cocktail.thumbnail}
            alt={cocktail.name}
            className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
              const placeholder = target.nextElementSibling;
              if (placeholder) {
                placeholder.classList.remove("hidden");
              }
            }}
          />
        ) : null}
        <div
          className={`absolute inset-0 flex items-center justify-center ${cocktail.thumbnail ? "" : ""}`}
        >
          <Wine className="w-10 h-10 text-muted-foreground/40" />
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <h3
          className="text-sm font-semibold text-foreground truncate"
          data-testid={`text-cocktail-name-${cocktail.id}`}
        >
          {cocktail.name}
        </h3>
        <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
          <Badge
            variant="secondary"
            className="text-[10px] px-1.5 py-0"
            data-testid={`badge-category-${cocktail.id}`}
          >
            {cocktail.category}
          </Badge>
          <Badge
            variant={
              cocktail.alcoholic === "Alcoholic" ? "default" : "outline"
            }
            className="text-[10px] px-1.5 py-0"
            data-testid={`badge-alcoholic-${cocktail.id}`}
          >
            {cocktail.alcoholic}
          </Badge>
        </div>
      </div>
    </button>
  );
}

export function CocktailCardSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="aspect-square skeleton-shimmer" />
      <div className="p-3 space-y-2">
        <div className="h-4 w-3/4 rounded skeleton-shimmer" />
        <div className="flex gap-1.5">
          <div className="h-4 w-16 rounded skeleton-shimmer" />
          <div className="h-4 w-14 rounded skeleton-shimmer" />
        </div>
      </div>
    </div>
  );
}
