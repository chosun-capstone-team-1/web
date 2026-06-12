import React from 'react';

export default function LogoutButton({ onLogout }) {
  return (
    <button type="button" className="btn btn-secondary" onClick={onLogout}>
      로그아웃
    </button>
  );
}
