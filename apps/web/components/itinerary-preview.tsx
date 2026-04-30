import { CalendarDays, MapPinned } from "lucide-react";

import { cn } from "@/lib/utils";

export function ItineraryPreview({ className }: { className?: string }) {
  return (
    <aside className={cn("flex-col overflow-hidden rounded-lg border bg-card", className)}>
      <div className="shrink-0 border-b px-5 py-4">
        <p className="text-sm font-semibold">Itinerary Preview</p>
        <p className="mt-1 text-sm text-muted-foreground">Your structured trip plan will appear here in a later feature.</p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-5">
        <div className="flex min-h-full flex-col justify-start gap-4 lg:justify-center">
          <div className="rounded-lg border bg-background p-4">
            <div className="flex items-center gap-3">
              <MapPinned className="h-5 w-5 text-primary" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium">Destination</p>
                <p className="text-sm text-muted-foreground">Waiting for trip details</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border bg-background p-4">
            <div className="flex items-center gap-3">
              <CalendarDays className="h-5 w-5 text-primary" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium">Day-by-day plan</p>
                <p className="text-sm text-muted-foreground">Generated itinerary cards come next</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
