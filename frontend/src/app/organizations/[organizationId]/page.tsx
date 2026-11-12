import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { connection } from "next/server";
import { Suspense } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createClient } from "@/lib/supabase/server";

type OrganizationTicketsPageProps = {
  params: Promise<{ organizationId: string }>;
};

type TicketListItem = {
  ticket_id: string;
  subject: string;
  status: string;
  created_at: string;
};

export default function OrganizationTicketsPage(
  props: OrganizationTicketsPageProps,
) {
  return (
    <Suspense fallback={<TicketsLoading />}>
      <OrganizationTicketsDashboard {...props} />
    </Suspense>
  );
}

async function OrganizationTicketsDashboard({
  params,
}: OrganizationTicketsPageProps) {
  await connection();

  const { organizationId } = await params;
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

  const response = await fetch(
    `${backendApiUrl}/organizations/${organizationId}/tickets`,
    {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    },
  );

  if (response.status === 403) {
    notFound();
  }

  if (!response.ok) {
    throw new Error("Could not load tickets.");
  }

  const tickets = (await response.json()) as TicketListItem[];

  return (
    <main className="min-h-screen bg-muted/30 px-6 py-12 sm:py-20">
      <section className="mx-auto w-full max-w-3xl">
        <Link
          href="/"
          className="text-sm font-medium text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          All workspaces
        </Link>

        <div className="mt-6 space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight">Inbox</h1>
          <p className="text-muted-foreground">
            Tickets for the selected workspace.
          </p>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Tickets</CardTitle>
            <CardDescription>
              Incoming support requests will appear here.
            </CardDescription>
          </CardHeader>

          <CardContent>
            {tickets.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No tickets have been created for this workspace yet.
              </p>
            ) : (
              <ul className="divide-y divide-border">
                {tickets.map((ticket) => (
                  <li
                    key={ticket.ticket_id}
                    className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
                  >
                    <div>
                      <p className="font-medium">{ticket.subject}</p>
                      <time
                        dateTime={ticket.created_at}
                        className="text-sm text-muted-foreground"
                      >
                        {new Intl.DateTimeFormat("en", {
                          dateStyle: "medium",
                          timeStyle: "short",
                        }).format(new Date(ticket.created_at))}
                      </time>
                    </div>

                    <span className="text-sm capitalize text-muted-foreground">
                      {ticket.status}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

function TicketsLoading() {
  return (
    <main className="grid min-h-screen place-items-center bg-muted/30 px-6">
      <p className="text-sm text-muted-foreground">Loading inbox...</p>
    </main>
  );
}
