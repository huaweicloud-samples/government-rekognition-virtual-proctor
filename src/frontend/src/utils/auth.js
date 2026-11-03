const TOKEN_KEY = "virtualProctor.token";
const USERNAME_KEY = "virtualProctor.username";

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);

export const getUsername = () => localStorage.getItem(USERNAME_KEY);

export const setUsername = (username) =>
  localStorage.setItem(USERNAME_KEY, username);

export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
};

export const isAuthenticated = () => !!getToken();
