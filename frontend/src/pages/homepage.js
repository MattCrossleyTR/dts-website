import { useState, useEffect } from "react";
import { getAuthToken } from "../utils/auth";
import Task from "../components/task";
import "../styles/task.css";

export default function HomePage() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/tasks/", {
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    })
      .then((response) => response.json())
      .then((data) => setTasks(data))
      .catch((error) => console.error("Error fetching tasks:", error));
  }, []);

  return (
    <div className="task-container">
      <h1>Your Tasks</h1>
      <div className="task-list">
        {Array.isArray(tasks) && tasks.map((task) => <Task task={task} />)}
      </div>
    </div>
  );
}
