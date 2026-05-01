"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  ImagePlus,
  Loader2,
  ArrowRight,
  MapPin,
} from "lucide-react";
import { createReport, ReportType } from "@/contexts/reporting/api/reports";
import { fileToResizedDataUri } from "@/shared/lib/image";
import { Button } from "@/shared/components/ui/button";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Select } from "@/shared/components/ui/select";
import { cn } from "@/shared/lib/utils";

const CATEGORIES = [
  "bag",
  "wallet",
  "phone",
  "laptop",
  "keys",
  "documents",
  "clothing",
  "jewelry",
  "book",
  "other",
];

export default function ReportPage() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [type, setType] = useState<ReportType>("lost");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("other");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function onFileChange(f: File | null) {
    setFile(f);
    if (f) {
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(f);
    } else {
      setPreview(null);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Please attach a photo — embeddings need an image to match against.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const image = await fileToResizedDataUri(file);
      const report = await createReport({ type, description, category, image });
      router.push(`/dashboard/items/${report.id}`);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  const charCount = description.length;
  const charPct = Math.min((charCount / 500) * 100, 100);

  return (
    <div className="mx-auto max-w-3xl space-y-10">
      {/* Header */}
      <header className="opacity-0 animate-fade-in-up">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-muted-foreground">
          Section&nbsp;02 &mdash; Report an item
        </p>
        <h1 className="mt-3 font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl">
          New <span className="underline-accent">report</span>.
        </h1>
        <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">
          Describe the item and upload a photo. The matching engine reads both
          your text and the image — be specific.
        </p>
      </header>

      <div className="rule-double opacity-0 animate-fade-in-up [animation-delay:120ms]" />

      {/* Form card */}
      <form
        onSubmit={onSubmit}
        className="
          relative rounded-lg border border-border bg-card
          shadow-rest opacity-0 animate-fade-in-up [animation-delay:200ms]
        "
      >
        {/* Top stripe */}
        <div className="flex items-center justify-between border-b border-border bg-card/60 px-7 py-3.5">
          <p className="font-mono text-[0.65rem] uppercase tracking-[0.28em] text-muted-foreground">
            Form&nbsp;01 ·{" "}
            <span className={type === "lost" ? "text-status-lost" : "text-status-found"}>
              {type === "lost" ? "Item lost" : "Item found"}
            </span>
          </p>
          <p className="font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
            Filed&nbsp;
            <span className="text-foreground">
              {new Date().toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </span>
          </p>
        </div>

        <div className="space-y-9 px-7 py-9">
          {/* TYPE */}
          <fieldset>
            <Label className="mb-3">Type</Label>
            <div className="grid grid-cols-2 overflow-hidden rounded-md border border-border">
              {(["lost", "found"] as ReportType[]).map((t) => {
                const active = type === t;
                return (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setType(t)}
                    className={cn(
                      "flex flex-col items-start gap-1 px-5 py-4 text-left",
                      "transition-colors duration-200 ease-ink",
                      "border-r last:border-r-0 border-border",
                      active
                        ? t === "lost"
                          ? "bg-status-lost/15 text-status-lost ring-1 ring-status-lost/40 -m-px"
                          : "bg-status-found/15 text-status-found ring-1 ring-status-found/40 -m-px"
                        : "bg-card hover:bg-accent text-foreground"
                    )}
                  >
                    <span className="font-mono text-[0.6rem] uppercase tracking-[0.22em] opacity-70">
                      {t === "lost" ? "Currently missing" : "Currently held"}
                    </span>
                    <span className="text-lg font-semibold tracking-tight">
                      {t === "lost" ? "I lost it" : "I found it"}
                    </span>
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* CATEGORY */}
          <div>
            <Label htmlFor="category" className="mb-2.5">
              Category
            </Label>
            <Select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c} className="capitalize">
                  {c}
                </option>
              ))}
            </Select>
          </div>

          {/* DESCRIPTION */}
          <div>
            <div className="mb-2.5 flex items-end justify-between">
              <Label htmlFor="description">Description</Label>
              <span className="font-mono text-[0.7rem] tabular-nums text-muted-foreground">
                {charCount}
                <span className="text-muted-foreground/60"> / 500</span>
              </span>
            </div>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={5}
              minLength={5}
              maxLength={500}
              required
              placeholder="Black leather backpack with a red zipper. Has a small tear on the left strap. Inside: Moleskine notebook, charging cable, and a paperback."
            />
            <div className="mt-2 h-px overflow-hidden bg-border">
              <div
                className="h-full bg-primary transition-[width] duration-500 ease-ink"
                style={{ width: `${charPct}%` }}
              />
            </div>
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
              <span className="text-foreground">Tip:</span> mention colors,
              materials, brand names, distinctive marks, and what was inside or
              attached. The matcher trades on specifics.
            </p>
          </div>

          {/* PHOTO */}
          <div>
            <Label className="mb-2.5">Photo</Label>
            <div
              onClick={() => fileRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") fileRef.current?.click();
              }}
              className={cn(
                "group relative cursor-pointer overflow-hidden rounded-md",
                "border border-dashed transition-colors duration-200 ease-ink",
                preview
                  ? "border-primary/40 bg-card/60 p-3"
                  : "border-border hover:border-primary/50 hover:bg-accent/50 bg-card/40 p-12"
              )}
            >
              {preview ? (
                <div className="relative">
                  <img
                    src={preview}
                    alt="Preview"
                    className="mx-auto max-h-72 w-full rounded-sm object-contain"
                  />
                  <p className="mt-3 text-center font-mono text-[0.6rem] uppercase tracking-[0.22em] text-muted-foreground">
                    Click to replace
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3 text-center">
                  <div className="rounded-md border border-border bg-card p-3">
                    <ImagePlus className="h-6 w-6 text-primary" strokeWidth={1.5} />
                  </div>
                  <p className="text-base font-semibold text-foreground">
                    Click to upload a photo
                  </p>
                  <p className="text-xs text-muted-foreground">
                    JPEG, PNG, or WebP &middot; up to 5&nbsp;MB
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
              className="hidden"
            />
          </div>

          {/* ERROR */}
          {error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-5 py-3.5">
              <p className="font-mono text-xs uppercase tracking-[0.18em] text-destructive">
                Error
              </p>
              <p className="mt-1 text-sm text-destructive/90">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex flex-col gap-3 border-t border-border bg-card/60 px-7 py-5 sm:flex-row sm:items-center sm:justify-between">
          <p className="flex items-center gap-2 font-mono text-[0.65rem] uppercase tracking-[0.22em] text-muted-foreground">
            <MapPin className="h-3 w-3" strokeWidth={1.75} />
            Filed under your account
          </p>
          <Button type="submit" disabled={submitting} size="lg">
            {submitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting…
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" strokeWidth={2.25} />
                Submit report
                <ArrowRight className="ml-2 h-4 w-4" strokeWidth={2.25} />
              </>
            )}
          </Button>
        </div>
      </form>

      {/* Footnote */}
      <p className="text-center text-sm leading-relaxed text-muted-foreground opacity-0 animate-fade-in-up [animation-delay:400ms]">
        Matching begins the moment you submit. You&rsquo;ll get an in-app
        notification and email the second a likely pair appears.
      </p>
    </div>
  );
}
