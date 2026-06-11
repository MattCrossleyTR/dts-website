import { Navigate, useLocation } from "react-router";
import { getAuthToken, setAuth } from "../utils/auth";
import { useEffect, useState } from "react";
import { BACKEND } from "../constants";

export default function ProtectedRoute({ adminOnly = false, children }) {
  const location = useLocation();
  const token = getAuthToken();
  const [authState, setAuthState] = useState(null)

  useEffect(() => {
    let cancelled = false

    checkAuth(location.pathname, token, adminOnly).then(result => {
      if (!cancelled) setAuthState(result)
    })

    return () => {
      cancelled = true
    }
  }, [location.pathname, token, adminOnly])

  useEffect(() => {
    if (authState?.msg) alert(authState.msg)
  }, [authState])

  if (authState == null) {
    return <p>Checking auth...</p>
  }
  if (authState.path) {
    return <Navigate to={authState.path} replace />;
  }
  return children;
}

export async function checkAuth(urlPath, token, adminOnly) {
  // no auth and not on login screen, send to login screen
  if (!token && urlPath !== "/login") {
    return {
      msg: null,
      path: '/login'
    }
  }

  if (urlPath === "/login") {
    if (token) {
      // If authenticated and on login page, redirect to home
      return {
        msg: null,
        path: '/'
      }
    } else {
      // not authenticated but on the login screen - do nothing
      return { auth: false }
    }

  }
  if (token && urlPath === "/login") {
    return {
      msg: null,
      path: '/'
    }
  }

  const response = await fetch(`${BACKEND}/users/current`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  })

  // If the response is not ok, clear auth and redirect to login
  if (!response.ok) {
    setAuth(null)
    return {
      msg: "Unauthorized. Please log in again.",
      path: "/login"
    }
  }

  const user = await response.json()
  // if route is admin only and user is not admin, send home
  if (adminOnly === true && !user.admin) {
    return {
      msg: "Unauthorized. You are not an admin",
      path: "/"
    }
  }
  return { auth: true }
}