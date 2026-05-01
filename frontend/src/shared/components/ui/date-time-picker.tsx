"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Calendar, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/components/ui/button";

/**
 * Custom date+time picker themed for TraceFind. No new deps —
 * built on plain React + Tailwind tokens. Returns/accepts a string
 * compatible with `<input type="datetime-local">` so the form code
 * stays unchanged: `YYYY-MM-DDTHH:MM`.
 */
export interface DateTimePickerProps {
  value: string;
  onChange: (value: string) => void;
  id?: string;
  max?: Date;
  placeholder?: string;
}

const DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function pad(n: number) {
  return n.toString().padStart(2, "0");
}

function parseValue(v: string): { date: Date | null; h12: number; m: number; pm: boolean } {
  if (!v) return { date: null, h12: 12, m: 0, pm: false };
  const d = new Date(v);
  if (isNaN(d.getTime())) return { date: null, h12: 12, m: 0, pm: false };
  const h = d.getHours();
  return {
    date: d,
    h12: ((h + 11) % 12) + 1,
    m: d.getMinutes(),
    pm: h >= 12,
  };
}

function formatDisplay(v: string): string {
  if (!v) return "";
  const d = new Date(v);
  if (isNaN(d.getTime())) return "";
  const day = d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  const time = d.toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
  return `${day} · ${time}`;
}

function combineToValue(date: Date, h12: number, m: number, pm: boolean): string {
  const h24 = pm ? (h12 % 12) + 12 : h12 % 12;
  const y = date.getFullYear();
  const mo = pad(date.getMonth() + 1);
  const da = pad(date.getDate());
  return `${y}-${mo}-${da}T${pad(h24)}:${pad(m)}`;
}

function startOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

export function DateTimePicker({
  value,
  onChange,
  id,
  max,
  placeholder = "Pick a date and time",
}: DateTimePickerProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const parsed = useMemo(() => parseValue(value), [value]);
  const [viewMonth, setViewMonth] = useState<Date>(
    () => startOfMonth(parsed.date ?? new Date())
  );

  const today = useMemo(() => new Date(), []);
  const maxDate = max ?? null;

  // Close on outside click / Escape
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
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Build the 6-week grid for the visible month
  const grid = useMemo(() => {
    const first = startOfMonth(viewMonth);
    const startDay = first.getDay();
    const cells: Date[] = [];
    const startDate = new Date(first);
    startDate.setDate(1 - startDay);
    for (let i = 0; i < 42; i++) {
      const d = new Date(startDate);
      d.setDate(startDate.getDate() + i);
      cells.push(d);
    }
    return cells;
  }, [viewMonth]);

  const updateValue = useCallback(
    (next: { date?: Date; h12?: number; m?: number; pm?: boolean }) => {
      const date = next.date ?? parsed.date ?? new Date();
      const h12 = next.h12 ?? parsed.h12;
      const m = next.m ?? parsed.m;
      const pm = next.pm ?? parsed.pm;
      onChange(combineToValue(date, h12, m, pm));
    },
    [parsed, onChange]
  );

  const handlePickDay = (d: Date) => {
    if (maxDate && d > maxDate) return;
    updateValue({ date: d });
  };

  const handleClear = () => {
    onChange("");
  };

  const handleToday = () => {
    const now = new Date();
    setViewMonth(startOfMonth(now));
    updateValue({
      date: now,
      h12: ((now.getHours() + 11) % 12) + 1,
      m: now.getMinutes(),
      pm: now.getHours() >= 12,
    });
  };

  const stepHour = (delta: number) => {
    const next = ((parsed.h12 - 1 + delta + 12) % 12) + 1;
    updateValue({ h12: next });
  };
  const stepMinute = (delta: number) => {
    const next = (parsed.m + delta + 60) % 60;
    updateValue({ m: next });
  };

  const display = formatDisplay(value);

  return (
    <div ref={containerRef} className="relative">
      <button
        id={id}
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="dialog"
        aria-expanded={open}
        className={cn(
          "flex h-11 w-full items-center justify-between gap-2 rounded-md border border-input bg-card/40",
          "px-4 py-2 text-left text-[0.95rem] text-foreground",
          "transition-[border-color,box-shadow,background] duration-200 ease-ink",
          open
            ? "border-primary bg-card shadow-[0_0_0_3px_hsl(var(--primary)/0.15)]"
            : "hover:border-primary/40"
        )}
      >
        <span className={cn(display ? "" : "text-muted-foreground/70")}>
          {display || placeholder}
        </span>
        <Calendar className="h-4 w-4 text-muted-foreground" strokeWidth={1.75} />
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Choose date and time"
          className={cn(
            "absolute left-0 top-full z-50 mt-2 w-[20rem]",
            "rounded-lg border border-border bg-popover text-popover-foreground",
            "shadow-[0_24px_64px_-32px_rgba(0,0,0,0.6),0_0_0_1px_hsl(var(--primary)/0.08)]",
            "p-3"
          )}
        >
          {/* Month nav */}
          <div className="mb-3 flex items-center justify-between">
            <button
              type="button"
              onClick={() =>
                setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() - 1, 1))
              }
              className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Previous month"
            >
              <ChevronLeft className="h-4 w-4" strokeWidth={2} />
            </button>
            <p className="text-sm font-semibold tracking-tight">
              {MONTHS[viewMonth.getMonth()]} {viewMonth.getFullYear()}
            </p>
            <button
              type="button"
              onClick={() =>
                setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() + 1, 1))
              }
              className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Next month"
            >
              <ChevronRight className="h-4 w-4" strokeWidth={2} />
            </button>
          </div>

          {/* Day-of-week header */}
          <div className="mb-1 grid grid-cols-7 gap-0.5 text-center">
            {DAYS.map((d) => (
              <div
                key={d}
                className="py-1 text-[0.65rem] font-medium uppercase tracking-wider text-muted-foreground"
              >
                {d}
              </div>
            ))}
          </div>

          {/* Day grid */}
          <div className="grid grid-cols-7 gap-0.5">
            {grid.map((d, i) => {
              const inMonth = d.getMonth() === viewMonth.getMonth();
              const isSelected = parsed.date && isSameDay(d, parsed.date);
              const isToday = isSameDay(d, today);
              const disabled = !!(maxDate && d > maxDate);
              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => handlePickDay(d)}
                  disabled={disabled}
                  className={cn(
                    "flex h-8 items-center justify-center rounded-md text-sm tabular-nums",
                    "transition-colors duration-150",
                    !inMonth && "text-muted-foreground/40",
                    inMonth && !isSelected && "text-foreground",
                    isSelected
                      ? "bg-primary text-primary-foreground font-semibold hover:bg-primary"
                      : "hover:bg-accent",
                    isToday && !isSelected && "ring-1 ring-primary/40",
                    disabled && "cursor-not-allowed opacity-30 hover:bg-transparent"
                  )}
                >
                  {d.getDate()}
                </button>
              );
            })}
          </div>

          {/* Time row */}
          <div className="mt-3 border-t border-border pt-3">
            <div className="flex items-center justify-center gap-2">
              <TimeStepper
                value={parsed.h12}
                onUp={() => stepHour(1)}
                onDown={() => stepHour(-1)}
                onChange={(n) => updateValue({ h12: ((n - 1 + 12) % 12) + 1 })}
                min={1}
                max={12}
                label="Hour"
              />
              <span className="text-lg text-muted-foreground" aria-hidden>
                :
              </span>
              <TimeStepper
                value={parsed.m}
                onUp={() => stepMinute(5)}
                onDown={() => stepMinute(-5)}
                onChange={(n) => updateValue({ m: Math.max(0, Math.min(59, n)) })}
                min={0}
                max={59}
                label="Minute"
              />

              <div className="ml-2 flex flex-col gap-0.5">
                {(["AM", "PM"] as const).map((label) => {
                  const isPm = label === "PM";
                  const active = parsed.pm === isPm;
                  return (
                    <button
                      key={label}
                      type="button"
                      onClick={() => updateValue({ pm: isPm })}
                      className={cn(
                        "rounded-sm px-2 py-1 text-[0.7rem] font-semibold tracking-wider",
                        "transition-colors duration-150",
                        active
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-foreground"
                      )}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-3 flex items-center justify-between gap-2 border-t border-border pt-3">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="h-7 px-2 text-xs"
            >
              Clear
            </Button>
            <div className="flex gap-1.5">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleToday}
                className="h-7 px-2 text-xs"
              >
                Today
              </Button>
              <Button
                type="button"
                size="sm"
                onClick={() => setOpen(false)}
                className="h-7 px-3 text-xs"
                disabled={!parsed.date}
              >
                Done
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface TimeStepperProps {
  value: number;
  onUp: () => void;
  onDown: () => void;
  onChange: (n: number) => void;
  min: number;
  max: number;
  label: string;
}

function TimeStepper({
  value,
  onUp,
  onDown,
  onChange,
  min,
  max,
  label,
}: TimeStepperProps) {
  return (
    <div className="flex flex-col items-center">
      <button
        type="button"
        onClick={onUp}
        aria-label={`${label} up`}
        className="flex h-5 w-12 items-center justify-center rounded-sm text-muted-foreground hover:bg-accent hover:text-foreground"
      >
        <ChevronUp />
      </button>
      <input
        type="number"
        min={min}
        max={max}
        value={pad(value)}
        onChange={(e) => {
          const n = parseInt(e.target.value, 10);
          if (!isNaN(n)) onChange(n);
        }}
        aria-label={label}
        className={cn(
          "w-12 rounded-sm border border-transparent bg-transparent py-1 text-center",
          "text-xl font-semibold tabular-nums text-foreground",
          "focus-visible:border-primary focus-visible:bg-card focus-visible:outline-none",
          "[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        )}
      />
      <button
        type="button"
        onClick={onDown}
        aria-label={`${label} down`}
        className="flex h-5 w-12 items-center justify-center rounded-sm text-muted-foreground hover:bg-accent hover:text-foreground"
      >
        <ChevronDown />
      </button>
    </div>
  );
}

function ChevronUp() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path d="M3 7L6 4L9 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ChevronDown() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path d="M3 5L6 8L9 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
