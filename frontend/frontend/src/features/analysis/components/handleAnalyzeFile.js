export async function handleAnalyzeFile() {
  return null;
}

export function getProgressBarInfo(status, progress) {
  if (status === "done") return { label: "분석 완료", labelColor: "text-green-600", barColor: "bg-green-400" };
  if (status === "processing") return { label: "분석 중...", labelColor: "text-yellow-600", barColor: "bg-yellow-400" };
  return { label: `${progress ?? 0}%`, labelColor: "text-gray-500", barColor: "bg-gray-200" };
}
