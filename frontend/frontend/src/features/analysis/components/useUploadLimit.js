import { useEffect, useState } from "react";
import isActuallyLoggedIn from "../../../utils/isLoggedIn";
import { getCookie } from "../../../utils/getCookie";

export function useUploadLimit() {
  const [remainingInfo, setRemainingInfo] = useState(null);

  useEffect(() => {
    if (!getCookie("client_uuid")) {
      const uuid = crypto.randomUUID?.() || Math.random().toString(36).slice(2);
      document.cookie = `client_uuid=${uuid}; path=/; max-age=86400`;
    }

    fetch("/api/limit/upload-remaining", { credentials: "include" })
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => setRemainingInfo(data))
      .catch(() => setRemainingInfo(null));
  }, []);

  const maxCount = isActuallyLoggedIn() ? Infinity : 3;
  return { maxCount, remainingInfo, remainingCount: remainingInfo?.remaining ?? maxCount, isActuallyLoggedIn };
}
