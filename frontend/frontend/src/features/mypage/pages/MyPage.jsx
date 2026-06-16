import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MyPageDetail from './MyPageDetail';
import {
  HISTORY_API_PATH,
  HISTORY_DOWNLOAD_PATH,
  formatDate,
  getAccessToken,
  getErrorMessage,
  getResultLabel,
  normalizePercent,
  resolveReportUrl,
  downloadAuthorizedFile,
} from '../../../utils/analysis';

function statusClass(label) {
  if (label === '악성') return 'danger';
  if (label === '정상') return 'safe';
  return 'warning';
}

export default function MyPage() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [expandedId, setExpandedId] = useState(null);
  const [authInvalid, setAuthInvalid] = useState(false);
  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    const fetchHistory = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(HISTORY_API_PATH, {
          headers: { Authorization: `Bearer ${token}` },
          credentials: 'include',
        });
        const payload = await response.json().catch(() => ({}));
        if (response.status === 401 || response.status === 403) {
          localStorage.removeItem('access_token');
          document.cookie = 'user_id=; path=/; max-age=0';
          setAuthInvalid(true);
          return;
        }
        if (!response.ok) throw new Error(getErrorMessage(payload, '히스토리 API가 없어 연결 불가'));
        const list = Array.isArray(payload) ? payload : [];
        setRecords(list);
        list.forEach((item) => {
          if (item?.analysis_id) localStorage.setItem(item.analysis_id, JSON.stringify(item));
        });
      } catch (err) {
        setError(err.message || '히스토리 API가 없어 연결 불가');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [token]);

  const filteredRecords = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return records
      .filter((item) => !normalized || (item.filename || '').toLowerCase().includes(normalized))
      .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
  }, [records, query]);

  const summary = useMemo(() => {
    const malicious = records.filter((item) => getResultLabel(item) === '악성').length;
    const normal = records.filter((item) => getResultLabel(item) === '정상').length;
    const reportable = records.filter((item) => item.report_url).length;
    return { total: records.length, malicious, normal, reportable };
  }, [records]);

  const openReport = async (record) => {
    const directUrl = resolveReportUrl(record.report_url);
    if (directUrl) {
      window.open(directUrl, '_blank');
      return;
    }
    if (!record.analysis_id) return;
    try {
      await downloadAuthorizedFile(
        `${HISTORY_DOWNLOAD_PATH}/${record.analysis_id}`,
        `${record.filename || 'analysis'}_report.pdf`
      );
    } catch (err) {
      setError(err.message || '보고서 다운로드에 실패했습니다.');
    }
  };

  if (!token || authInvalid) {
    return (
      <section className="security-card empty-state">
        <span className="empty-icon">🔐</span>
        <h1>로그인 후 이용 가능합니다.</h1>
        <p>분석 기록과 보고서 다운로드는 로그인 사용자에게 제공됩니다.</p>
        <Link to="/login" className="btn btn-primary">로그인 하러 가기</Link>
      </section>
    );
  }

  return (
    <div className="page-stack reference-history-page">
      <section className="history-header-row">
        <div>
          <h1>분석 기록</h1>
          <p>로그인 사용자의 악성파일 분석 내역을 확인합니다.</p>
        </div>
      </section>

      {records.length > 0 && (
        <section className="history-summary-grid">
          <article className="summary-card"><span>총 분석 건수</span><strong>{summary.total.toLocaleString()}</strong></article>
          <article className="summary-card danger"><span>탐지된 위협</span><strong>{summary.malicious.toLocaleString()}</strong></article>
          <article className="summary-card safe"><span>정상 파일</span><strong>{summary.normal.toLocaleString()}</strong></article>
          <article className="summary-card"><span>보고서</span><strong>{summary.reportable.toLocaleString()}</strong></article>
        </section>
      )}

      <section className="security-card history-table-card">
        <div className="history-toolbar">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="파일명 검색"
            className="search-input"
          />
          <span className="muted-text">표시 {filteredRecords.length}건</span>
        </div>

        {loading && <div className="analysis-loading"><span className="spinner" /><strong>분석 기록을 불러오는 중입니다...</strong></div>}
        {error && <div className="alert alert-danger">{error}</div>}
        {!loading && !error && filteredRecords.length === 0 && (
          <div className="empty-state small">
            <span className="empty-icon">⌕</span>
            <h2>아직 분석 기록이 없습니다.</h2>
            <p>악성파일 분석을 완료하면 이곳에 기록이 표시됩니다.</p>
          </div>
        )}

        {filteredRecords.length > 0 && (
          <div className="responsive-table-wrap">
            <table className="history-table reference-history-table">
              <thead>
                <tr>
                  <th>파일명</th>
                  <th>분석 일시</th>
                  <th>결과</th>
                  <th>신뢰도</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => {
                  const label = getResultLabel(record);
                  const confidence = label === '악성'
                    ? normalizePercent(record.malicious, 0)
                    : normalizePercent(record.normal, 0);
                  const reportUrl = resolveReportUrl(record.report_url);
                  return (
                    <React.Fragment key={record.analysis_id}>
                      <tr>
                        <td className="break-anywhere file-cell">{record.filename || 'N/A'}</td>
                        <td>{formatDate(record.created_at || record.log?.start_time)}</td>
                        <td><span className={`status-badge ${statusClass(label)}`}>{label}</span></td>
                        <td>
                          <div className="confidence-cell">
                            <span>{confidence ?? 'N/A'}{confidence !== null ? '%' : ''}</span>
                            <div className="mini-meter"><i style={{ width: `${normalizePercent(confidence, 0)}%` }} /></div>
                          </div>
                        </td>
                        <td className="manage-cell">
                          <button
                            type="button"
                            className="table-link"
                            onClick={() => {
                              localStorage.setItem(record.analysis_id, JSON.stringify(record));
                              localStorage.setItem('lastViewedAnalysisId', record.analysis_id);
                              navigate(`/analysis_results/${record.analysis_id}`);
                            }}
                          >
                            결과 보기
                          </button>
                          {(reportUrl || record.analysis_id) && (
                            <button type="button" className="table-link secondary" onClick={() => openReport(record)}>보고서</button>
                          )}
                          <button type="button" className="table-link secondary" onClick={() => setExpandedId(expandedId === record.analysis_id ? null : record.analysis_id)}>상세</button>
                        </td>
                      </tr>
                      {expandedId === record.analysis_id && (
                        <tr className="detail-row"><td colSpan="5"><MyPageDetail file={record} /></td></tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
