const DEFAULT_API_BASE = "/api";

export const API_BASE_URL = normalizeApiBase(import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE);
export const ANALYSIS_API_PATH = apiPath("/analyze-full");
export const HISTORY_API_PATH = apiPath("/history/my-analyses-full");
export const HISTORY_DOWNLOAD_PATH = apiPath("/history/download");

function normalizeApiBase(value) {
  const raw = String(value || DEFAULT_API_BASE).trim();
  if (!raw || raw === "/") return "";
  return raw.replace(/\/+$/, "");
}

export function apiPath(path) {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE_URL) return cleanPath;
  return `${API_BASE_URL}${cleanPath}`;
}

export function getAccessToken() {
  const token = localStorage.getItem("access_token");
  return token && token !== "undefined" && token.trim() !== "" ? token : null;
}

export function normalizePercent(value, fallback = null) {
  if (value === null || value === undefined || value === "") return fallback;
  const number = Number(value);
  if (!Number.isFinite(number)) return fallback;
  if (number >= 0 && number <= 1) return Number((number * 100).toFixed(2));
  if (number > 100) return 100;
  if (number < 0) return 0;
  return Number(number.toFixed(2));
}

export function getConfidence(data) {
  const fromResponse = normalizePercent(data?.confidence, null);
  if (fromResponse !== null) return fromResponse;
  const normal = normalizePercent(data?.normal, 0);
  const malicious = normalizePercent(data?.malicious, 0);
  return Math.max(normal, malicious);
}

export function isMaliciousResult(data) {
  const label = String(data?.result || "").toLowerCase();
  if (label.includes("악성") || label.includes("malicious")) return true;
  if (label.includes("정상") || label.includes("benign") || label.includes("safe")) return false;
  return normalizePercent(data?.malicious, 0) >= 60;
}

export function getResultLabel(data) {
  if (!data) return "정보 없음";
  return isMaliciousResult(data) ? "악성" : "정상";
}

export function formatBytes(bytes) {
  const number = Number(bytes);
  if (!Number.isFinite(number)) return "N/A";
  if (number < 1024) return `${number} B`;
  if (number < 1024 * 1024) return `${(number / 1024).toFixed(1)} KB`;
  return `${(number / 1024 / 1024).toFixed(2)} MB`;
}

export function formatDate(value) {
  if (!value) return "N/A";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function resolveReportUrl(reportUrl) {
  if (!reportUrl) return null;
  if (/^https?:\/\//i.test(reportUrl)) return reportUrl;
  const clean = reportUrl.startsWith("/") ? reportUrl : `/${reportUrl}`;
  if (clean.startsWith("/api/")) return clean;
  return apiPath(clean);
}

export function getErrorMessage(error, fallback = "요청 중 오류가 발생했습니다.") {
  if (!error) return fallback;
  if (typeof error === "string") return error;
  const detail = error?.detail || error?.message;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || String(item)).join(", ");
  if (detail) return String(detail);
  return fallback;
}

export async function downloadAuthorizedFile(url, filename = "analysis-report.pdf") {
  const token = getAccessToken();
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(getErrorMessage(payload, "보고서 다운로드에 실패했습니다."));
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
}

export function saveAnalysisResult(result) {
  if (!result?.analysis_id) return;
  const enriched = {
    ...result,
    uploadedAt: result.uploadedAt || new Date().toISOString(),
    status: "done",
    name: result.filename || result.name || "분석 파일",
  };
  localStorage.setItem(result.analysis_id, JSON.stringify(enriched));
  localStorage.setItem("lastViewedAnalysisId", result.analysis_id);
  sessionStorage.setItem("lastViewedAnalysisId", result.analysis_id);

  const previous = JSON.parse(sessionStorage.getItem("uploadedFiles") || "[]");
  const merged = [enriched, ...previous.filter((item) => item.analysis_id !== result.analysis_id)];
  sessionStorage.setItem("uploadedFiles", JSON.stringify(merged));
  window.dispatchEvent(new Event("fileListUpdated"));
}
