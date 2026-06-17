import React from "react";
import { Loader2, LockKeyhole } from "lucide-react";

export default function LoginPage({ onLogin, loading, error }) {
  return (
    <main className="min-h-screen bg-ivory px-5 py-9 text-ink sm:px-7">
      <div className="mx-auto grid min-h-[calc(100vh-72px)] max-w-6xl items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-[28px] border border-line bg-[#FBF6F1] p-8 shadow-soft sm:p-10">
          <div className="mb-4 flex flex-wrap gap-3">
            <span className="rounded-full bg-[#F5DFD2] px-3 py-1 text-xs font-black text-accent">Secure Workspace</span>
            <span className="rounded-full bg-[#F5DFD2] px-3 py-1 text-xs font-black text-accent">Google Authentication</span>
          </div>
          <h1 className="max-w-xl text-4xl font-black tracking-tight sm:text-5xl">Self-Healing RAG Platform</h1>
          <p className="mt-4 max-w-xl text-sm leading-7 text-[#6A4034]">
            Sign in to access your indexed documents, grounded answers, and analytics dashboard in the same workspace design you already use.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <FeatureCard title="Protected Chat" body="Only authenticated users can query the RAG pipeline." />
            <FeatureCard title="Private Uploads" body="Document ingestion and indexing stay behind auth." />
            <FeatureCard title="Secure Analytics" body="Evaluation metrics and dashboards require sign-in." />
          </div>
        </section>

        <section className="rounded-[28px] border border-line bg-paper p-8 shadow-soft sm:p-10">
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[#FFE0D3] text-accent">
            <LockKeyhole size={24} />
          </div>
          <p className="mt-6 text-xs font-black uppercase tracking-[0.18em] text-[#9B7A6E]">Workspace Access</p>
          <h2 className="mt-3 text-3xl font-black">Continue with Google</h2>
          <p className="mt-3 text-sm leading-6 text-muted">
            Use your Google account to access the application securely through Firebase Authentication.
          </p>
          <button
            type="button"
            onClick={onLogin}
            disabled={loading}
            className="mt-8 flex w-full items-center justify-center gap-3 rounded-md bg-accent px-5 py-4 text-sm font-black text-white shadow-soft transition hover:bg-[#A93E00] disabled:opacity-65"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <GoogleMark />}
            {loading ? "Signing you in..." : "Continue with Google"}
          </button>
          {error && <p className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        </section>
      </div>
    </main>
  );
}

function FeatureCard({ title, body }) {
  return (
    <div className="rounded-2xl border border-line bg-[#FFFEFC] p-5">
      <p className="text-sm font-black">{title}</p>
      <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
    </div>
  );
}

function GoogleMark() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden="true">
      <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.9-5.5 3.9-3.3 0-6-2.8-6-6.2s2.7-6.2 6-6.2c1.9 0 3.2.8 3.9 1.5l2.7-2.7C16.9 2.8 14.7 2 12 2 6.9 2 2.8 6.2 2.8 11.4S6.9 20.8 12 20.8c6.9 0 9.1-4.9 9.1-7.4 0-.5 0-.9-.1-1.3H12Z" />
      <path fill="#34A853" d="M2.8 7.3 6 9.6c.9-2 3-3.4 6-3.4 1.9 0 3.2.8 3.9 1.5l2.7-2.7C16.9 2.8 14.7 2 12 2 8 2 4.6 4.3 2.8 7.3Z" />
      <path fill="#FBBC05" d="M12 20.8c2.6 0 4.8-.8 6.4-2.3l-3-2.5c-.8.6-1.9 1-3.4 1-4 0-5.3-2.6-5.5-3.9L3.3 15.6c1.8 3 5.2 5.2 8.7 5.2Z" />
      <path fill="#4285F4" d="M21.1 12.1H12v3.9h5.5c-.3 1.2-1.2 2.2-2.1 2.8l3 2.5c1.8-1.7 2.7-4.1 2.7-7 0-.5 0-.9-.1-1.2Z" />
    </svg>
  );
}
