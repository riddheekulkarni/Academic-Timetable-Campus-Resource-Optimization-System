/**
 * API Fetch Client & Global UI Toast System
 */

const Toast = (() => {
  function getContainer() {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }
    return container;
  }

  return {
    show: (message, type = "info") => {
      const container = getContainer();
      const toast = document.createElement("div");
      toast.className = `toast toast-${type}`;
      toast.textContent = message;
      container.appendChild(toast);

      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }
  };
})();

const api = (() => {
  const BASE_URL = "";

  function getToken() {
    return localStorage.getItem("auth_token");
  }

  async function request(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(BASE_URL + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    let data;
    try {
      data = await response.json();
    } catch (err) {
      data = { success: false, message: "Invalid server response." };
    }

    if (!response.ok && data.success === undefined) {
      data.success = false;
    }

    return data;
  }

  return {
    get: (path) => request("GET", path),
    post: (path, body) => request("POST", path, body),
    put: (path, body) => request("PUT", path, body),
    del: (path) => request("DELETE", path),
  };
})();