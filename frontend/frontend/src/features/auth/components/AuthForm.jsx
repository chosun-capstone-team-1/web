import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser, loginUser } from '../../../api/auth';

function AuthForm({ onAuthSuccess }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    if (!form.username.trim() || !form.password.trim()) {
      setMessage('아이디와 비밀번호를 모두 입력해주세요.');
      return false;
    }
    return true;
  };

  const handleLogin = async () => {
    const res = await loginUser(form);
    if (res.success && res.accessToken) {
      onAuthSuccess?.(res.accessToken);
      navigate('/');
      return;
    }
    setMessage(res.message || '로그인 실패');
  };

  const handleSignup = async () => {
    const res = await registerUser(form);
    if (!res.success) {
      setMessage(res.message || '회원가입 실패');
      return;
    }
    if (res.message?.includes('이미 가입된')) {
      setMessage(res.message);
      setMode('login');
      return;
    }
    const loginRes = await loginUser(form);
    if (loginRes.success && loginRes.accessToken) {
      onAuthSuccess?.(loginRes.accessToken);
      navigate('/');
    } else {
      setMessage('회원가입은 완료되었지만 자동 로그인에 실패했습니다. 다시 로그인해주세요.');
      setMode('login');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setMessage('');
    try {
      if (mode === 'login') await handleLogin();
      else await handleSignup();
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <label>
        <span>아이디</span>
        <input name="username" placeholder="아이디를 입력하세요" value={form.username} onChange={handleChange} required />
      </label>
      <label>
        <span>비밀번호</span>
        <input name="password" type="password" placeholder="비밀번호를 입력하세요" value={form.password} onChange={handleChange} required />
      </label>
      {message && <div className={`alert ${/실패|올바르지|존재하지|연결/i.test(message) ? 'alert-danger' : 'alert-info'}`}>{message}</div>}
      <button type="submit" className="btn btn-primary full-width" disabled={loading}>
        {loading ? '처리 중...' : mode === 'login' ? '로그인' : '회원가입'}
      </button>
      <button type="button" className="link-button" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setMessage(''); }}>
        {mode === 'login' ? '계정이 없으신가요? 회원가입' : '이미 계정이 있으신가요? 로그인'}
      </button>
    </form>
  );
}

export default AuthForm;
