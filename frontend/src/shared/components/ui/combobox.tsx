"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/shared/lib/utils";

export interface ComboboxOption {
  value: string;
  label?: string;
}

export interface ComboboxProps {
  value: string;
  onChange: (value: string) => void;
  options: ComboboxOption[];
  id?: string;
  placeholder?: string;
  /** When true, show a small text filter at the top of the popover. */
  searchable?: boolean;
}

function labelFor(option: ComboboxOption): string {
  return option.label ?? option.value.charAt(0).toUpperCase() + option.value.slice(1);
}

/**
 * Custom select / combobox themed for TraceFind. Replaces the native
 * <select> so the popover, hover states, and selected highlight all
 * use our amber-on-charcoal palette instead of the browser's default
 * bright-blue rendering.
 *
 * Keyboard:
 *   ArrowDown / ArrowUp — move focus through options
 *   Enter / Space — pick the focused option
 *   Escape — close
 *   Type-to-search — letters jump to the first matching option
 */
export function Combobox({
  value,
  onChange,
  options,
  id,
  placeholder = "Select…",
  searchable = false,
}: ComboboxProps) {
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState<number>(() =>
    Math.max(
      0,
      options.findIndex((o) => o.value === value)
    )
  );
  const [filter, setFilter] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const filterRef = useRef<HTMLInputElement>(null);
  const typeBufferRef = useRef<{ buf: string; expires: number }>({
    buf: "",
    expires: 0,
  });

  const filteredOptions = useMemo(() => {
    if (!filter.trim()) return options;
    const q = filter.trim().toLowerCase();
    return options.filter((o) =>
      labelFor(o).toLowerCase().includes(q) || o.value.toLowerCase().includes(q)
    );
  }, [options, filter]);

  // Keep activeIndex in range after filtering
  useEffect(() => {
    if (activeIndex >= filteredOptions.length) {
      setActiveIndex(0);
    }
  }, [filteredOptions, activeIndex]);

  // Reset filter when closing
  useEffect(() => {
    if (!open) setFilter("");
  }, [open]);

  // When opening, scroll the active option into view + focus search if shown
  useEffect(() => {
    if (!open) return;
    const idx = options.findIndex((o) => o.value === value);
    if (idx >= 0) setActiveIndex(idx);
    requestAnimationFrame(() => {
      if (searchable) {
        filterRef.current?.focus();
      }
      const list = listRef.current;
      if (!list) return;
      const el = list.children[Math.max(0, idx)] as HTMLElement | undefined;
      el?.scrollIntoView({ block: "nearest" });
    });
  }, [open, options, value, searchable]);

  // Outside click / Escape close
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);

  const pick = useCallback(
    (next: string) => {
      onChange(next);
      setOpen(false);
    },
    [onChange]
  );

  const onTriggerKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen(true);
    }
  };

  const onListKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(filteredOptions.length - 1, i + 1));
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(0, i - 1));
      return;
    }
    if (e.key === "Home") {
      e.preventDefault();
      setActiveIndex(0);
      return;
    }
    if (e.key === "End") {
      e.preventDefault();
      setActiveIndex(filteredOptions.length - 1);
      return;
    }
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      const opt = filteredOptions[activeIndex];
      if (opt) pick(opt.value);
      return;
    }
    // Type-to-search: gather letters into a buffer that resets after 800ms
    if (!searchable && e.key.length === 1 && /[a-zA-Z0-9]/.test(e.key)) {
      const now = Date.now();
      const buf =
        now > typeBufferRef.current.expires ? "" : typeBufferRef.current.buf;
      const next = (buf + e.key).toLowerCase();
      typeBufferRef.current = { buf: next, expires: now + 800 };
      const found = filteredOptions.findIndex((o) =>
        labelFor(o).toLowerCase().startsWith(next)
      );
      if (found >= 0) setActiveIndex(found);
    }
  };

  // When activeIndex changes, scroll into view
  useEffect(() => {
    if (!open) return;
    const list = listRef.current;
    if (!list) return;
    const el = list.children[activeIndex] as HTMLElement | undefined;
    el?.scrollIntoView({ block: "nearest" });
  }, [activeIndex, open]);

  const selected = options.find((o) => o.value === value);

  return (
    <div ref={containerRef} className="relative">
      <button
        id={id}
        type="button"
        role="combobox"
        aria-expanded={open}
        aria-haspopup="listbox"
        onClick={() => setOpen((o) => !o)}
        onKeyDown={onTriggerKeyDown}
        className={cn(
          "flex h-11 w-full items-center justify-between gap-2 rounded-md border border-input bg-card/40",
          "px-4 py-2 text-left text-[0.95rem] text-foreground",
          "transition-[border-color,box-shadow,background] duration-200 ease-ink",
          open
            ? "border-primary bg-card shadow-[0_0_0_3px_hsl(var(--primary)/0.15)]"
            : "hover:border-primary/40"
        )}
      >
        <span className={cn(selected ? "" : "text-muted-foreground/70")}>
          {selected ? labelFor(selected) : placeholder}
        </span>
        <ChevronsUpDown
          className="h-4 w-4 shrink-0 text-muted-foreground"
          strokeWidth={1.75}
        />
      </button>

      {open && (
        <div
          className={cn(
            "absolute left-0 top-full z-50 mt-2 w-full",
            "rounded-lg border border-border bg-popover text-popover-foreground",
            "shadow-[0_24px_64px_-32px_rgba(0,0,0,0.6),0_0_0_1px_hsl(var(--primary)/0.08)]",
            "py-1.5"
          )}
          onKeyDown={onListKeyDown}
        >
          {searchable && (
            <div className="px-2 pb-1.5">
              <input
                ref={filterRef}
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Search…"
                className={cn(
                  "h-8 w-full rounded-md border border-input bg-card/40 px-3 text-sm",
                  "placeholder:text-muted-foreground/70",
                  "focus-visible:outline-none focus-visible:border-primary",
                  "focus-visible:shadow-[0_0_0_3px_hsl(var(--primary)/0.15)]"
                )}
              />
            </div>
          )}
          {filteredOptions.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              No matches.
            </p>
          ) : (
            <ul
              ref={listRef}
              role="listbox"
              tabIndex={-1}
              className="max-h-64 overflow-y-auto px-1 outline-none"
            >
              {filteredOptions.map((opt, i) => {
                const isSelected = opt.value === value;
                const isActive = i === activeIndex;
                return (
                  <li
                    key={opt.value}
                    role="option"
                    aria-selected={isSelected}
                    onMouseEnter={() => setActiveIndex(i)}
                    onClick={() => pick(opt.value)}
                    className={cn(
                      "flex cursor-pointer items-center justify-between rounded-md px-3 py-2",
                      "text-sm transition-colors duration-100",
                      isActive
                        ? "bg-accent text-foreground"
                        : "text-foreground/90 hover:bg-accent"
                    )}
                  >
                    <span>{labelFor(opt)}</span>
                    {isSelected && (
                      <Check
                        className="h-3.5 w-3.5 text-primary"
                        strokeWidth={2.5}
                      />
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
