import React from "react";
import { CheckCircle2, Clock, ShieldCheck, XCircle } from "lucide-react";

const variants = {
  verified: "bg-green-50 text-green-700",
  indexed: "bg-[#F5E1D4] text-accent",
  processing: "bg-[#ECE8E4] text-muted",
  error: "bg-red-50 text-red-700",
};

export default function StatusPill({ status = "processing", children }) {
  const normalized = String(status).toLowerCase();
  const Icon = normalized.includes("verified")
    ? ShieldCheck
    : normalized.includes("indexed")
      ? CheckCircle2
      : normalized.includes("error")
        ? XCircle
        : Clock;

  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${variants[normalized] || variants.processing}`}>
      <Icon size={13} />
      {children || status}
    </span>
  );
}
