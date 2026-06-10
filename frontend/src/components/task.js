export default function Task({ task }) {
  return (
    <a href={`/task/${task.id}`}>
      <div class="task">
        <h3>[{task.completed ? "✓" : " "}] {task.title}</h3>
        <p>{task.description}</p>
        <p>Due: {task.due ? new Date(task.due).toLocaleString() : "No due date"}</p>
      </div>
    </a>
  );
}
