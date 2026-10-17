import type { MasteryStatus } from "../types";

export default function StatusBadge({ status }: { status: MasteryStatus }) {
  const label = status === "needs_review" ? "Needs review" : status === "demonstrated" ? "Demonstrated" : "Unknown";
  return <span className={`status status-${status}`}><i />{label}</span>;
}
