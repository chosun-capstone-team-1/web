import { setCookie } from '../utils/cookie';
import { apiPath } from '../utils/analysis';

async function requestJson(path, body) {
  const response = await fetch(apiPath(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload?.detail || payload?.message || '서버에 연결할 수 없습니다';
    throw { response: { status: response.status, data: { detail } }, message: detail };
  }
  return payload;
}

export const registerUser = async (userInfo) => {
  try {
    const data = await requestJson('/users/register', userInfo);
    return { success: true, message: '회원가입이 완료되었습니다.', data };
  } catch (error) {
    const detail = error.response?.data?.detail || error.message;
    if (/이미 존재|already exists|already registered/i.test(detail)) {
      return { success: true, message: '이미 가입된 계정입니다. 로그인해주세요.' };
    }
    return { success: false, status: error.response?.status, message: detail || '회원가입 실패' };
  }
};

export const loginUser = async (loginInfo) => {
  try {
    const data = await requestJson('/users/login', loginInfo);
    const token = data.access_token;
    if (typeof token === 'string' && token.length > 0) {
      localStorage.setItem('access_token', token);
      setCookie('user_id', loginInfo.username);
    }
    return { success: true, accessToken: token, data };
  } catch (error) {
    const status = error.response?.status;
    const detail = (error.response?.data?.detail || '').toLowerCase();
    let message = '로그인 실패';
    if (status === 401) {
      if (detail.includes('비밀번호')) message = '비밀번호가 올바르지 않습니다.';
      else if (detail.includes('존재하지') || detail.includes('not found')) message = '존재하지 않는 사용자입니다.';
      else message = '아이디 또는 비밀번호가 일치하지 않습니다.';
    } else {
      message = error.response?.data?.detail || '서버에 연결할 수 없습니다';
    }
    return { success: false, status, message };
  }
};
