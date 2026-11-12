"use client";

import { useActionState } from "react";

import { signIn, type LoginState } from "./actions";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const initialState: LoginState = {
  error: null,
};

export function LoginForm() {
  const [state, formAction, isPending] = useActionState(signIn, initialState);

return (
  <form action={formAction} className="space-y-5">
    <div className="space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        required
      />
    </div>

    <div className="space-y-2">
      <Label htmlFor="password">Password</Label>
      <Input
        id="password"
        name="password"
        type="password"
        autoComplete="current-password"
        required
      />
    </div>

    {state.error ? (
      <Alert variant="destructive">
        <AlertTitle>Sign-in failed</AlertTitle>
        <AlertDescription>{state.error}</AlertDescription>
      </Alert>
    ) : null}

    <Button type="submit" size="lg" className="w-full" disabled={isPending}>
      {isPending ? "Signing in..." : "Sign in"}
    </Button>
  </form>
);
}