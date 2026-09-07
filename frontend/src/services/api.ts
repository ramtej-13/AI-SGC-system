import axios from "axios";
import {
  User,
  Grievance,
  AnalyticsData,
  ModelPerformanceData,
  GeneralizationTestResult,
  Department
} from "../types";

const apiBase = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL.replace(/\/$/, "")}/api`
  : "/api";

const api = axios.create({
  baseURL: apiBase,
  headers: {
    "Content-Type": "application/json"
  }
});

// Attach JWT token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sgc_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("sgc_token");
      localStorage.removeItem("sgc_user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (credentials: { email: string; password: string }) => {
    const res = await api.post("/auth/login", credentials);
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get("/auth/me");
    return res.data;
  }
};

export const grievanceApi = {
  submit: async (data: { title: string; description: string }): Promise<Grievance> => {
    const res = await api.post("/grievances", data);
    return res.data;
  },
  getMyGrievances: async (): Promise<Grievance[]> => {
    const res = await api.get("/grievances/my");
    return res.data;
  },
  getById: async (id: number): Promise<Grievance> => {
    const res = await api.get(`/grievances/${id}`);
    return res.data;
  }
};

export const departmentApi = {
  getQueue: async (params?: { status?: string; priority?: string }): Promise<Grievance[]> => {
    const res = await api.get("/department/grievances", { params });
    return res.data;
  },
  updateStatus: async (id: number, data: { status: string; remarks?: string }): Promise<Grievance> => {
    const res = await api.patch(`/grievances/${id}/status`, data);
    return res.data;
  }
};

export const adminApi = {
  getAllGrievances: async (params?: {
    status?: string;
    category?: string;
    department_id?: number;
    priority?: string;
    low_confidence?: boolean;
  }): Promise<Grievance[]> => {
    const res = await api.get("/admin/grievances", { params });
    return res.data;
  },
  getAnalytics: async (): Promise<AnalyticsData> => {
    const res = await api.get("/admin/analytics");
    return res.data;
  },
  getModelPerformance: async (): Promise<ModelPerformanceData> => {
    const res = await api.get("/admin/model-performance");
    return res.data;
  },
  testModel: async (data: { text: string; threshold?: number }): Promise<GeneralizationTestResult> => {
    const res = await api.post("/admin/model-test", data);
    return res.data;
  },
  getLowConfidenceQueue: async (): Promise<Grievance[]> => {
    const res = await api.get("/admin/low-confidence");
    return res.data;
  },
  resolveManualReview: async (
    id: number,
    data: { assigned_category: string; assigned_department_id?: number; review_notes?: string }
  ): Promise<Grievance> => {
    const res = await api.post(`/admin/manual-review/${id}`, data);
    return res.data;
  },
  getDepartments: async (): Promise<Department[]> => {
    const res = await api.get("/departments");
    return res.data;
  }
};

export default api;
