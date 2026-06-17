import React, { useMemo, useRef, useState } from "react";
import { Database, Eye, FileText, Filter, Loader2, MoreVertical, RefreshCw, Search, Trash2, Upload, X } from "lucide-react";
import Footer from "../components/Footer.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { deleteDocument, reindexDocument, uploadDocument, fetchCollections, createCollection, deleteCollection } from "../services/api.js";

const allowedTypes = ".pdf,.docx,.pptx,.xlsx,.csv,.txt";

const formatSize = (doc) => {
  if (doc.size_kb != null && doc.size_kb >= 1024) return `${(doc.size_kb / 1024).toFixed(2)} MB`;
  if (doc.size_kb != null) return `${doc.size_kb} KB`;
  if (!doc.size_bytes) return "0 KB";
  return `${(doc.size_bytes / 1024).toFixed(1)} KB`;
};

export default function DocumentsPage({ documents, loading, error, onRefresh }) {
  const inputRef = useRef(null);
  const [query, setQuery] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [actionError, setActionError] = useState("");
  const [deleting, setDeleting] = useState("");
  const [reindexing, setReindexing] = useState("");
  const [selected, setSelected] = useState([]);
  const [sort, setSort] = useState({ key: "uploaded_at", direction: "desc" });
  const [menuOpen, setMenuOpen] = useState("");
  const [chunkDoc, setChunkDoc] = useState(null);

  const [collections, setCollections] = useState([]);
  const [newCollectionName, setNewCollectionName] = useState("");
  const [selectedUploadCollection, setSelectedUploadCollection] = useState("");

  React.useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const data = await fetchCollections();
      setCollections(data.collections || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateCollection = async (e) => {
    e.preventDefault();
    if (!newCollectionName.trim()) return;
    try {
      await createCollection(newCollectionName.trim());
      setNewCollectionName("");
      loadCollections();
    } catch (err) {
      setActionError(err.response?.data?.detail || "Failed to create collection");
    }
  };

  const handleDeleteCollection = async (id) => {
    try {
      await deleteCollection(id);
      loadCollections();
    } catch (err) {
      setActionError(err.response?.data?.detail || "Failed to delete collection");
    }
  };

  const filteredDocuments = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const visible = needle ? documents.filter((doc) => doc.name?.toLowerCase().includes(needle)) : [...documents];
    return visible.sort((a, b) => {
      const left = a[sort.key] ?? "";
      const right = b[sort.key] ?? "";
      const result = typeof left === "number" && typeof right === "number"
        ? left - right
        : String(left).localeCompare(String(right));
      return sort.direction === "asc" ? result : -result;
    });
  }, [documents, query, sort]);

  const totalChunks = documents.reduce((sum, doc) => sum + Number(doc.chunks || 0), 0);
  const totalMb = documents.reduce((sum, doc) => sum + Number(doc.size_bytes || 0), 0) / (1024 * 1024);

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadProgress(0);
    setActionError("");
    try {
      const result = await uploadDocument(file, selectedUploadCollection || null, (progressEvent) => {
        if (progressEvent.total) {
          setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
        }
      });
      if (result.error) throw new Error(result.error);
      await onRefresh();
    } catch (uploadError) {
      setActionError(uploadError.response?.data?.detail || uploadError.message || "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const handleDelete = async (filename) => {
    setDeleting(filename);
    setActionError("");
    try {
      const result = await deleteDocument(filename);
      if (result.error) throw new Error(result.error);
      await onRefresh();
    } catch (deleteError) {
      setActionError(deleteError.response?.data?.detail || deleteError.message || "Delete failed.");
    } finally {
      setDeleting("");
    }
  };

  const handleReindex = async (filename) => {
    setReindexing(filename);
    setActionError("");
    try {
      const result = await reindexDocument(filename);
      if (result.error) throw new Error(result.error);
      await onRefresh();
    } catch (reindexError) {
      setActionError(reindexError.response?.data?.detail || reindexError.message || "Re-index failed.");
    } finally {
      setReindexing("");
      setMenuOpen("");
    }
  };

  const toggleSort = (key) => {
    setSort((current) => ({
      key,
      direction: current.key === key && current.direction === "asc" ? "desc" : "asc",
    }));
  };

  const toggleSelected = (name) => {
    setSelected((current) => current.includes(name) ? current.filter((item) => item !== name) : [...current, name]);
  };

  const allVisibleSelected = filteredDocuments.length > 0 && filteredDocuments.every((doc) => selected.includes(doc.name));

  return (
    <>
      <main className="px-5 py-9 sm:px-7">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-4xl font-black tracking-tight">Document Library</h1>
              <p className="mt-3 max-w-2xl text-base leading-7 text-[#6A4034]">
                Manage your knowledge base. Documents are parsed, embedded, and stored with self-healing indexing enabled.
              </p>
            </div>
            <input ref={inputRef} type="file" accept={allowedTypes} onChange={handleUpload} className="hidden" />
            <div className="flex items-center gap-3">
              <select 
                value={selectedUploadCollection} 
                onChange={e => setSelectedUploadCollection(e.target.value)}
                className="h-11 rounded-md border border-line bg-paper px-3 text-sm outline-none"
              >
                <option value="">No Collection</option>
                {collections.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                disabled={uploading}
                className="flex h-11 items-center justify-center gap-2 rounded-md bg-accent px-6 text-sm font-black text-white shadow-soft hover:bg-[#A93E00] disabled:opacity-60"
              >
                {uploading ? <Loader2 className="animate-spin" size={17} /> : <Upload size={17} />}
                Upload
              </button>
            </div>
          </div>

          {(actionError || error) && <p className="mt-5 rounded-md bg-red-50 p-3 text-sm text-red-700">{actionError || error}</p>}

          <div className="mt-9 grid gap-6 lg:grid-cols-[340px_minmax(0,1fr)]">
            <aside className="space-y-5">
              <div className="rounded-lg border border-line bg-paper p-7">
                <p className="text-sm font-semibold text-[#6A4034]">Active Sync</p>
                <p className="mt-6 text-sm font-black uppercase text-accent">
                  {uploading ? "Updating Knowledge Base" : "Knowledge Base Ready"}
                </p>
                <p className="mt-2 truncate text-sm font-black">{uploading ? "Indexing uploaded file" : `${documents.length} documents indexed`}</p>
                <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-[#D9CDC4]">
                  <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${uploading ? Math.max(uploadProgress, 8) : 100}%` }} />
                </div>
                <div className="mt-3 flex justify-between text-sm text-[#7A6259]">
                  <span>Index - Store in ChromaDB</span>
                  <span>{uploading ? `${uploadProgress}%` : "100%"}</span>
                </div>
                <div className="mt-7 grid grid-cols-3 gap-2">
                  {["Upload", "Index", "Store"].map((label, index) => (
                    <div key={label} className={`grid h-12 place-items-center text-[11px] font-black uppercase ${index === 1 ? "bg-accent text-white" : "bg-[#FFFEFC] text-muted"}`}>
                      {label}
                    </div>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-lg border border-line bg-paper p-6">
                  <FileText className="text-accent" size={19} />
                  <p className="mt-7 text-3xl font-black">{totalChunks.toLocaleString()}</p>
                  <p className="text-sm text-[#6A4034]">Total Chunks</p>
                </div>
                <div className="rounded-lg border border-line bg-paper p-6">
                  <Database className="text-accent" size={19} />
                  <p className="mt-7 text-3xl font-black">{totalMb.toFixed(1)}MB</p>
                  <p className="text-sm text-[#6A4034]">Vector Store</p>
                </div>
              </div>

              {/* Collections Management UI */}
              <div className="rounded-lg border border-line bg-paper p-6">
                <p className="text-sm font-black mb-4">Collections</p>
                <form onSubmit={handleCreateCollection} className="flex gap-2 mb-4">
                  <input 
                    value={newCollectionName} 
                    onChange={e => setNewCollectionName(e.target.value)} 
                    placeholder="New collection..." 
                    className="flex-1 rounded-md border border-line bg-[#FFFEFC] px-3 py-2 text-sm outline-none" 
                  />
                  <button type="submit" className="rounded-md bg-[#D9C7BC] px-3 py-2 text-xs font-black text-[#6A4034] hover:bg-[#C8B4A8] transition">Add</button>
                </form>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {collections.map(col => (
                    <div key={col.id} className="flex items-center justify-between bg-[#FFFEFC] border border-line rounded p-2">
                      <span className="text-sm font-semibold truncate pr-2">{col.name}</span>
                      <button type="button" onClick={() => handleDeleteCollection(col.id)} className="text-[#A18478] hover:text-red-600 transition" aria-label="Delete collection">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                  {collections.length === 0 && <p className="text-xs text-muted text-center py-2">No collections yet.</p>}
                </div>
              </div>
            </aside>

            <section className="overflow-hidden rounded-lg border border-line bg-[#FFFEFC] shadow-soft">
              <div className="flex flex-col gap-4 border-b border-line bg-[#FFFEFC] p-5 sm:flex-row sm:items-center sm:justify-between">
                <label className="field flex h-11 w-full items-center gap-3 px-3 sm:max-w-sm">
                  <Search size={17} className="text-muted" />
                  <input value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 bg-transparent text-sm outline-none" placeholder="Search files..." />
                </label>
                <button type="button" className="flex items-center gap-2 text-sm font-semibold text-muted">
                  <Filter size={16} />
                  Filter
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-left">
                  <thead className="bg-paper text-xs font-black uppercase text-[#6F5A52]">
                    <tr>
                      <th className="px-4 py-4">
                        <input
                          type="checkbox"
                          checked={allVisibleSelected}
                          onChange={() => setSelected(allVisibleSelected ? [] : filteredDocuments.map((doc) => doc.name))}
                          aria-label="Select all documents"
                        />
                      </th>
                      <SortableHeader label="Filename" sortKey="name" sort={sort} onSort={toggleSort} />
                      <SortableHeader label="Size" sortKey="size_bytes" sort={sort} onSort={toggleSort} />
                      <th className="px-6 py-4" title="Chunk size: 512 tokens. Overlap: 50 tokens. Embedding model: sentence-transformers.">Chunks</th>
                      <th className="px-6 py-4">Status</th>
                      <SortableHeader label="Upload Date" sortKey="uploaded_at" sort={sort} onSort={toggleSort} />
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading && (
                      <tr><td colSpan="7" className="px-6 py-10 text-center text-sm text-muted">Loading documents...</td></tr>
                    )}
                    {!loading && filteredDocuments.length === 0 && (
                      <tr><td colSpan="7" className="px-6 py-10 text-center text-sm text-muted">No documents found.</td></tr>
                    )}
                    {filteredDocuments.map((doc) => (
                      <tr key={doc.name} className="border-t border-line bg-[#F6F1EB]">
                        <td className="px-4 py-5">
                          <input
                            type="checkbox"
                            checked={selected.includes(doc.name)}
                            onChange={() => toggleSelected(doc.name)}
                            aria-label={`Select ${doc.name}`}
                          />
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-3">
                            <FileText className="text-accent" size={18} />
                            <div className="min-w-0">
                              <p className="truncate text-sm font-black">{doc.name}</p>
                              <p className="text-xs text-muted">{doc.pages || 0} pages</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-5 text-sm font-semibold">{formatSize(doc)}</td>
                        <td className="px-6 py-5 text-sm font-semibold">{doc.chunks || 0}</td>
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-2">
                            <StatusPill status="indexed">Indexed</StatusPill>
                            {doc.ocr_used && <span className="rounded bg-indigo-50 px-2 py-1 text-[10px] font-black text-indigo-700">OCR</span>}
                          </div>
                        </td>
                        <td className="px-6 py-5 text-sm text-muted">{doc.uploaded_at || "Pending"}</td>
                        <td className="px-6 py-5">
                          <div className="relative flex justify-end">
                            <button type="button" onClick={() => setMenuOpen(menuOpen === doc.name ? "" : doc.name)} className="icon-button" aria-label={`Actions for ${doc.name}`}>
                              {deleting === doc.name || reindexing === doc.name ? <Loader2 className="animate-spin" size={17} /> : <MoreVertical size={17} />}
                            </button>
                            {menuOpen === doc.name && (
                              <div className="absolute right-0 top-10 z-20 w-44 rounded-md border border-line bg-[#FFFEFC] p-1 text-sm shadow-soft">
                                <button type="button" onClick={() => setChunkDoc(doc)} className="flex w-full items-center gap-2 rounded px-3 py-2 text-left hover:bg-paper">
                                  <Eye size={15} /> View Chunks
                                </button>
                                <button type="button" onClick={() => handleReindex(doc.name)} className="flex w-full items-center gap-2 rounded px-3 py-2 text-left hover:bg-paper">
                                  <RefreshCw size={15} /> Re-index
                                </button>
                                <button type="button" onClick={() => handleDelete(doc.name)} className="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-red-700 hover:bg-red-50">
                                  <Trash2 size={15} /> Delete
                                </button>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="border-t border-line px-6 py-4 text-sm text-muted">
                Showing {filteredDocuments.length} of {documents.length} documents
                {selected.length > 0 && <span className="ml-3 font-black text-accent">{selected.length} selected</span>}
              </div>
            </section>
          </div>
        </div>
      </main>
      {chunkDoc && (
        <div className="fixed inset-0 z-40 grid place-items-center bg-black/25 p-4">
          <div className="w-full max-w-lg rounded-lg bg-[#FFFEFC] p-6 shadow-soft">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-black">Chunk Metadata</h2>
                <p className="mt-1 text-sm text-muted">{chunkDoc.name}</p>
              </div>
              <button type="button" onClick={() => setChunkDoc(null)} className="icon-button" aria-label="Close chunks modal">
                <X size={18} />
              </button>
            </div>
            <div className="mt-6 grid gap-3 text-sm">
              <InfoRow label="Chunks" value={chunkDoc.chunks || 0} />
              <InfoRow label="Pages" value={chunkDoc.pages || 0} />
              <InfoRow label="Chunk Size" value="512 tokens" />
              <InfoRow label="Overlap" value="50 tokens" />
              <InfoRow label="Embedding Model" value="sentence-transformers" />
            </div>
          </div>
        </div>
      )}
      <Footer />
    </>
  );
}

function SortableHeader({ label, sortKey, sort, onSort }) {
  return (
    <th className="px-6 py-4">
      <button type="button" onClick={() => onSort(sortKey)} className="font-black uppercase">
        {label} {sort.key === sortKey ? (sort.direction === "asc" ? "ASC" : "DESC") : ""}
      </button>
    </th>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between border-b border-line pb-2">
      <span className="font-semibold text-muted">{label}</span>
      <span className="font-black">{value}</span>
    </div>
  );
}
