import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LoginForm } from "@/app/login/login-form";

export default function LoginPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-muted/30 px-6 py-12">
      <section className="w-full max-w-md">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl tracking-tight">
              Sign in to SupportFlow AI
            </CardTitle>
            <CardDescription>
              Use your local development account to access the workspace.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </section>
    </main>
  );
}