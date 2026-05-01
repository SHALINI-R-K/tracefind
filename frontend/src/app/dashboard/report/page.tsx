"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Upload, ImagePlus, Loader2, ChevronLeft, AlertCircle } from "lucide-react";
import { createReport, ReportType } from "@/contexts/reporting/api/reports";
import { fileToResizedDataUri } from "@/shared/lib/image";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
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
      setError("Please attach a photo.");
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
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Breadcrumb + heading */}
      <div>
        <Link
          href="/dashboard"
          className="inline-flex items-center text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="h-3.5 w-3.5" strokeWidth={2} />
          Back to dashboard
        </Link>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">New report</h1>
        <p className="text-sm text-muted-foreground">
          Describe the item and attach a photo. The matcher reads both your text and the image.
        </p>
      </div>

      {/* Form card */}
      <form onSubmit={onSubmit}>
        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold">Item details</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Type toggle */}
            <div className="space-y-2">
              <Label>Report type</Label>
              <div className="grid grid-cols-2 overflow-hidden rounded-md border border-border">
                {(["lost", "found"] as ReportType[]).map((t, idx) => {
                  const active = type === t;
                  return (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setType(t)}
                      className={cn(
                        "flex flex-col items-start gap-0.5 px-4 py-3 text-left",
                        "transition-colors duration-150",
                        idx === 0 ? "border-r border-border" : "",
                        active
                          ? t === "lost"
                            ? "bg-status-lost/15 ring-1 ring-status-lost/40 -m-px"
                            : "bg-status-found/15 ring-1 ring-status-found/40 -m-px"
                          : "bg-card hover:bg-accent"
                      )}
                    >
                      <span
                        className={cn(
                          "text-xs",
                          active
                            ? t === "lost"
                              ? "text-status-lost"
                              : "text-status-found"
                            : "text-muted-foreground"
                        )}
                      >
                        {t === "lost" ? "Lost" : "Found"}
                      </span>
                      <span className="text-sm font-medium">
                        {t === "lost" ? "I lost something" : "I found something"}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
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

            {/* Description */}
            <div className="space-y-2">
              <div className="flex items-end justify-between">
                <Label htmlFor="description">Description</Label>
                <span className="text-xs tabular-nums text-muted-foreground">
                  {charCount} / 500
                </span>
              </div>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                minLength={5}
                maxLength={500}
                required
                placeholder="Black leather backpack with a red zipper. Small tear on the left strap. Inside: Moleskine notebook, charging cable."
              />
              <div className="h-px overflow-hidden bg-border">
                <div
                  className="h-full bg-primary transition-[width] duration-300 ease-ink"
                  style={{ width: `${charPct}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Mention colors, materials, brands, distinctive marks, and contents.
                Specifics improve match accuracy.
              </p>
            </div>

            {/* Photo */}
            <div className="space-y-2">
              <Label>Photo</Label>
              <div
                onClick={() => fileRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") fileRef.current?.click();
                }}
                className={cn(
                  "group relative cursor-pointer overflow-hidden rounded-md",
                  "border border-dashed transition-colors duration-150",
                  preview
                    ? "border-primary/40 bg-card/40 p-3"
                    : "border-border bg-card/40 hover:border-primary/50 hover:bg-accent/30 p-8"
                )}
              >
                {preview ? (
                  <div>
                    <img
                      src={preview}
                      alt="Preview"
                      className="mx-auto max-h-60 w-full rounded-sm object-contain"
                    />
                    <p className="mt-2 text-center text-xs text-muted-foreground">
                      Click to replace
                    </p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2 text-center">
                    <div className="rounded-md border border-border bg-card p-2.5">
                      <ImagePlus className="h-5 w-5 text-primary" strokeWidth={1.75} />
                    </div>
                    <p className="text-sm font-medium">Click to upload a photo</p>
                    <p className="text-xs text-muted-foreground">
                      JPEG, PNG or WebP &middot; up to 5&nbsp;MB
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

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2.5 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5">
                <AlertCircle className="h-4 w-4 shrink-0 text-destructive mt-0.5" strokeWidth={2} />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </CardContent>

          <CardFooter className="border-t border-border bg-card/40 px-6 pt-4">
            <Button type="submit" disabled={submitting} className="ml-auto">
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting…
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" strokeWidth={2.25} />
                  Submit report
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  );
}
