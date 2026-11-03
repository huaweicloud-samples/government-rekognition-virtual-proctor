import { retryWrapper } from "./index";
import { clearAuth, getToken, setToken, setUsername } from "./auth";

const settings = window.proctorSettings || {};
const baseUrl = settings.apiEndpoint || "";

export const login = (username, password) =>
  fetch(`${baseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  }).then((res) => {
    if (!res.ok) throw new Error("Invalid username or password");
    return res.json().then((body) => {
      setToken(body.token);
      setUsername(body.username);
      return body;
    });
  });

const request = (url, method, data) =>
  retryWrapper(() =>
    fetch(`${baseUrl}${url}`, {
      method: method || "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: data ? JSON.stringify(data) : undefined,
    }).then((res) => {
      if (res.status === 401) {
        clearAuth();
        throw new Error("Session expired. Please sign in again.");
      }
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      return res.json();
    })
  );

export default request;
