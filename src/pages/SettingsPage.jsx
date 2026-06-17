import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { fetchSettings, updateSettings } from "../services/api.js";
import {
  User,
  LogOut,
  BrainCircuit,
  Sliders,
  Database,
  BarChart,
  Shield,
  Save,
  Loader2,
  Trash2,
  Download
} from "lucide-react";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  
  const [settings, setSettings] = useState({
    selfHealingMode: true,
    confidenceThreshold: 50,
    maxRetryAttempts: 3,
    showSources: true,
    topKRetrieval: 5,
    similarityThreshold: 0.5,
    queryRewrite: true,
    criticAgent: true,
    verificationAgent: true,
    defaultCollection: "all",
    autoIndex: true,
    ocrEnabled: false,
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const data = await fetchSettings();
        if (data) setSettings(data);
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMessage("");
    try {
      await updateSettings(settings);
      setSaveMessage("Settings saved successfully.");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (err) {
      console.error(err);
      setSaveMessage("Failed to save settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="grid min-h-[calc(100vh-49px)] place-items-center">
        <Loader2 className="animate-spin text-accent" size={32} />
      </div>
    );
  }

  return (
    <main className="max-w-4xl mx-auto px-5 py-8 sm:py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-black text-ink">Settings</h1>
          <p className="text-sm text-muted mt-2">Manage your AI pipeline, retrieval strategies, and account.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 rounded-md bg-accent px-5 py-2.5 text-sm font-black text-white shadow-soft transition hover:bg-[#A93E00] disabled:opacity-65"
        >
          {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
          Save Changes
        </button>
      </div>

      {saveMessage && (
        <div className={`mb-6 p-3 rounded-md text-sm font-bold ${saveMessage.includes("Failed") ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"}`}>
          {saveMessage}
        </div>
      )}

      <div className="grid gap-8 sm:grid-cols-2">
        {/* Profile Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <User size={18} /> Profile Settings
          </div>
          <div className="p-5 flex items-start justify-between">
            <div className="flex items-center gap-4">
               {user?.profile_picture ? (
                  <img src={user.profile_picture} alt="Profile" className="h-14 w-14 rounded-full object-cover shrink-0 border-2 border-accent" />
               ) : (
                  <div className="grid h-14 w-14 place-items-center rounded-full bg-[#FFE0D3] text-xl font-black text-accent shrink-0">
                    {(user?.name || "U").slice(0, 1).toUpperCase()}
                  </div>
               )}
               <div>
                 <p className="text-lg font-black text-ink">{user?.name || "Authenticated User"}</p>
                 <p className="text-sm font-semibold text-muted">{user?.email || ""}</p>
               </div>
            </div>
            <button onClick={logout} className="p-2 text-muted hover:text-red-600 transition bg-paper rounded-md border border-line hover:border-red-200">
               <LogOut size={20} />
            </button>
          </div>
        </section>

        {/* AI Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <BrainCircuit size={18} /> AI Settings
          </div>
          <div className="p-5 space-y-5">
            <label className="flex items-center justify-between cursor-pointer">
               <div>
                  <p className="text-sm font-bold text-ink">Self-Healing Mode</p>
                  <p className="text-xs text-muted mt-1">Automatically fix ungrounded hallucinations.</p>
               </div>
               <input type="checkbox" checked={settings.selfHealingMode} onChange={e => handleChange("selfHealingMode", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
            </label>
            
            <div>
              <div className="flex justify-between mb-2">
                 <p className="text-sm font-bold text-ink">Confidence Threshold</p>
                 <p className="text-xs font-black text-accent">{settings.confidenceThreshold}%</p>
              </div>
              <input type="range" min="50" max="95" value={settings.confidenceThreshold} onChange={e => handleChange("confidenceThreshold", Number(e.target.value))} className="w-full accent-accent" />
            </div>

            <div className="flex items-center justify-between">
               <p className="text-sm font-bold text-ink">Max Retry Attempts</p>
               <select value={settings.maxRetryAttempts} onChange={e => handleChange("maxRetryAttempts", Number(e.target.value))} className="border border-line rounded-md p-1.5 text-sm bg-paper font-bold outline-none">
                 {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
               </select>
            </div>

            <label className="flex items-center justify-between cursor-pointer">
               <p className="text-sm font-bold text-ink">Show Sources</p>
               <input type="checkbox" checked={settings.showSources} onChange={e => handleChange("showSources", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
            </label>
          </div>
        </section>

        {/* Retrieval Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <Sliders size={18} /> Retrieval Settings
          </div>
          <div className="p-5 space-y-5">
             <div className="flex items-center justify-between">
               <p className="text-sm font-bold text-ink">Top-K Retrieval</p>
               <select value={settings.topKRetrieval} onChange={e => handleChange("topKRetrieval", Number(e.target.value))} className="border border-line rounded-md p-1.5 text-sm bg-paper font-bold outline-none">
                 <option value={3}>3 Documents</option>
                 <option value={5}>5 Documents</option>
                 <option value={10}>10 Documents</option>
               </select>
             </div>
             
             <div>
               <div className="flex justify-between mb-2">
                  <p className="text-sm font-bold text-ink">Similarity Threshold</p>
                  <p className="text-xs font-black text-accent">{settings.similarityThreshold}</p>
               </div>
               <input type="range" min="0" max="1" step="0.1" value={settings.similarityThreshold} onChange={e => handleChange("similarityThreshold", Number(e.target.value))} className="w-full accent-accent" />
             </div>

             <label className="flex items-center justify-between cursor-pointer">
               <p className="text-sm font-bold text-ink">Query Rewrite Agent</p>
               <input type="checkbox" checked={settings.queryRewrite} onChange={e => handleChange("queryRewrite", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
             </label>

             <label className="flex items-center justify-between cursor-pointer">
               <p className="text-sm font-bold text-ink">Critic Agent</p>
               <input type="checkbox" checked={settings.criticAgent} onChange={e => handleChange("criticAgent", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
             </label>

             <label className="flex items-center justify-between cursor-pointer">
               <p className="text-sm font-bold text-ink">Verification Agent</p>
               <input type="checkbox" checked={settings.verificationAgent} onChange={e => handleChange("verificationAgent", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
             </label>
          </div>
        </section>

        {/* Document Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <Database size={18} /> Document Settings
          </div>
          <div className="p-5 space-y-5">
             <label className="flex items-center justify-between cursor-pointer">
               <p className="text-sm font-bold text-ink">Auto Index Documents</p>
               <input type="checkbox" checked={settings.autoIndex} onChange={e => handleChange("autoIndex", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
             </label>

             <label className="flex items-center justify-between cursor-pointer">
               <div>
                 <p className="text-sm font-bold text-ink">OCR Support</p>
                 <p className="text-xs text-muted mt-1">Extract text from images & scanned PDFs.</p>
               </div>
               <input type="checkbox" checked={settings.ocrEnabled} onChange={e => handleChange("ocrEnabled", e.target.checked)} className="accent-accent w-5 h-5 cursor-pointer" />
             </label>

             <div className="pt-4 border-t border-line">
                <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-md border border-red-200 bg-red-50 text-red-600 text-sm font-bold hover:bg-red-100 transition">
                   <Trash2 size={16} /> Delete All Documents
                </button>
             </div>
          </div>
        </section>

        {/* Analytics Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <BarChart size={18} /> Analytics Settings
          </div>
          <div className="p-5 space-y-4">
             <button className="flex items-center justify-between w-full p-3 rounded-md border border-line bg-paper hover:border-accent hover:text-accent transition text-sm font-bold text-ink">
                Export Analytics JSON <Download size={16} />
             </button>
             <button className="flex items-center justify-between w-full p-3 rounded-md border border-line bg-paper hover:border-accent hover:text-accent transition text-sm font-bold text-ink">
                View Evaluation Metrics <BarChart size={16} />
             </button>
             <button className="flex items-center justify-between w-full p-3 rounded-md border border-red-200 bg-red-50 text-red-600 hover:bg-red-100 transition text-sm font-bold">
                Reset Analytics History <Trash2 size={16} />
             </button>
          </div>
        </section>

        {/* Account Settings */}
        <section className="rounded-xl border border-line bg-[#FFFEFC] shadow-soft overflow-hidden">
          <div className="flex items-center gap-2 border-b border-line bg-paper px-5 py-4 font-black uppercase tracking-wider text-accent text-sm">
            <Shield size={18} /> Account Settings
          </div>
          <div className="p-5 space-y-4">
             <div className="p-3 bg-paper border border-line rounded-md text-xs">
                <p className="font-bold text-ink uppercase tracking-wider mb-2">Google Account Info</p>
                <p className="text-muted"><span className="font-bold">UID:</span> {user?.uid}</p>
                <p className="text-muted"><span className="font-bold">Auth:</span> OAuth 2.0</p>
             </div>
             
             <div className="p-3 bg-paper border border-line rounded-md text-xs">
                <p className="font-bold text-ink uppercase tracking-wider mb-2">Login History</p>
                <p className="text-muted text-xs">Current Session: {new Date().toLocaleString()}</p>
                <p className="text-muted text-xs mt-1">Status: Active & Verified</p>
             </div>

             <div className="pt-2">
                <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-md bg-red-600 text-white text-sm font-bold hover:bg-red-700 shadow-soft transition">
                   Delete Account
                </button>
             </div>
          </div>
        </section>

      </div>
    </main>
  );
}
