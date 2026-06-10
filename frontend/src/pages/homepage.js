import { useState, useEffect } from "react";
import { getAuthPayload, getAuthToken } from "../utils/auth";
import Task from "../components/task";
import "../styles/task.css";
import { BACKEND } from "../constants";

export default function HomePage() {
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);

  const currentUserId = getAuthPayload().sub
  const [filterMode, setFilterMode] = useState("all")

  useEffect(() => {
    fetch(`${BACKEND}/tasks/`, {
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    })
      .then((response) => response.json())
      .then((data) => setTasks(data))
      .catch((error) => console.error("Error fetching tasks:", error));
  }, []);

  useEffect(() => {
    const filteredTasks = tasks.filter(t => {
      switch (filterMode) {
        case "createdByMe":
          return t.created_by === currentUserId
        case "assignedToMe":
          return t.assigned_to === currentUserId
        default:
          return true
      }
    })
    setFilteredTasks(filteredTasks)
  }, [tasks, filterMode, currentUserId])

  return (
    <div className="task-container">
      <h1>Your Tasks</h1>
      <div>
        <span>Filter by:</span>
        <input type="radio" name="filter" id="all" onClick={() => setFilterMode("all")} checked={filterMode === "all"} />
        <label for="all">All tasks</label>
        <input type="radio" name="filter" id="createdByMe" onClick={() => setFilterMode("createdByMe")} checked={filterMode === "createdByMe"} />
        <label for="createdByMe">Created by me</label>
        <input type="radio" name="filter" id="assignedToMe" onClick={() => setFilterMode("assignedToMe")} checked={filterMode === "assignedToMe"} />
        <label for="assignedToMe">Assigned to me</label>
      </div>
      <div className="task-list">
        {Array.isArray(filteredTasks) && filteredTasks.map((task) => <Task task={task} />)}
      </div>
    </div>
  );
}
