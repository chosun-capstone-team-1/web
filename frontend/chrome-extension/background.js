let autoAnalyzeEnabled = true;

function toggleAutoAnalyze() {
  autoAnalyzeEnabled = !autoAnalyzeEnabled;
  chrome.action.setBadgeText({ text: autoAnalyzeEnabled ? "ON" : "OFF" });
  chrome.action.setBadgeBackgroundColor({
    color: autoAnalyzeEnabled ? "#00c853" : "#d50000"
  });
  //chrome.action.setIcon({ path: autoAnalyzeEnabled ? "icons/icon-on.png" : "icons/icon-off.png" });
  console.log("자동 분석 기능:", autoAnalyzeEnabled ? "켜짐" : "꺼짐");
}

async function analyzeDownloadedFile(fileUrl) {
  try {
    const response = await fetch(fileUrl);
    const blob = await response.blob();
    console.log("📦 다운로드된 blob:", blob);
    const formData = new FormData();
    const extMap = {
      "application/pdf": "pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
      "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
      "application/x-msdownload": "exe"
    };
    const extension = extMap[blob.type] || "bin";
    const safeFilename = `downloaded_file.${extension}`;
    formData.append("file", blob, safeFilename);
    console.log("📤 formData 파일 확인:", formData.get("file"));

    const res = await fetch("http://13.125.214.199:8000/analyze-full", {
      method: "POST",
      body: formData,
      credentials: "omit", // no need for cookies
      headers: {
        "X-Extension-Request": "true"
      }
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`HTTP ${res.status} - ${res.statusText}\n${errText}`);
    }

    const result = await res.json();
    console.log("백엔드 분석 결과:", result);
    const rawVerdict = result?.result || "UNKNOWN";
    const verdictIcon = rawVerdict === "정상" ? "🟢" : rawVerdict === "악성" ? "🔴" : "🔍";
    const verdict = `${verdictIcon} ${rawVerdict}`;
    const message = result?.summary
      ? `${rawVerdict === "정상" ? "✅" : rawVerdict === "악성" ? "❌" : "ℹ️"} ${result.summary}`
      : "ℹ️ 검증 결과를 확인해주세요.";

    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon.png",
      title: `🔍 검증 결과: ${verdict}`,
      message
    });
  } catch (error) {
    console.error("검증 오류", error);
    const errorText = error.message || "알 수 없는 오류";
    let verdict = "알 수 없음";
    let userMessage = "⚠️ 분석 요청에 실패했습니다.\n";

    if (errorText.includes("지원하지 않는 확장자")) {
      verdict = "지원되지 않음";
      userMessage += "해당 파일 확장자는 분석이 지원되지 않습니다.";
    } else {
      userMessage += `사유: ${errorText}`;
    }

    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon.png",
      title: `분석 실패: ${verdict}`,
      message: userMessage,
    });
  }
}

chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state?.current === "complete") {
    if (!autoAnalyzeEnabled) {
      console.log("자동 분석 기능이 꺼져 있습니다.");
      return;
    }

    chrome.downloads.search({ id: delta.id }, ([downloadItem]) => {
      const fileUrl = downloadItem.url;
      const filename = downloadItem.filename || fileUrl.split("/").pop();

      console.log("다운로드 완료 감지됨:", fileUrl);
      console.log("추출된 파일명:", filename);

      if (/\.(exe|docx|pdf|hwp|pptx|xlsx)$/i.test(filename)) {
        chrome.storage.local.get(["analyze_count"], ({ analyze_count = 0 }) => {
          console.log("지원되는 확장자 감지됨. 분석 시작");
          chrome.notifications.create({
            type: "basic",
            iconUrl: "icons/icon.png",
            title: "파일 다운로드 감지됨",
            message: "파일이 감지되었습니다. 자동으로 악성 여부를 분석합니다.",
          }, (notificationId) => {
            console.log("알림 생성됨:", notificationId);
          });

          analyzeDownloadedFile(fileUrl);
        });
      } else {
        console.log("지원되지 않는 파일 확장자:", filename);
      }
    });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "TOGGLE_AUTO_ANALYZE") {
    autoAnalyzeEnabled = message.enabled;
    console.log("자동 분석 설정 변경됨:", autoAnalyzeEnabled);
    sendResponse({ success: true });
  }
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({ text: "ON" });
  chrome.action.setBadgeBackgroundColor({ color: "#00c853" });
  //chrome.action.setIcon({ path: "icons/icon-on.png" });
});

chrome.action.onClicked.addListener(() => {
  toggleAutoAnalyze();
});
