import * as React from "react";
import { cn } from "@/shared/lib/utils";

const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => {
  return (
    <div className="relative">
      <select
        ref={ref}
        className={cn(
          "flex h-11 w-full appearance-none rounded-md border border-input bg-card/40",
          "px-4 pr-10 py-2 text-[0.95rem] text-foreground",
          "focus-visible:outline-none focus-visible:border-primary focus-visible:bg-card",
          "focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.15)]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "transition-[border-color,box-shadow,background] duration-200 ease-ink capitalize",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <span
        className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground"
        aria-hidden
      >
        ▾
      </span>
    </div>
  );
});
Select.displayName = "Select";

export { Select };
