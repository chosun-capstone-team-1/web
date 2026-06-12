import React from 'react';
import {
  formatDate,
  getConfidence,
  getResultLabel,
  normalizePercent,
  resolveReportUrl,
} from '../../../utils/analysis';

export default function MyPageDetail({ file }) {
  if (!file) return <div className="alert alert-danger">파일 정보가 없습니다.</div>;
  const normal = normalizePercent(file.normal, 0);
  const malicious = normalizePercent(file.malicious, 0);
  const reportUrl = resolveReportUrl(file.report_url);

  return (
    <div className="detail-panel">
      <div className="result-grid">
        <div>
          <h3>분석 요약</h3>
          <p>{file.summary || `${getResultLabel(file)} 파일로 판별되었습니다.`}</p>
          <dl className="info-list compact-list">
            <div><dt>신뢰도</dt><dd>{getConfidence(file)}%</dd></div>
            <div><dt>정상 확률</dt><dd>{normal}%</dd></div>
            <div><dt>악성 확률</dt><dd>{malicious}%</dd></div>
          </dl>
        </div>
        <div>
          <h3>파일 정보</h3>
          <dl className="info-list compact-list">
            <div><dt>파일명</dt><dd className="break-anywhere">{file.filename || file.name || 'N/A'}</dd></div>
            <div><dt>파일 크기</dt><dd>{file.file_size || file.size || 'N/A'}</dd></div>
            <div><dt>SHA-256</dt><dd className="break-anywhere">{file.sha256 || 'N/A'}</dd></div>
            <div><dt>분석 일시</dt><dd>{formatDate(file.created_at || file.uploadedAt || file.log?.start_time)}</dd></div>
          </dl>
        </div>
      </div>
      {reportUrl ? (
        <a className="btn btn-secondary" href={reportUrl} target="_blank" rel="noreferrer">결과 보고서 다운로드</a>
      ) : (
        <div className="alert alert-info">사용 가능한 결과 보고서가 없습니다.</div>
      )}
    </div>
  );
}
