import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "../types";
import { authApi } from "../services/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("sgc_token"));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("sgc_token");
      if (storedToken) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
        } catch (err) {
          console.error("Session restore failed", err);
          localStorage.removeItem("sgc_token");
          localStorage.removeItem("sgc_user");
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    const data = await authApi.login({ email, password });
    localStorage.setItem("sgc_token", data.access_token);
    setToken(data.access_token);

    const currentUser: User = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
      department_id: data.department_id,
      department_code: data.department_code,
      department_name: data.department_name
    };
    localStorage.setItem("sgc_user", JSON.stringify(currentUser));
    setUser(currentUser);
    return currentUser;
  };

  const logout = () => {
    localStorage.removeItem("sgc_token");
    localStorage.removeItem("sgc_user");
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
