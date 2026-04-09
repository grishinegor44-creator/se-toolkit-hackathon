import { ReactNode } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogIn, UserPlus } from "lucide-react";

interface AuthGuardProps {
  children: ReactNode;
  requireAuth?: boolean;
}

export default function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const [, navigate] = useLocation();
  const { isAuthenticated } = useAuth();

  if (requireAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-background">
        <Card className="w-full max-w-md mx-4">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please sign in or register to access this feature
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              className="w-full"
              onClick={() => navigate("/login")}
            >
              <LogIn className="w-4 h-4 mr-2" />
              Sign in
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => navigate("/register")}
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Register
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
}
