import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";

/**
 * Badges are compact label-stamps. Uppercase mono with letter tracking,
 * 1px border in the accent color, soft tinted background. Distinct enough
 * to scan in a list, restrained enough to live next to other UI.
 */
const badgeVariants = cva(
  [
    "inline-flex items-center font-medium",
    "px-2 py-0.5 text-xs",
    "border rounded-md select-none",
    "transition-colors duration-150",
  ].join(" "),
  {
    variants: {
      variant: {
        default: "border-primary/40 text-primary bg-primary/10",
        secondary: "border-border text-foreground bg-secondary",
        outline: "border-border text-foreground bg-transparent",
        destructive: "border-destructive/40 text-destructive bg-destructive/10",

        // Item types
        lost: "border-status-lost/40 text-status-lost bg-status-lost/[0.08]",
        found: "border-status-found/40 text-status-found bg-status-found/[0.08]",

        // Statuses
        active: "border-primary/40 text-primary bg-primary/[0.08]",
        matched: "border-status-matched/40 text-status-matched bg-status-matched/[0.08]",
        pending: "border-status-pending/40 text-status-pending bg-status-pending/[0.08]",
        confirmed: "border-status-found/40 text-status-found bg-status-found/[0.08]",
        claimed: "border-status-found/40 text-status-found bg-status-found/[0.08]",
        rejected: "border-status-archived/40 text-status-archived bg-status-archived/[0.08] line-through decoration-1",
        archived: "border-status-archived/40 text-status-archived bg-status-archived/[0.08]",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
