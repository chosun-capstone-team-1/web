import React, { useEffect, useState } from 'react';
import { Routes, Route, useLocation, Link } from 'react-router-dom';
import { createPortal } from 'react-dom';
import Cookies from 'js-cookie';
import LoginPage from './features/auth/pages/LoginPage';
import MainLayout from './components/layout/MainLayout';
import MyPage from './features/mypage/pages/MyPage';
import MyPageDetail from './features/mypage/pages/MyPageDetail';
import GuideSection from './features/guide/pages/GuideSection';
import AnalysisPage from './features/analysis/pages/AnalysisPage';
import { ToastProvider } from './context/ToastContext';
import AnalysisResults from './features/analysis/pages/AnalysisResults';
import { v4 as uuidv4 } from 'uuid';

function NotFound() {
  return (
    <section className="security-card empty-state">
      <span className="empty-icon">404</span>
      <h1>페이지를 찾을 수 없습니다</h1>
      <p>현재 제공되는 기능은 악성파일 분석과 로그인 사용자 분석 기록입니다.</p>
      <Link to="/" className="btn btn-primary">파일 분석으로 이동</Link>
    </section>
  );
}

function App() {
  const location = useLocation();
  const showLoginModal = location.pathname === '/login';
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    if (!Cookies.get('client_uuid')) {
      Cookies.set('client_uuid', uuidv4(), { expires: 1, path: '/' });
    }
  }, []);

  useEffect(() => {
    const clientUuid = Cookies.get('client_uuid');
    if (clientUuid && typeof window !== 'undefined' && window.chrome?.runtime?.sendMessage) {
      window.chrome.runtime.sendMessage({ type: 'SET_CLIENT_UUID', uuid: clientUuid });
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token && token !== 'undefined' && token.trim() !== '');
  }, [location.pathname]);

  const handleLoginSuccess = (accessToken) => {
    localStorage.setItem('access_token', accessToken);
    sessionStorage.removeItem('uploadedFiles');
    sessionStorage.removeItem('uploadedCount');
    setIsLoggedIn(true);
  };

  return (
    <ToastProvider>
      {showLoginModal && createPortal(
        <div className="modal-backdrop">
          <div className="modal-panel">
            <LoginPage onLoginSuccess={handleLoginSuccess} />
          </div>
        </div>,
        document.body
      )}
      <Routes>
        <Route path="/" element={<MainLayout isLoggedIn={isLoggedIn} />}>
          <Route index element={<AnalysisPage />} />
          <Route path="login" element={<div />} />
          <Route path="mypage" element={<MyPage />} />
          <Route path="analysis_results/:analysis_id" element={<AnalysisResults />} />
          <Route path="analysis_results" element={<AnalysisResults />} />
          <Route path="guide" element={<GuideSection />} />
          <Route path="mypage/detail/:analysis_id" element={<MyPageDetail />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </ToastProvider>
  );
}

export default App;
