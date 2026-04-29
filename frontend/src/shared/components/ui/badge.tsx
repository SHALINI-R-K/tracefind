import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive: "border-transparent bg-destructive text-destructive-foreground",
        outline: "text-foreground",
        lost: "border-transparent bg-red-500/15 text-red-400",
        found: "border-transparent bg-emerald-500/15 text-emerald-400",
        active: "border-transparent bg-blue-500/15 text-blue-400",
        matched: "border-transparent bg-amber-500/15 text-amber-400",
        claimed: "border-transparent bg-emerald-500/15 text-emerald-400",
        pending: "border-transparent bg-amber-500/15 text-amber-400",
        confirmed: "border-transparent bg-emerald-500/15 text-emerald-400",
        rejected: "border-transparent bg-red-500/15 text-red-400",
        archived: "border-transparent bg-zinc-500/15 text-zinc-400",
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
