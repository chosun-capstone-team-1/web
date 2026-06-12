# 🛡️ Web - Frontend
AI 기반 악성코드 탐지 시스템의 프론트엔드 개발 작업 레포지토리입니다.<br/>
웹 및 Google Chrome Extension 개발을 진행사항을 확인할 수 있습니다.<br/>
> - 웹에서는 파일 업로드 및 분석 요청, 파일 분석 결과, 분석에 사용된 모델 정보, 마이페이지, 가이드 페이지, 로그인/회원가입 기능 및 QR/URL 분석을 진행할 수 있습니다.<br/>
> - Google Chrome Extension 에서는 자동으로 사용자의 다운로드 파일을 인식하여 분석 결과를 알림으로 보여주며, 레포지토리의 chore-extension 파일 다운로드 후 확장자 관리 -> 개발자 모드 -> 압축해제 된 파일 업로드를 통해 확장자를 등록하여 사용할 수 있습니다.<br/>


<br/>

## 🌐 배포 주소
👉 [배포된 웹 페이지 바로가기](https://web-front-test.netlify.app/)    

> 🔐 검색 차단 설정(`robots.txt`, `<meta name="robots">`) 이 적용되어 검색 엔진에는 노출되지 않고 있습니다.


<br/>

---

## 🛠️ 사용 기술 스택

<div align="center">

<img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
<img src="https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
<img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
<img src="https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
<img src="https://img.shields.io/badge/Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white" />

</div>


<br/>

---

### 📁 frontend 디렉토리 구조 (기능 기반 + 역할 분리)
```
frontend
├─ chrome-extension
│  ├─ icons
│  │  └─icon.PNG
│  ├─ background.js
│  └─ mainfest.json
│
├─ frontend
│  ├─ public
│  │  ├─ AWS.png
│  │  ├─ AWSRDS.png
│  │  ├─ CSEC.PNG
│  │  ├─ EC2.png
│  │  ├─ axios-logo.png
│  │  └─ robots.txt
│  │
│  ├─ src
│  │  ├─ api
│  │  │  └─ auth.js
│  │  │
│  │  ├─ components/layout
│  │  │  ├─ GlobalStats.jsx
│  │  │  ├─ MainLayout.jsx
│  │  │  ├─ MainLayoutMobile.jsx
│  │  │  ├─ MainLayoutPC.jsx
│  │  │  └─ Sidebar.jsx
│  │  │
│  │  ├─ context
│  │  │  ├─ AuthContext.jsx
│  │  │  └─ ToastContext.jsx
│  │  │
│  │  ├─ features
│  │  │  ├─ analysis
│  │  │  │  ├─ components
│  │  │  │  │  ├─ DragAndDrop.jsx
│  │  │  │  │  ├─ FileInput.jsx
│  │  │  │  │  ├─ FileUpload.jsx
│  │  │  │  │  ├─ FileUploadView.jsx
│  │  │  │  │  ├─ handleAnalyzeFile.js
│  │  │  │  │  ├─ useUploadLimit.js
│  │  │  │  │  └─ useUploadSession.js
│  │  │  │  │
│  │  │  │  └─ pages
│  │  │  │     ├─ AnalysisPage.jsx
│  │  │  │     └─ AnalysisResult.jsx 
│  │  │  │
│  │  │  ├─ auth
│  │  │  │  ├─ components
│  │  │  │  │  ├─ AuthForm.jsx
│  │  │  │  │  └─ LogoutButton.jsx
│  │  │  │  │
│  │  │  │  └─ pages
│  │  │  │     └─ LoginPage.jsx 
│  │  │  │
│  │  │  ├─ guide/pages
│  │  │  │  └─ GuideSection.jsx
│  │  │  │
│  │  │  ├─ mypage/pages
│  │  │  │  ├─ MyPage.jsx
│  │  │  │  └─ MyPageDetail.jsx
│  │  │  │
│  │  │  ├─ performance/pages
│  │  │  │  └─ PerformanceSection.jsx
│  │  │  │
│  │  │  └─ search
│  │  │     ├─ components
│  │  │     │  ├─ QRScanner.jsx
│  │  │     │  ├─ QRSearchBlock.jsx
│  │  │     │  ├─ QRUploader.jsx
│  │  │     │  └─ URLSearchForm.jsx
│  │  │     │
│  │  │     └─ pages
│  │  │        └─ QRSerarchPage.jsx 
│  │  │
│  │  ├─ utils
│  │  │  ├─ cookie.js
│  │  │  ├─ getCookie.js
│  │  │  └─ isLoggedIn.js
│  │  │
│  │  ├─ App.css
│  │  ├─ App.jsx
│  │  ├─ index.css
│  │  └─ main.jsx
│  │
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ log-server.js
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ postcss.config.js
│  ├─ tailwind.config.js
│  └─ vite.config.js
│
├─ .gitignore
└─ README.md

```

<br/>