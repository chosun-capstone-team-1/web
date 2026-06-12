import React from 'react';
import Sidebar from './Sidebar';
import { Outlet, Link } from 'react-router-dom';
import Cookies from 'js-cookie';
import { getCookie } from '../../utils/getCookie';
import LogoutButton from '../../features/auth/components/LogoutButton';
import { isLoggedIn } from '../../utils/isLoggedIn';

export default function MainLayoutPC() {
  const userId = getCookie('user_id');
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    Cookies.remove('user_id');
    window.location.href = '/';
  };

  return (
    <div className="app-shell topnav-shell">
      <header className="app-topbar">
        <div className="topbar-inner">
          <Link to="/" className="malguard-logo" aria-label="MalGuard 홈">MalGuard</Link>
          <Sidebar />
          <div className="topbar-actions">
            <Link to="/guide" className="topbar-help">도움말</Link>
            {isLoggedIn() ? (
              <div className="topbar-user-area">
                <span className="user-avatar" aria-hidden="true">{(userId || 'M').slice(0, 1).toUpperCase()}</span>
                <LogoutButton userId={userId} onLogout={handleLogout} />
              </div>
            ) : (
              <Link to="/login" className="login-chip" aria-label="로그인 또는 회원가입">로그인</Link>
            )}
          </div>
        </div>
      </header>
      <main className="page-frame compact-frame">
        <Outlet />
      </main>
    </div>
  );
}
