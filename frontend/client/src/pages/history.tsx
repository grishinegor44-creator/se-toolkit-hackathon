import { useQuery } from "@tanstack/react-query";
import { Clock, Search, FlaskConical } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getHistory } from "@/lib/api";
import AuthGuard from "@/components/auth-guard";
import type { HistoryEntry } from "@shared/schema";

export default function HistoryPage() {
  const {
    data: history = [],
    isLoading,
    error,
  } = useQuery<HistoryEntry[]>({
    queryKey: ["/history"],
    queryFn: () => getHistory(20),
  });

  return (
    <AuthGuard>
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              History
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Your recent searches
            </p>
          </div>

          {/* Error */}
          {error && (
            <div
              className="text-center py-12 text-destructive text-sm"
              data-testid="text-error"
            >
              Could not load history. Please try again.
            </div>
          )}

          {/* Loading */}
          {isLoading && (
            <div className="space-y-3" data-testid="loading-skeletons">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 rounded-lg border border-border"
                >
                  <Skeleton className="w-8 h-8 rounded-lg shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* History list */}
          {!isLoading && !error && history.length > 0 && (
            <div className="space-y-2" data-testid="list-history">
              {history.map((entry, i) => (
                <div
                  key={entry.id ?? i}
                  className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card animate-fade-in"
                  style={{ animationDelay: `${i * 30}ms` }}
                  data-testid={`history-entry-${i}`}
                >
                  <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
                    {entry.query_type === "ingredients" ? (
                      <FlaskConical className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <Search className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {entry.query}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Badge
                        variant="outline"
                        className="text-[10px] px-1.5 py-0"
                      >
                        {entry.query_type}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {entry.result_count} result
                        {entry.result_count !== 1 ? "s" : ""}
                      </span>
                    </div>
                  </div>
                  {entry.timestamp && (
                    <span className="text-xs text-muted-foreground shrink-0">
                      {new Date(entry.timestamp).toLocaleDateString()}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && history.length === 0 && (
            <div
              className="text-center py-16 space-y-3"
              data-testid="empty-history"
            >
              <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center">
                <Clock className="w-8 h-8 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground">No searches yet</p>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
