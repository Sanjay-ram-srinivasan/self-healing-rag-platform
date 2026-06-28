import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach token to every request
apiClient.interceptors.request.use(
  async (config) => {
    // If a token has been set globally, attach it
    const token = getApiAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // Try to refresh the Firebase token if available
      try {
        const { firebaseAuth } = await import("../lib/firebase.js");
        if (firebaseAuth.currentUser) {
          const newToken = await firebaseAuth.currentUser.getIdToken(true);
          setApiAuthToken(newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
      }
    }

    // Normalize error message for UI consumption
    if (error.response?.data?.detail) {
      error.message = error.response.data.detail;
    } else if (error.response?.status === 401) {
      error.message = "Authentication required. Please sign in again.";
    } else if (error.response?.status === 403) {
      error.message = "You do not have permission to access this resource.";
    } else if (error.code === "ERR_NETWORK") {
      error.message = "Network error. Please verify that the backend is running and CORS is allowed.";
    }

    return Promise.reject(error);
  }
);

let _authToken = "";

export function setApiAuthToken(token) {
  _authToken = token;
  apiClient.defaults.headers.common.Authorization = token ? `Bearer ${token}` : undefined;
}

export function getApiAuthToken() {
  return _authToken;
}

// Documents
export const fetchDocuments = async () => {
  const { data } = await apiClient.get("/api/documents");
  return data;
};

export const uploadDocument = async (file, collectionId = null, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  if (collectionId) {
    formData.append("collection_id", collectionId);
  }
  const { data } = await apiClient.post("/api/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: onProgress,
  });
  return data;
};

export const deleteDocument = async (filename) => {
  const { data } = await apiClient.delete(`/api/documents/${encodeURIComponent(filename)}`);
  return data;
};

export const reindexDocument = async (filename) => {
  const { data } = await apiClient.post(`/api/documents/${encodeURIComponent(filename)}/reindex`);
  return data;
};

// Collections
export const fetchCollections = async () => {
  const { data } = await apiClient.get("/api/collections");
  return data;
};

export const createCollection = async (name) => {
  const { data } = await apiClient.post("/api/collections", { name });
  return data;
};

export const deleteCollection = async (id) => {
  const { data } = await apiClient.delete(`/api/collections/${encodeURIComponent(id)}`);
  return data;
};

// Chats
export const fetchChats = async () => {
  const { data } = await apiClient.get("/api/chats");
  return data;
};

export const searchChats = async (query) => {
  const { data } = await apiClient.get(`/api/chats/search`, { params: { query } });
  return data;
};

export const createChat = async (title, collectionId = null) => {
  const { data } = await apiClient.post("/api/chats", { title, collection_id: collectionId });
  return data;
};

export const fetchChat = async (chatId) => {
  const { data } = await apiClient.get(`/api/chats/${encodeURIComponent(chatId)}`);
  return data;
};

export const deleteChat = async (chatId) => {
  const { data } = await apiClient.delete(`/api/chats/${encodeURIComponent(chatId)}`);
  return data;
};

export const updateChat = async (chatId, payload) => {
  const { data } = await apiClient.put(`/api/chats/${encodeURIComponent(chatId)}`, payload);
  return data;
};

// Ask
export const askQuestion = async (payload) => {
  const { data } = await apiClient.post("/api/chat", payload);
  return data;
};

// Analytics
export const fetchAnalytics = async (range, startDate, endDate) => {
  const params = { range };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  const { data } = await apiClient.get("/api/analytics", { params });
  return data;
};

export const streamLogsUrl = `/api/logs/stream`;

// Settings
export const fetchSettings = async () => {
  const { data } = await apiClient.get("/api/settings");
  return data;
};

export const updateSettings = async (settings) => {
  const { data } = await apiClient.post("/api/settings", { settings });
  return data;
};
