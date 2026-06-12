import { Link } from 'react-router-dom';
import AuthForm from '../../auth/components/AuthForm';

export default function LoginPage({ onLoginSuccess }) {
  return (
    <div className="auth-page">
      <div className="security-card auth-card">
        <Link to="/" className="back-link">← EXE 분석으로 돌아가기</Link>
        <span className="eyebrow">Account</span>
        <h1>로그인 / 회원가입</h1>
        <p>로그인하면 분석 기록과 결과 보고서 다운로드를 사용할 수 있습니다.</p>
        <AuthForm onAuthSuccess={onLoginSuccess} />
      </div>
    </div>
  );
}
