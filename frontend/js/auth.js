/**
 * auth.js
 * Session and Authentication Manager for frontend UI.
 */
const Auth = (() => {
  const TOKEN_KEY = "auth_token";
  const USER_KEY = "auth_user";

  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getUser() {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = "/index.html";
  }

  function redirectByRole(role) {
    switch (role) {
      case "ADMIN":
        window.location.href = "/admin/dashboard.html";
        break;
      case "FACULTY":
        window.location.href = "/faculty/dashboard.html";
        break;
      case "STUDENT":
        window.location.href = "/student/dashboard.html";
        break;
      default:
        window.location.href = "/index.html";
    }
  }

  function requireRole(expectedRole) {
    const token = getToken();
    const user = getUser();
    if (!token || !user || user.role !== expectedRole) {
      logout();
    }
  }

  return {
    setSession,
    getToken,
    getUser,
    logout,
    redirectByRole,
    requireRole
  };
})();