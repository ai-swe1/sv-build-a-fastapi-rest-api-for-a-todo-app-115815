import React, { useEffect, useState, FormEvent } from 'react';
import {
  fetchTodos,
  createTodo,
  updateTodo,
  deleteTodo,
} from '../api/todoService';
import { Todo } from '../types';
import styles from './TodoApp.module.css';

const TodoApp: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTitle, setNewTitle] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadTodos = async () => {
    try {
      const data = await fetchTodos();
      setTodos(data);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  useEffect(() => {
    loadTodos();
  }, []);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) {
      setError('Title is required');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const created = await createTodo({ title: newTitle.trim(), completed: false });
      setTodos((prev) => [...prev, created]);
      setNewTitle('');
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const toggleComplete = async (todo: Todo) => {
    const updated = { ...todo, completed: !todo.completed };
    try {
      const result = await updateTodo(updated);
      setTodos((prev) => prev.map((t) => (t.id === result.id ? result : t)));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteTodo(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleEdit = async (id: number, newTitle: string) => {
    if (!newTitle.trim()) {
      setError('Title cannot be empty');
      return;
    }
    const todo = todos.find((t) => t.id === id);
    if (!todo) return;
    const updated = { ...todo, title: newTitle.trim() };
    try {
      const result = await updateTodo(updated);
      setTodos((prev) => prev.map((t) => (t.id === result.id ? result : t)));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.header}>Todo List</h1>
      <form className={styles.form} onSubmit={handleAdd}>
        <input
          className={styles.input}
          type="text"
          placeholder="Add new todo"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          disabled={loading}
        />
        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add'}
        </button>
      </form>
      {error && <div className={styles.error}>{error}</div>}
      <ul className={styles.list}>
        {todos.map((todo) => (
          <li key={todo.id} className={styles.item}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleComplete(todo)}
            />
            <EditableTitle
              title={todo.title}
              onSave={(newTitle) => handleEdit(todo.id, newTitle)}
            />
            <div className={styles.actions}>
              <button
                className={styles.button}
                onClick={() => handleDelete(todo.id)}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

interface EditableTitleProps {
  title: string;
  onSave: (newTitle: string) => void;
}

const EditableTitle: React.FC<EditableTitleProps> = ({ title, onSave }) => {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(title);

  const handleBlur = () => {
    if (value !== title) {
      onSave(value);
    }
    setEditing(false);
  };

  return editing ? (
    <input
      className={styles.title}
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onBlur={handleBlur}
      autoFocus
    />
  ) : (
    <span className={styles.title} onDoubleClick={() => setEditing(true)}>
      {title}
    </span>
  );
};

export default TodoApp;