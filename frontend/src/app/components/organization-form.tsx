"use client";
import { FormEvent, useState } from "react";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type CreateOrganizationResponse = {
  detail?: string;
  name?: string;
};

export function OrganizationForm() {
  const [name, setName] = useState("");
  const [createdName, setCreatedName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setCreatedName(null);
    setIsPending(true);

    try {
      const response = await fetch("/api/organizations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
      });

      const payload = (await response.json()) as CreateOrganizationResponse;

      if (!response.ok) {
        setError(payload.detail ?? "Could not create the workspace.");
        return;
      }

      setCreatedName(payload.name ?? name);
      setName("");
    } catch {
      setError("Could not reach the application. Please try again.");
    } finally {
      setIsPending(false);
    }
  }

return (
  <form onSubmit={handleSubmit} className="space-y-5">
    <div className="space-y-2">
      <Label htmlFor="organization-name">Workspace name</Label>

      <Input
        id="organization-name"
        name="organization-name"
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Acme Support"
        minLength={1}
        maxLength={200}
        required
        disabled={isPending}
        aria-describedby="organization-name-help"
      />

      <p id="organization-name-help" className="text-sm text-muted-foreground">
        Your workspace keeps tickets and access separate from other teams.
      </p>
    </div>

    {error ? (
      <Alert variant="destructive">
        <AlertTitle>Workspace was not created</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    ) : null}

    {createdName ? (
      <Alert role="status">
        <AlertTitle>Workspace created</AlertTitle>
        <AlertDescription>
        Workspace &quot;{createdName}&quot; was created.
        </AlertDescription>
      </Alert>
    ) : null}

    <Button type="submit" size="lg" disabled={isPending}>
      {isPending ? "Creating workspace..." : "Create workspace"}
    </Button>
  </form>
);
}