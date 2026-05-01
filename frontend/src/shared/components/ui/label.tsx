import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";

/**
 * Labels are small, monospaced, uppercase, and tracked — like field
 * captions in a technical schematic. They sit above the input with
 * deliberate breathing room.
 */
const labelVariants = cva(
  [
    "block font-mono text-[0.7rem] uppercase tracking-[0.18em] text-muted-foreground",
    "peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
  ].join(" ")
);

const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root> &
    VariantProps<typeof labelVariants>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants(), className)}
    {...props}
  />
));
Label.displayName = LabelPrimitive.Root.displayName;

export { Label };
