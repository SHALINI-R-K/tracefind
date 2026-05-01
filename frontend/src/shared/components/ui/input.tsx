import * as React from "react";
import { cn } from "@/shared/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-md border border-input bg-card/40",
          "px-4 py-2 text-[0.95rem] text-foreground",
          "placeholder:text-muted-foreground/70",
          "focus-visible:outline-none focus-visible:border-primary",
          "focus-visible:bg-card focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.15)]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "transition-[border-color,box-shadow,background] duration-200 ease-ink",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
