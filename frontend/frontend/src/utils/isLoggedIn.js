const isActuallyLoggedIn = () => {
    if (import.meta.env.VITE_SKIP_AUTH === "true") return true;
    const token = localStorage.getItem("access_token");
    return typeof token === "string" && token !== "undefined" && token.trim() !== "";
};

export default isActuallyLoggedIn;
export const isLoggedIn = isActuallyLoggedIn;