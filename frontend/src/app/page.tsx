import { Suspense } from "react";
import { redirect } from "next/navigation";
import { connection } from "next/server";
import { OrganizationForm } from "./components/organization-form";
import { createClient } from "@/lib/supabase/server";
import { signOut } from "./actions";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";

type OrganizationSummary = {
  organization_id: string;
  name: string;
  role: "owner" | "admin" | "agent" | "viewer";
};

export default function Home() {
  return (
    <Suspense fallback={<DashboardLoading />}>
      <Dashboard />
    </Suspense>
  );
}



async function Dashboard() {
  await connection();

  const supabase = await createClient();
  const { data: claimsData } = await supabase.auth.getClaims();

  if (!claimsData?.claims) {
    redirect("/login");
  }

  const {
  data: { session },
} = await supabase.auth.getSession();

if (!session?.access_token) {
  redirect("/login");
}

const backendApiUrl = process.env.BACKEND_API_URL;

if (!backendApiUrl) {
  throw new Error("Backend API URL is not configured.");
}

const response = await fetch(`${backendApiUrl}/organizations`, {
  headers: {
    Authorization: `Bearer ${session.access_token}`,
  },
  cache: "no-store",
  signal: AbortSignal.timeout(5_000),
});

if (!response.ok) {
  throw new Error("Could not load workspaces.");
}

const organizations =
  (await response.json()) as OrganizationSummary[];

return (
  <main className="min-h-screen bg-muted/30 px-6 py-12 sm:py-20">
    <section className="mx-auto w-full max-w-xl">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
        <h1 className="text-balance text-3xl font-semibold tracking-tight">
  {organizations.length === 0
    ? "Create your workspace"
    : "Your workspaces"}
</h1>

<p className="max-w-prose text-muted-foreground">
  {organizations.length === 0
    ? "A workspace is the security boundary for your team's support tickets."
    : "Choose a workspace to manage its support operations."}
</p>
        </div>

        <form action={signOut}>
          <Button type="submit" variant="outline" size="sm">
            Sign out
          </Button>
        </form>
      </div>

   <Card>
  {organizations.length === 0 ? (
    <>
      <CardHeader>
        <CardTitle>Workspace details</CardTitle>
      </CardHeader>

      <CardContent>
        <OrganizationForm />
      </CardContent>
    </>
  ) : (
    <>
      <CardHeader>
        <CardTitle>Your workspaces</CardTitle>
      </CardHeader>

      <CardContent>
        <ul className="divide-y divide-border">
          {organizations.map((organization) => (
      <li key={organization.organization_id}>
  <Link
    href={`/organizations/${organization.organization_id}`}
    className="flex items-center justify-between gap-4 rounded-lg px-2 py-3 transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
  >
    <span className="font-medium">{organization.name}</span>
    <span className="text-sm text-muted-foreground">
      {organization.role}
    </span>
  </Link>
</li>
          ))}
        </ul>
      </CardContent>
    </>
  )}
</Card>
    </section>
  </main>
);
}

function DashboardLoading() {
  return (
    <main className="grid min-h-screen place-items-center bg-muted/30 px-6">
      <p className="text-sm text-muted-foreground">Loading workspace...</p>
    </main>
  );
}