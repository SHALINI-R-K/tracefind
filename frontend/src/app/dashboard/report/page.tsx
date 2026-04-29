"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, ImageIcon, Loader2 } from "lucide-react";
import { createReport, ReportType } from "@/contexts/reporting/api/reports";
import { fileToResizedDataUri } from "@/shared/lib/image";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Select } from "@/shared/components/ui/select";
import { cn } from "@/shared/lib/utils";

const CATEGORIES = [
  "bag", "wallet", "phone", "laptop", "keys",
  "documents", "clothing", "jewelry", "book", "other",
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
      setError("Please attach a photo");
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

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Report an item</h1>
        <p className="mt-1 text-muted-foreground">
          Describe the item and upload a photo for AI matching.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Item Details</CardTitle>
          <CardDescription>
            Provide as much detail as possible for better matching results.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-6">
            {/* Type toggle */}
            <div className="space-y-2">
              <Label>Type</Label>
              <div className="flex gap-2">
                {(["lost", "found"] as ReportType[]).map((t) => (
                  <Button
                    key={t}
                    type="button"
                    variant={type === t ? "default" : "outline"}
                    className="capitalize flex-1"
                    onClick={() => setType(t)}
                  >
                    {t === "lost" ? "🔍 " : "📦 "}
                    {t}
                  </Button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                minLength={5}
                maxLength={500}
                required
                placeholder="Black leather backpack with a red zipper, contains a notebook and charger"
              />
              <p className="text-xs text-muted-foreground">
                {description.length}/500 characters
              </p>
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

            {/* Photo upload */}
            <div className="space-y-2">
              <Label>Photo</Label>
              <div
                onClick={() => fileRef.current?.click()}
                className={cn(
                  "group cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors hover:border-primary/50 hover:bg-accent/50",
                  preview ? "border-primary/30" : "border-input"
                )}
              >
                {preview ? (
                  <img
                    src={preview}
                    alt="Preview"
                    className="mx-auto max-h-48 rounded-md object-contain"
                  />
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <div className="rounded-lg bg-muted p-3">
                      <ImageIcon className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-muted-foreground/70">
                      JPEG, PNG or WebP (max 5MB)
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
              <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}

            {/* Submit */}
            <Button type="submit" disabled={submitting} className="w-full" size="lg">
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting…
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Submit report
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
