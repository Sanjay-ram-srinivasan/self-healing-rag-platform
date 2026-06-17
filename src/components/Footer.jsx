import React from "react";

export default function Footer() {
  return (
    <footer className="border-t border-line bg-ivory px-6 py-5 text-sm text-[#6A4034]">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-2xl font-black text-accent">Self-Healing RAG</p>
          <p className="mt-1 text-xs font-semibold">Built with LangGraph, Groq, ChromaDB, FastAPI, and React</p>
        </div>
        <div className="flex flex-wrap gap-6 text-xs font-semibold">
          <span>Documentation</span>
          <span>API Status</span>
          <span>Privacy Policy</span>
        </div>
      </div>
    </footer>
  );
}
