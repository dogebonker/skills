import { render } from "vitest-browser-react";
import { describe, expect, it } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
  it("renders the label", async () => {
    const screen = render(<Button label="Save" />);
    await expect.element(screen.getByText("Save")).toBeVisible();
  });

  it("calls onClick", async () => {
    let clicked = 0;
    const screen = render(<Button label="Go" onClick={() => clicked++} />);
    await screen.getByRole("button").click();
    expect(clicked).toBe(1);
  });
});
