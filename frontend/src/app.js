import { Route, Routes } from "react-router";
import "./styles/app.css";
import ProtectedRoute from "./components/ProtectedRoute";
import NavBar from "./components/navbar";
import HomePage from "./pages/homepage";
import LoginPage from "./pages/login";
import TaskPage from "./pages/task";
import RegisterPage from "./pages/register";
import UserPage from "./pages/users";

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/task/:taskId?"
          element={
            <ProtectedRoute>
              <TaskPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/users/"
          element={
            <ProtectedRoute adminOnly={true}>
              <UserPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}
