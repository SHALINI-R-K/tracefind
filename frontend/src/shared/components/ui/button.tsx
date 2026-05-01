import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center whitespace-nowrap font-medium",
    "ring-offset-background transition-[transform,background,border,box-shadow,color]",
    "duration-200 ease-ink",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
    "focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
    "active:translate-y-px",
  ].join(" "),
  {
    variants: {
      variant: {
        default: [
          "bg-primary text-primary-foreground",
          "border border-primary/0",
          "hover:bg-primary/90",
          "shadow-[0_0_0_1px_hsl(var(--primary)/0.4),0_8px_24px_-12px_hsl(var(--primary)/0.5)]",
          "hover:shadow-[0_0_0_1px_hsl(var(--primary)/0.6),0_12px_32px_-12px_hsl(var(--primary)/0.6)]",
        ].join(" "),
        outline: [
          "bg-transparent text-foreground",
          "border border-border",
          "hover:bg-accent hover:text-accent-foreground hover:border-primary/40",
        ].join(" "),
        ghost:
          "bg-transparent text-foreground hover:bg-accent hover:text-accent-foreground border border-transparent",
        destructive: [
          "bg-destructive text-destructive-foreground",
          "border border-destructive/0",
          "hover:bg-destructive/90",
          "shadow-[0_0_0_1px_hsl(var(--destructive)/0.4),0_8px_24px_-12px_hsl(var(--destructive)/0.4)]",
        ].join(" "),
        secondary: [
          "bg-secondary text-secondary-foreground",
          "border border-border",
          "hover:bg-accent",
        ].join(" "),
        link: "text-primary underline-offset-4 hover:underline border border-transparent",
      },
      size: {
        default: "h-10 px-5 text-sm rounded-md",
        sm: "h-8 px-3.5 text-xs rounded-sm",
        lg: "h-12 px-7 text-[0.95rem] rounded-md",
        icon: "h-10 w-10 rounded-md",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
