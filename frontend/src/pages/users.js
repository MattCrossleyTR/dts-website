import { useState, useEffect } from "react";
import { getAuthToken } from "../utils/auth";
import User from "../components/user";

export default function UserPage() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/users/", {
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    })
      .then((response) => response.json())
      .then((data) => setUsers(data))
      .catch((error) => console.error("Error fetching users:", error));
  }, []);

  return (
    <div className="task-container">
      <h1>Users</h1>
      <div class="task-list">
        {users.map((user) => (
          <User user={user} />
        ))}
      </div>
    </div>
  );
}
