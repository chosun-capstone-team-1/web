import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

export function deleteFileFromSessionAndLocal(analysisId) {
  const removeFrom = (storage) => {
    const list = JSON.parse(storage.getItem("uploadedFiles") || "[]");
    storage.setItem("uploadedFiles", JSON.stringify(list.filter((item) => item.analysis_id !== analysisId)));
    storage.removeItem(analysisId);
  };
  removeFrom(sessionStorage);
  removeFrom(localStorage);
  if (sessionStorage.getItem("lastViewedAnalysisId") === analysisId) sessionStorage.removeItem("lastViewedAnalysisId");
  if (localStorage.getItem("lastViewedAnalysisId") === analysisId) localStorage.removeItem("lastViewedAnalysisId");
}

export function deleteFileByNameAndSize(name, size) {
  const removeFrom = (storage) => {
    const list = JSON.parse(storage.getItem("uploadedFiles") || "[]");
    storage.setItem("uploadedFiles", JSON.stringify(list.filter((item) => !(item.name === name && item.size === size))));
  };
  removeFrom(sessionStorage);
  removeFrom(localStorage);
}

export function getUploadedFilesFromSession() {
  return JSON.parse(sessionStorage.getItem("uploadedFiles") || "[]");
}

export function useUploadSession() {
  const [fileList, setFileList] = useState(getUploadedFilesFromSession());

  const updateSession = (newFiles) => {
    const enhanced = newFiles.map((file) => ({
      analysis_id: file.analysis_id || uuidv4(),
      name: file.name || file.filename || "분석 파일",
      size: file.size || 0,
      extension: file.extension || file.name?.split('.').pop() || 'exe',
      status: file.status || "pending",
      uploadedAt: file.uploadedAt || new Date().toISOString(),
      file,
    }));
    const merged = [...enhanced, ...fileList].filter((item, index, self) =>
      index === self.findIndex((candidate) => candidate.analysis_id === item.analysis_id)
    );
    setFileList(merged);
    sessionStorage.setItem("uploadedFiles", JSON.stringify(merged));
    sessionStorage.setItem("uploadedCount", String(merged.length));
    return merged;
  };

  return [fileList, setFileList, updateSession];
}
