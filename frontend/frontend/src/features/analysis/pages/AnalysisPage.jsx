import React from 'react';
import FileUpload from '../components/FileUpload';

export default function AnalysisPage({ handleFileSelect }) {
  return (
    <div className="page-stack compact-stack">
      <section className="page-title-block centered-title">
        <h1>EXE 파일 분석</h1>
        <p>의심스러운 Windows 실행 파일을 제출하여 정적 분석 결과를 확인하세요.</p>
      </section>

      <section className="security-card upload-card compact-upload-card">
        <div className="section-heading compact">
          <div>
            <h2>파일 업로드</h2>
            <p>분석 대상은 EXE 파일만 허용됩니다.</p>
          </div>
          <span className="pill pill-blue">.exe only</span>
        </div>
        <FileUpload onFileSelect={handleFileSelect} />
      </section>

      <section className="steps-grid compact-steps">
        <article className="step-card">
          <span>1</span>
          <h3>제출</h3>
          <p>EXE 파일을 선택하거나 드래그합니다.</p>
        </article>
        <article className="step-card">
          <span>2</span>
          <h3>정적 분석</h3>
          <p>기존 백엔드 분석 API로 악성 여부를 판별합니다.</p>
        </article>
        <article className="step-card">
          <span>3</span>
          <h3>결과 리포트</h3>
          <p>판정, 악성 확률, 대응 방법을 확인합니다.</p>
        </article>
      </section>
    </div>
  );
}
