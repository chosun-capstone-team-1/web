import React, { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  formatDate,
  getConfidence,
  getResultLabel,
  isMaliciousResult,
  normalizePercent,
  resolveReportUrl,
} from "../../../utils/analysis";

function loadStoredAnalysis(id) {
  if (!id) return null;
  for (const storage of [localStorage, sessionStorage]) {
    const raw = storage.getItem(id);
    if (!raw) continue;
    try { return JSON.parse(raw); } catch { return null; }
  }
  return null;
}

function findLatestAnalysis() {
  const ids = [sessionStorage.getItem("lastViewedAnalysisId"), localStorage.getItem("lastViewedAnalysisId")].filter(Boolean);
  for (const id of ids) {
    const data = loadStoredAnalysis(id);
    if (data) return data;
  }
  const sessionFiles = JSON.parse(sessionStorage.getItem("uploadedFiles") || "[]");
  return sessionFiles
    .filter((item) => item?.analysis_id)
    .sort((a, b) => new Date(b.created_at || b.uploadedAt || 0) - new Date(a.created_at || a.uploadedAt || 0))[0] || null;
}

function AnalysisResults() {
  const { analysis_id, analysisId } = useParams();
  const routeId = analysis_id || analysisId;
  const [fileData, setFileData] = useState(null);

  useEffect(() => {
    setFileData(loadStoredAnalysis(routeId) || findLatestAnalysis());
  }, [routeId]);

  const result = useMemo(() => {
    if (!fileData) return null;
    const malicious = isMaliciousResult(fileData);
    const displayPercent = malicious
      ? normalizePercent(fileData.malicious, 0)
      : normalizePercent(fileData.normal, 0);
    return {
      malicious,
      label: getResultLabel(fileData),
      modelAccuracy: getConfidence(fileData),
      normal: normalizePercent(fileData.normal, 0),
      maliciousPercent: normalizePercent(fileData.malicious, 0),
      displayPercent,
      displayLabel: malicious ? "악성 확률" : "정상 확률",
      reportUrl: resolveReportUrl(fileData.report_url),
    };
  }, [fileData]);

  if (!fileData || !result) {
    return (
      <section className="security-card empty-state">
        <span className="empty-icon">⌕</span>
        <h1>분석 결과가 없습니다</h1>
        <p>결과 화면은 EXE 파일 분석을 완료한 뒤 확인할 수 있습니다.</p>
        <Link to="/" className="btn btn-primary">EXE 파일 분석으로 돌아가기</Link>
      </section>
    );
  }

  const fileName = fileData.filename || fileData.name || fileData.display_name || "N/A";
  const completedAt = fileData.created_at || fileData.uploadedAt || fileData.log?.start_time;
  const verdictTitle = result.malicious ? "악성 판정 (Malicious)" : "정상 판정 (Benign)";
  const verdictText = result.malicious
    ? "악성 파일로 의심됩니다. 정적 분석 결과 악성 패턴이 탐지되었습니다. 파일을 실행하지 말고 관리자에게 전달한 뒤 삭제를 권장합니다."
    : "정상 파일로 판단되었습니다. 다만 정적 분석 기반 1차 판별 결과이므로 출처가 불분명한 파일은 주의가 필요합니다.";

  return (
    <div className="page-stack reference-result-page">
      <div className="breadcrumb">Home › Analysis › <strong>Result</strong></div>

      <div className={`result-alert ${result.malicious ? "danger" : "safe"}`}>
        {result.malicious ? "이 파일은 잠재적인 위험으로 분류되었습니다." : "이 파일은 정상 파일로 분류되었습니다."}
      </div>

      <div className="report-title-row">
        <h1>분석 결과 리포트</h1>
        {result.reportUrl ? (
          <a href={result.reportUrl} target="_blank" rel="noreferrer" className="btn btn-primary btn-sm">결과 보고서 다운로드</a>
        ) : (
          <button type="button" className="btn btn-disabled btn-sm" disabled>결과 보고서 없음</button>
        )}
      </div>

      <section className="result-top-grid">
        <article className={`verdict-report-card ${result.malicious ? "danger" : "safe"}`}>
          <div className="score-ring">
            <strong>{result.displayPercent ?? "N/A"}{result.displayPercent !== null ? "%" : ""}</strong>
            <span>{result.displayLabel}</span>
          </div>
          <div className="verdict-copy">
            <span className={`status-badge ${result.malicious ? "danger" : "safe"}`}>{result.label}</span>
            <h2>{verdictTitle}</h2>
            <p>{verdictText}</p>
          </div>
        </article>

        <article className="security-card file-info-card reference-file-card">
          <h2>File Information</h2>
          <dl className="info-list file-info-list">
            <div><dt>Filename</dt><dd className="break-anywhere">{fileName}</dd></div>
            <div><dt>Size</dt><dd>{fileData.file_size || fileData.size || "N/A"}</dd></div>
            <div><dt>SHA-256 Hash</dt><dd className="hash-box">{fileData.sha256 || "N/A"}</dd></div>
          </dl>
        </article>
      </section>

      <section className="result-bottom-grid">
        <article className="security-card">
          <h2>분석 설명</h2>
          <div className="probability-list compact-probability">
            <div>
              <div className="probability-label"><span>정상 확률</span><strong>{result.normal}%</strong></div>
              <div className="meter"><span className="safe" style={{ width: `${result.normal}%` }} /></div>
            </div>
            <div>
              <div className="probability-label"><span>악성 확률</span><strong>{result.maliciousPercent}%</strong></div>
              <div className="meter"><span className="danger" style={{ width: `${result.maliciousPercent}%` }} /></div>
            </div>
          </div>
          <p className="muted-text result-note">{fileData.summary || verdictText}</p>
        </article>

        <article className="security-card">
          <h2>Recommended Actions</h2>
          {result.malicious ? (
            <ul className="action-list danger-list">
              <li>파일 실행 금지</li>
              <li>발신자 재확인</li>
              <li>관리자 전달</li>
              <li>삭제 권장</li>
            </ul>
          ) : (
            <div className="alert alert-warning">
              정적 분석 기반 1차 판별 결과이므로 출처가 불분명한 파일은 주의가 필요합니다.
            </div>
          )}
        </article>

        <article className="security-card">
          <h2>Additional Info</h2>
          <dl className="info-list compact-info-list">
            <div><dt>Analyzed At</dt><dd>{formatDate(completedAt)}</dd></div>
            <div><dt>Extension</dt><dd>{fileData.extension || ".exe"}</dd></div>
            <div><dt>Model Accuracy</dt><dd>{result.modelAccuracy ?? "N/A"}%</dd></div>
            <div><dt>Report</dt><dd>{result.reportUrl ? "생성됨" : "없음"}</dd></div>
          </dl>
        </article>
      </section>
    </div>
  );
}

export default AnalysisResults;
