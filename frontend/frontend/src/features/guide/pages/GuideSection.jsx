import React from 'react';

const guides = [
  {
    title: '악성파일 분석',
    body: '악성파일을 업로드해 백엔드 분석 API로 악성 여부를 확인합니다.',
  },
  {
    title: '정상/악성 결과 확인',
    body: '분석 결과 카드에서 정상/악성 여부, 신뢰도, SHA-256, 대응 방법, 보고서 다운로드 상태를 확인할 수 있습니다.',
  },
  {
    title: '로그인 사용자 기록',
    body: '로그인 후 분석하면 백엔드 히스토리 API를 통해 분석 기록과 보고서를 다시 확인할 수 있습니다.',
  },
];

function GuideSection() {
  return (
    <div className="page-stack">
      <section className="hero-card compact-hero">
        <span className="eyebrow">Service Guide</span>
        <h1>서비스 안내</h1>
        <p>불필요한 기능을 제외하고 악성파일 분석 흐름을 명확하게 제공합니다.</p>
      </section>
      <section className="steps-grid">
        {guides.map((item, index) => (
          <article className="step-card" key={item.title}>
            <span>{index + 1}</span>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </article>
        ))}
      </section>
      <section className="security-card">
        <h2>결과 해석 유의사항</h2>
        <p className="muted-text mt-2">
          본 서비스는 정적 분석 기반 1차 판별 결과를 제공합니다. 정상으로 표시되더라도 출처가 불분명한 실행 파일은
          열기 전 발신자를 재확인하고 보안 담당자에게 문의하는 것을 권장합니다.
        </p>
      </section>
    </div>
  );
}

export default GuideSection;
