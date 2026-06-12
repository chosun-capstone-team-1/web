import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ANALYSIS_API_PATH,
  formatBytes,
  getAccessToken,
  getErrorMessage,
  saveAnalysisResult,
} from "../../../utils/analysis";

const isExeFile = (file) => file?.name?.toLowerCase().endsWith(".exe");

function FileUpload({ onFileSelect }) {
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const setFileSafely = (file) => {
    if (!file) return;
    if (!isExeFile(file)) {
      setSelectedFile(null);
      setError("EXE 파일만 업로드할 수 있습니다.");
      return;
    }
    setError("");
    setSelectedFile(file);
    onFileSelect?.([file]);
  };

  const handleFileChange = (event) => {
    setFileSafely(Array.from(event.target.files || [])[0]);
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    setFileSafely(Array.from(event.dataTransfer.files || [])[0]);
  };

  const analyze = async () => {
    if (!selectedFile) {
      setError("분석할 EXE 파일을 먼저 선택해주세요.");
      return;
    }
    if (!isExeFile(selectedFile)) {
      setError("EXE 파일만 업로드할 수 있습니다.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const token = getAccessToken();
      const response = await fetch(ANALYSIS_API_PATH, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const contentType = response.headers.get("content-type") || "";
      const payload = contentType.includes("application/json") ? await response.json() : await response.text();

      if (!response.ok) {
        throw new Error(getErrorMessage(payload, "분석 요청 중 오류가 발생했습니다."));
      }

      const result = {
        ...payload,
        uploadedAt: new Date().toISOString(),
        name: payload.filename || selectedFile.name,
        size: selectedFile.size,
      };
      saveAnalysisResult(result);
      navigate(`/analysis_results/${result.analysis_id}`);
    } catch (err) {
      const message = err?.message || "서버 연결에 실패했습니다.";
      const modelHint = /모델|model|찾을 수 없습니다|missing/i.test(message)
        ? " 모델 파일이 없거나 경로가 맞지 않아 분석을 진행할 수 없습니다."
        : "";
      setError(`${message}${modelHint}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="upload-flow">
      <div
        className={`upload-dropzone ${isDragging ? "dragging" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
        }}
      >
        <input
          ref={inputRef}
          id="exe-upload-input"
          type="file"
          accept=".exe,application/x-msdownload,application/vnd.microsoft.portable-executable"
          className="sr-only"
          onChange={handleFileChange}
        />
        <div className="upload-icon">⇧</div>
        <h3>분석할 EXE 파일 선택 또는 드래그</h3>
        <p>Windows 실행 파일(.exe)만 업로드할 수 있습니다.</p>
        <button type="button" className="btn btn-secondary">파일 선택</button>
      </div>

      {selectedFile && (
        <div className="selected-file-card">
          <div>
            <span className="eyebrow">선택된 파일</span>
            <strong className="break-anywhere">{selectedFile.name}</strong>
            <p>{formatBytes(selectedFile.size)}</p>
          </div>
          <button type="button" className="btn btn-primary" onClick={analyze} disabled={isAnalyzing}>
            {isAnalyzing ? "분석 중입니다..." : "분석 요청"}
          </button>
        </div>
      )}

      {isAnalyzing && (
        <div className="analysis-loading" role="status" aria-live="polite">
          <span className="spinner" />
          <div>
            <strong>분석 중입니다...</strong>
            <p>파일 특징을 추출하고 악성 여부를 판별하는 중입니다.</p>
          </div>
        </div>
      )}

      {error && <div className="alert alert-danger">{error}</div>}
    </div>
  );
}

export default FileUpload;
