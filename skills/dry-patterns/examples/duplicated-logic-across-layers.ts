export {};

// Duplicated logic across layers: the browser form and the API handler each
// re-typed the signup rules. The fix declares the rules once and both layers read them.

interface SignupInput {
  email: string;
  password: string;
  displayName: string;
}

// --- Violation: two hand-written copies of the same rules ---
function clientValidateSignup(input: SignupInput): string[] {
  const errors: string[] = [];
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(input.email)) errors.push("email: invalid");
  if (input.password.length < 12) errors.push("password: too short");
  if (input.displayName.trim().length === 0) errors.push("displayName: required");
  return errors;
}

function serverHandleSignup(input: SignupInput): { status: number; errors: string[] } {
  const errors: string[] = [];
  if (!input.email.includes("@") || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(input.email)) errors.push("email: invalid");
  if (!(input.password.length >= 12)) errors.push("password: too short");
  if (!input.displayName.trim()) errors.push("displayName: required");
  return { status: errors.length ? 422 : 201, errors };
}

// --- Fix: one schema module imported by both the client bundle and the server ---
type Rule = { field: keyof SignupInput; message: string; ok: (value: string) => boolean };

const signupSchema: readonly Rule[] = [
  { field: "email", message: "invalid", ok: (v) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v) },
  { field: "password", message: "too short", ok: (v) => v.length >= 12 },
  { field: "displayName", message: "required", ok: (v) => v.trim().length > 0 },
];

function validate(input: SignupInput): string[] {
  return signupSchema.filter((r) => !r.ok(input[r.field])).map((r) => `${r.field}: ${r.message}`);
}

const clientValidate = validate;
function serverHandle(input: SignupInput): { status: number; errors: string[] } {
  const errors = validate(input);
  return { status: errors.length ? 422 : 201, errors };
}

// --- Demo: both layers agree before and after ---
const inputs: SignupInput[] = [
  { email: "ana@example.com", password: "correct-horse-battery", displayName: "Ana" },
  { email: "not-an-email", password: "short", displayName: "  " },
];
for (const input of inputs) {
  const before = JSON.stringify([clientValidateSignup(input), serverHandleSignup(input)]);
  const after = JSON.stringify([clientValidate(input), serverHandle(input)]);
  console.log(after, before === after ? "same" : "DIFFERENT");
}
