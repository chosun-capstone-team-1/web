import React, { createContext, useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { CheckCircleIcon, ClockIcon } from "@heroicons/react/24/solid";
import { useNavigate } from "react-router-dom";

// ToastContext: 전역 상태 관리를 위한 Context 생성
const ToastContext = createContext();

// ToastProvider: 토스트 알림 상태와 관련 함수를 제공하는 Context Provider 컴포넌트
export const ToastProvider = ({ children }) => {
  // toasts 상태: 현재 화면에 표시 중인 토스트 알림 목록 (배열)
  const [toasts, setToasts] = useState([]);
  const navigate = useNavigate();

  // showToast: 새 토스트 알림을 추가하는 함수
  // message: 알림 메시지, status: 상태값, analysisId: 분석 식별자, progress: 진행률(0~100)
  const showToast = (message, status = "done", analysisId = null, progress = 0) => {
    const id = Date.now(); // 고유 ID 생성 (타임스탬프 사용)
    setToasts(prev => [...prev, { id, message, status, analysisId, progress }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 30000); // 30초 후 자동 제거
  };

  // updateToastStatus: 특정 분석 ID에 해당하는 토스트의 상태(status)를 업데이트
  const updateToastStatus = (analysisId, status) => {
    setToasts(prev =>
      prev.map(t =>
        t.analysisId === analysisId
          ? { ...t, status }
          : t
      )
    );
  };

  // updateProgress: 특정 분석 ID에 해당하는 토스트의 진행률(progress)를 업데이트
  const updateProgress = (analysisId, progress) => {
    setToasts(prev =>
      prev.map(t =>
        t.analysisId === analysisId
          ? { ...t, progress }
          : t
      )
    );
  };

  // removeToast: 특정 토스트 ID를 가진 알림을 수동으로 제거하는 함수
  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // 프로그래스가 100% 이상인 항목을 "done" 상태로 자동 전환 처리
  useEffect(() => {
    const hasPending = toasts.some(t => t.progress >= 100 && t.status !== "done");
    if (hasPending) {
      setToasts(prev =>
        prev.map(t =>
          t.progress >= 100 && t.status !== "done"
            ? { ...t, status: "done" }
            : t
        )
      );
    }
  }, [toasts]);

  return (
    <ToastContext.Provider value={{ showToast, updateProgress, updateToastStatus }}>
      {children}
      {/* createPortal: 알림을 최상위 DOM(body)에 렌더링하여 UI가 다른 컴포넌트에 가려지지 않도록 함 */}
      {createPortal(
        <div className="fixed top-20 right-7 space-y-3 z-50">
          {toasts.map((toast) => (
            // 알림 카드: 상태에 따라 테두리 색상 및 애니메이션 적용
            <div
              key={toast.id}
              className={`relative w-72 bg-white rounded-xl shadow-lg p-3 transition-all duration-700 ease-in-out
                ${toast.status === 'done' ? 'translate-x-0 hover:translate-x-1 animate-slide-out border border-green-200' : 'border border-yellow-300'}`}
            >
              {/* 닫기 버튼: 사용자가 수동으로 해당 토스트 알림을 제거할 수 있음 */}
              <button
                onClick={() => removeToast(toast.id)}
                className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gray-400 hover:bg-gray-500 text-white flex items-center justify-center shadow"
                aria-label="닫기"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <div className="flex items-center space-x-2">
                {/* 아이콘 표시: 상태에 따른 아이콘 및 배경 색상 변경 */}
                <div className={`${toast.status === 'done' ? 'bg-green-100' : 'bg-yellow-100'} p-1.5 rounded-full`}>
                  {toast.status === 'done' ? (
                    // 분석 완료: 초록색 체크 아이콘 표시
                    <CheckCircleIcon className="h-5 w-5 text-green-500" />
                  ) : (
                    // 분석 중: 노란색 시계 아이콘 표시
                    <ClockIcon className="h-5 w-5 text-yellow-500" />
                  )}
                </div>

                <div className="flex-1">
                  {/* 상태 텍스트: 완료 또는 진행 중에 따라 다르게 표시 */}
                  <p className="text-sm font-semibold text-gray-800">
                    {toast.status === 'done' ? "분석 완료" : "분석 중"}
                  </p>

                  {/* 알림 메시지: 여러 줄 지원 및 줄바꿈 유지 */}
                  <div className="text-xs text-gray-600 break-all whitespace-pre-wrap max-w-full">{toast.message}</div>

                  {/* 프로그래스 바 표시: 진행 중일 때만 */}
                  {toast.status !== 'done' && (
                    <div className="w-full mt-2">
                      <div className="flex items-center space-x-2">
                        {/* 프로그래스 바 배경 */}
                        <div className="flex-1 bg-gray-200 h-2 rounded-full">
                          {/* 프로그래스 바 진행률 표시 */}
                          <div
                            className="h-2 bg-yellow-400 rounded-full transition-all duration-500"
                            style={{ width: `${toast.progress || 0}%` }}
                          />
                        </div>
                        {/* 진행률 텍스트 */}
                        <div className="text-xs text-gray-500">{toast.progress || 0}%</div>
                      </div>
                    </div>
                  )}

                  {/* 분석 완료: 결과 보기 버튼 표시 */}
                  {toast.status === 'done' && (
                    <p
                      onClick={() => {
                        if (toast.analysisId) {
                          navigate(`/analysis_results/${toast.analysisId}`);
                        }
                      }}
                      className="text-xs text-green-600 mt-1 font-medium cursor-pointer hover:underline"
                    >
                      결과 보기 →
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
};
{/* --- Tailwind CSS Custom Animation for Slide-Out --- */}
<style>
{`
@keyframes slide-out {
  to {
    transform: translateX(150%);
    opacity: 0;
  }
}
.animate-slide-out {
  animation: slide-out 1s ease-in forwards;
  animation-delay: 177s; /* start near 3min */
}
`}
</style>
