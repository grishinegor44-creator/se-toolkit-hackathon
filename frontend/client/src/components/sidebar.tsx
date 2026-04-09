import { Link, useLocation } from "wouter";
import { Search, Star, Clock, Sun, Moon, Wine, LogIn, LogOut, UserPlus } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

interface AppSidebarProps {
  isDark: boolean;
  onToggleTheme: () => void;
}

const navItems = [
  { path: "/", label: "Search", icon: Search },
  { path: "/favorites", label: "Favorites", icon: Star },
  { path: "/history", label: "History", icon: Clock },
];

export default function AppSidebar({ isDark, onToggleTheme }: AppSidebarProps) {
  const [location] = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.hash = "/";
  };

  return (
    <aside
      className="flex flex-col h-screen bg-card border-r border-border w-16 md:w-56 shrink-0 transition-all duration-200"
      data-testid="sidebar"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-border">
        <div className="w-8 h-8 flex items-center justify-center rounded-lg bg-primary text-primary-foreground shrink-0">
          <Wine className="w-4 h-4" />
        </div>
        <span className="hidden md:block text-sm font-bold tracking-tight text-foreground">
          CocktailBot
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 flex flex-col gap-1 p-2 mt-2">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = location === path;
          return (
            <Link key={path} href={path}>
              <div
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors duration-150 text-sm font-medium",
                  isActive
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
                data-testid={`nav-${label.toLowerCase()}`}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 shrink-0",
                    isActive && "text-primary"
                  )}
                />
                <span className="hidden md:block">{label}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Auth section */}
      <div className="p-2 border-t border-border">
        {isAuthenticated ? (
          <div className="space-y-2">
            <div className="hidden md:block px-3 py-2 text-xs text-muted-foreground">
              Signed in as <span className="text-foreground font-medium">{user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg w-full text-muted-foreground hover:bg-muted hover:text-foreground transition-colors duration-150 text-sm"
              data-testid="button-logout"
              aria-label="Logout"
            >
              <LogOut className="w-4 h-4 shrink-0" />
              <span className="hidden md:block">Logout</span>
            </button>
          </div>
        ) : (
          <div className="space-y-1">
            <Link href="/login">
              <div
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors duration-150 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
                data-testid="nav-login"
              >
                <LogIn className="w-4 h-4 shrink-0" />
                <span className="hidden md:block">Sign in</span>
              </div>
            </Link>
            <Link href="/register">
              <div
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors duration-150 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
                data-testid="nav-register"
              >
                <UserPlus className="w-4 h-4 shrink-0" />
                <span className="hidden md:block">Register</span>
              </div>
            </Link>
          </div>
        )}
      </div>

      {/* Theme toggle */}
      <div className="p-2 border-t border-border">
        <button
          onClick={onToggleTheme}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg w-full text-muted-foreground hover:bg-muted hover:text-foreground transition-colors duration-150 text-sm"
          data-testid="button-theme-toggle"
          aria-label="Toggle theme"
        >
          {isDark ? (
            <Sun className="w-4 h-4 shrink-0" />
          ) : (
            <Moon className="w-4 h-4 shrink-0" />
          )}
          <span className="hidden md:block">
            {isDark ? "Light mode" : "Dark mode"}
          </span>
        </button>
      </div>
    </aside>
  );
}
