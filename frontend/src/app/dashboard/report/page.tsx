"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Upload,
  ImagePlus,
  Loader2,
  ChevronLeft,
  AlertCircle,
  X,
  MapPin,
  Calendar,
} from "lucide-react";
import { createReport, ReportType } from "@/contexts/reporting/api/reports";
import { fileToResizedDataUri } from "@/shared/lib/image";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Combobox } from "@/shared/components/ui/combobox";
import { DateTimePicker } from "@/shared/components/ui/date-time-picker";
import { cn } from "@/shared/lib/utils";

const CATEGORIES = [
  { value: "accessory", label: "Accessory (small item)" },
  { value: "backpack", label: "Backpack" },
  { value: "bag", label: "Bag" },
  { value: "book", label: "Book" },
  { value: "bottle", label: "Bottle" },
  { value: "camera", label: "Camera" },
  { value: "card", label: "Card / ID" },
  { value: "charger", label: "Charger / cable" },
  { value: "clothing", label: "Clothing" },
  { value: "documents", label: "Documents" },
  { value: "earphones", label: "Earphones / earbuds" },
  { value: "glasses", label: "Glasses / sunglasses" },
  { value: "headphones", label: "Headphones" },
  { value: "jacket", label: "Jacket / coat" },
  { value: "jewelry", label: "Jewelry" },
  { value: "keys", label: "Keys" },
  { value: "laptop", label: "Laptop" },
  { value: "pen", label: "Pen / stationery" },
  { value: "phone", label: "Phone" },
  { value: "shoes", label: "Shoes" },
  { value: "tablet", label: "Tablet" },
  { value: "umbrella", label: "Umbrella" },
  { value: "wallet", label: "Wallet" },
  { value: "watch", label: "Watch" },
  { value: "other", label: "Other" },
];

const MAX_PHOTOS = 3;
const MAX_BYTES = 5 * 1024 * 1024;

interface PhotoSlot {
  file: File;
  preview: string;
}

export default function ReportPage() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [type, setType] = useState<ReportType>("lost");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("other");
  const [location, setLocation] = useState("");
  const [incidentAt, setIncidentAt] = useState(""); // datetime-local string
  const [photos, setPhotos] = useState<PhotoSlot[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const addFiles = useCallback(async (files: FileList | File[] | null) => {
    if (!files) return;
    const accepted = Array.from(files).filter((f) =>
      ["image/jpeg", "image/png", "image/webp"].includes(f.type)
    );
    if (accepted.length === 0) {
      setError("Only JPEG, PNG, or WebP images are accepted.");
      return;
    }
    const tooBig = accepted.find((f) => f.size > MAX_BYTES);
    if (tooBig) {
      setError(`"${tooBig.name}" exceeds the 5 MB limit.`);
      return;
    }
    setError(null);
    const slots: PhotoSlot[] = await Promise.all(
      accepted.map(
        (file) =>
          new Promise<PhotoSlot>((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve({ file, preview: reader.result as string });
            reader.readAsDataURL(file);
          })
      )
    );
    setPhotos((prev) => [...prev, ...slots].slice(0, MAX_PHOTOS));
  }, []);

  const removePhoto = (idx: number) => {
    setPhotos((prev) => prev.filter((_, i) => i !== idx));
  };

  // Drag-and-drop handlers
  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (photos.length < MAX_PHOTOS) setIsDragging(true);
  }, [photos.length]);
  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);
  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      void addFiles(e.dataTransfer.files);
    },
    [addFiles]
  );

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (photos.length === 0) {
      setError("Please attach at least one photo.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      // Resize each photo client-side before sending
      const images = await Promise.all(
        photos.map((p) => fileToResizedDataUri(p.file))
      );
      const incidentISO = incidentAt
        ? new Date(incidentAt).toISOString()
        : undefined;
      const report = await createReport({
        type,
        description,
        category,
        images,
        location: location.trim() || undefined,
        incident_at: incidentISO,
      });
      router.push(`/dashboard/items/${report.id}`);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  const charCount = description.length;
  const charPct = Math.min((charCount / 500) * 100, 100);
  const canAddMorePhotos = photos.length < MAX_PHOTOS;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
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
          Describe the item, attach 1–{MAX_PHOTOS} photos, and tell us where
          and when. Specifics make matches faster and more accurate.
        </p>
      </div>

      <form onSubmit={onSubmit}>
        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold">Item details</CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Type */}
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
              <Combobox
                id="category"
                value={category}
                onChange={setCategory}
                options={CATEGORIES}
                searchable
                placeholder="Pick a category"
              />
            </div>

            {/* Location + Incident time — two-column on wider screens */}
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="location" className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5 text-muted-foreground" strokeWidth={1.75} />
                  {type === "lost" ? "Where you lost it" : "Where you found it"}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  maxLength={200}
                  placeholder="A-block 210 cafeteria"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="incident-at" className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" strokeWidth={1.75} />
                  {type === "lost" ? "When you lost it" : "When you found it"}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <DateTimePicker
                  id="incident-at"
                  value={incidentAt}
                  onChange={setIncidentAt}
                  max={new Date()}
                  placeholder={
                    type === "lost" ? "When did you last have it?" : "When did you find it?"
                  }
                />
              </div>
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
              </p>
            </div>

            {/* Photos — drag-drop, up to 3 */}
            <div className="space-y-2">
              <div className="flex items-end justify-between">
                <Label>
                  Photos
                  <span className="ml-1.5 text-muted-foreground">
                    ({photos.length} / {MAX_PHOTOS})
                  </span>
                </Label>
                {photos.length > 0 && canAddMorePhotos && (
                  <button
                    type="button"
                    onClick={() => fileRef.current?.click()}
                    className="text-xs text-primary hover:underline"
                  >
                    Add another
                  </button>
                )}
              </div>

              {/* Existing photo grid */}
              {photos.length > 0 && (
                <div className="grid grid-cols-3 gap-2">
                  {photos.map((p, i) => (
                    <div
                      key={i}
                      className="group relative aspect-square overflow-hidden rounded-md border border-border bg-card/40"
                    >
                      <img
                        src={p.preview}
                        alt={`Photo ${i + 1}`}
                        className="h-full w-full object-cover"
                      />
                      <button
                        type="button"
                        onClick={() => removePhoto(i)}
                        className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-md bg-background/90 text-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:bg-destructive hover:text-destructive-foreground"
                        aria-label={`Remove photo ${i + 1}`}
                      >
                        <X className="h-3.5 w-3.5" strokeWidth={2} />
                      </button>
                      {i === 0 && (
                        <span className="absolute bottom-1.5 left-1.5 rounded-sm bg-primary px-1.5 py-0.5 text-[0.65rem] font-medium text-primary-foreground">
                          Primary
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Dropzone — only if we have room for more */}
              {canAddMorePhotos && (
                <div
                  onClick={() => fileRef.current?.click()}
                  onDragOver={onDragOver}
                  onDragLeave={onDragLeave}
                  onDrop={onDrop}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") fileRef.current?.click();
                  }}
                  className={cn(
                    "group relative cursor-pointer overflow-hidden rounded-md border border-dashed",
                    "transition-colors duration-150",
                    isDragging
                      ? "border-primary bg-primary/10"
                      : "border-border bg-card/40 hover:border-primary/50 hover:bg-accent/30",
                    "p-8"
                  )}
                >
                  <div className="flex flex-col items-center gap-2 text-center">
                    <div className="rounded-md border border-border bg-card p-2.5">
                      <ImagePlus className="h-5 w-5 text-primary" strokeWidth={1.75} />
                    </div>
                    <p className="text-sm font-medium">
                      {isDragging
                        ? "Drop to add"
                        : photos.length === 0
                        ? "Click or drag photos here"
                        : "Add another photo"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      JPEG, PNG, or WebP &middot; up to 5&nbsp;MB each &middot; up to{" "}
                      {MAX_PHOTOS - photos.length} more
                    </p>
                  </div>
                </div>
              )}

              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                multiple
                onChange={(e) => {
                  void addFiles(e.target.files);
                  // Reset input so the same file can be re-picked if removed
                  e.target.value = "";
                }}
                className="hidden"
              />

              {photos.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  Tip: a primary photo plus angles (back, label, distinguishing
                  marks) helps the matcher catch lookalikes.
                </p>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2.5 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5">
                <AlertCircle
                  className="mt-0.5 h-4 w-4 shrink-0 text-destructive"
                  strokeWidth={2}
                />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </CardContent>

          <CardFooter className="border-t border-border bg-card/40 px-6 pt-4">
            <Button
              type="submit"
              disabled={submitting || photos.length === 0}
              className="ml-auto"
            >
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
