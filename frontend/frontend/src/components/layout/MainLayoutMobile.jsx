import React, { useState } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import Sidebar from './Sidebar';
import { Outlet, Link } from 'react-router-dom';
import Cookies from 'js-cookie';
import { getCookie } from '../../utils/getCookie';
import LogoutButton from '../../features/auth/components/LogoutButton';
import { isLoggedIn } from '../../utils/isLoggedIn';

export default function MainLayoutMobile() {
  const [menuOpen, setMenuOpen] = useState(false);
  const userId = getCookie('user_id');
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    Cookies.remove('user_id');
    window.location.href = '/';
  };

  return (
    <div className="app-shell topnav-shell">
      <header className="app-topbar">
        <div className="topbar-inner mobile">
          <Link to="/" className="malguard-logo" aria-label="MalGuard 홈">MalGuard</Link>
          <button className="icon-button flat" onClick={() => setMenuOpen(true)} aria-label="메뉴 열기">
            <Bars3Icon className="w-5 h-5" />
          </button>
        </div>
      </header>

      {menuOpen && <div className="mobile-overlay" onClick={() => setMenuOpen(false)} />}
      <aside className={`mobile-menu-panel ${menuOpen ? 'open' : ''}`}>
        <div className="mobile-menu-head">
          <span className="malguard-logo">MalGuard</span>
          <button className="icon-button flat" onClick={() => setMenuOpen(false)} aria-label="메뉴 닫기">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        <Sidebar onNavigate={() => setMenuOpen(false)} />
        <div className="mobile-auth-area">
          {isLoggedIn() ? (
            <LogoutButton userId={userId} onLogout={handleLogout} />
          ) : (
            <Link to="/login" onClick={() => setMenuOpen(false)} className="btn btn-primary btn-sm">로그인 / 회원가입</Link>
          )}
        </div>
      </aside>

      <main className="page-frame compact-frame">
        <Outlet />
      </main>
    </div>
  );
}
