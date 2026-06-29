import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { onIdTokenChanged, signInWithPopup, signOut } from "firebase/auth";
import { firebaseAuth, googleProvider } from "../lib/firebase.js";
import { setApiAuthToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!firebaseAuth) {
      setLoading(false);
      setError("Firebase Authentication is not configured. Please set VITE_FIREBASE_API_KEY, VITE_FIREBASE_PROJECT_ID, and VITE_FIREBASE_AUTH_DOMAIN in your Vercel deployment variables.");
      return undefined;
    }

    const unsubscribe = onIdTokenChanged(firebaseAuth, async (nextUser) => {
      if (!nextUser) {
        setUser(null);
        setToken("");
        setApiAuthToken("");
        setLoading(false);
        return;
      }

      try {
        const idToken = await nextUser.getIdToken();

        setToken(idToken);
        setApiAuthToken(idToken);

        setUser({
          uid: nextUser.uid,
          name: nextUser.displayName || "",
          email: nextUser.email || "",
          profile_picture: nextUser.photoURL || "",
        });

        setError("");
      } catch (authError) {
        setError(authError.message || "Unable to load your session.");
      } finally {
        setLoading(false);
      }
    });

    return unsubscribe;
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      error,
      isAuthenticated: Boolean(user && token),

      async loginWithGoogle() {
        if (!firebaseAuth || !googleProvider) {
          setError("Google Sign-In is unavailable because Firebase is not configured.");
          return;
        }
        setError("");
        setLoading(true);

        try {
          await signInWithPopup(firebaseAuth, googleProvider);
        } catch (authError) {
          setError(authError.message || "Google sign-in failed.");
          setLoading(false);
        }
      },

      async logout() {
        if (!firebaseAuth) {
          setUser(null);
          setToken("");
          setApiAuthToken("");
          return;
        }
        setLoading(true);

        try {
          await signOut(firebaseAuth);

          setUser(null);
          setToken("");
          setApiAuthToken("");
        } finally {
          setLoading(false);
        }
      },
    }),
    [user, token, loading, error]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}