import { useState, useEffect } from "react";
import { Container, Flex, Typography, CellList, CellSimple, CellHeader, Button, SearchInput, Spinner } from "@maxhub/max-ui";
import { useWebApp } from "../hooks/useWebApp";
import apiService from "../services/api";
import TaskDetailPage from "./TaskDetailPage";
import CreateTaskModal from "../components/CreateTaskModal";

const TasksPage = () => {
  const { userId } = useWebApp();
  const [selectedTask, setSelectedTask] = useState(null);
  const [showNewTask, setShowNewTask] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (userId) {
      setLoading(true);
      loadTasks();
      loadCategories();
    }
  }, [userId]);

  const loadTasks = async (search = searchQuery) => {
    try {
      const data = await apiService.getTasks({ 
        max_user_id: userId,
        search: search || undefined 
      });
      setTasks(data);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setError('Не удалось загрузить задачи');
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await apiService.getUserCategories(userId);
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  useEffect(() => {
    if (!userId) return;
    
    // Не делаем запрос для очень коротких запросов (меньше 3 символов)
    if (searchQuery && searchQuery.trim().length > 0 && searchQuery.trim().length < 3) {
      return;
    }
    
    const timer = setTimeout(() => {
      loadTasks(searchQuery);
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchQuery, userId]);

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.name || '';
  };

  const filteredTasks = tasks;

  const handleGenerateTask = async (data) => {
    try {
      await apiService.generateTask({
        max_user_id: userId,
        prompt: data.prompt,
        category_id: data.category_id
      });
      await loadTasks();
      setShowNewTask(false);
    } catch (err) {
      console.error('Failed to generate task:', err);
      alert('Ошибка при генерации задачи');
    }
  };

  const handleCreateManualTask = async (data) => {
    try {
      await apiService.createTask({
        max_user_id: userId,
        title: data.title,
        description: data.description || null,
        category_id: data.category_id,
        expiration_date: data.expiration_date
      });
      await loadTasks();
      setShowNewTask(false);
    } catch (err) {
      console.error('Failed to create task:', err);
      alert('Ошибка при создании задачи');
    }
  };

  const handleUpdateTask = async (updatedTask) => {
    try {
      setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
    } catch (err) {
      console.error('Failed to update task in list:', err);
    }
  };

  const handleDeleteTask = async (id) => {
    try {
      await apiService.deleteTask(id);
      await loadTasks();
      setSelectedTask(null);
    } catch (err) {
      console.error('Failed to delete task:', err);
      alert('Ошибка при удалении задачи');
    }
  };

  if (showNewTask) {
    return (
      <CreateTaskModal
        categories={categories}
        onClose={() => setShowNewTask(false)}
        onGenerateAI={handleGenerateTask}
        onCreateManual={handleCreateManualTask}
      />
    );
  }

  if (selectedTask) {
    return (
      <TaskDetailPage
        task={selectedTask}
        categories={categories}
        onClose={() => setSelectedTask(null)}
        onSave={handleUpdateTask}
        onDelete={handleDeleteTask}
      />
    );
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
          {error}
        </Typography.Body>
      </div>
    );
  }

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px" }}>
    <Flex direction="column" gap={16} style={{ width: "100%" }}>
      <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
        <Flex direction="row" justify="space-between" align="center" style={{ width: "100%", marginBottom: "12px" }}>
          <Typography.Headline variant="large-strong">Задачи</Typography.Headline>
          <Button
            size="medium"
            mode="primary"
            appearance="themed"
            onClick={() => setShowNewTask(true)}
          >
            Создать
          </Button>
        </Flex>
        <SearchInput
          placeholder="Поиск задач..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: "100%" }}
        />
      </Container>

      {filteredTasks.length === 0 ? (
        <Container style={{ textAlign: 'center', padding: '40px 16px' }}>
          <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
            {searchQuery ? 'Задачи не найдены' : 'У вас пока нет задач'}
          </Typography.Body>
        </Container>
      ) : (
        <CellList mode="island" header={<CellHeader>Все задачи</CellHeader>} style={{ width: "100%" }}>
          {filteredTasks.map(task => (
            <CellSimple
              key={task.id}
              showChevron
              title={task.title}
              subtitle={
                <div>
                  {task.description && <div>{task.description.substring(0, 60)}{task.description.length > 60 ? '...' : ''}</div>}
                  <div style={{ color: 'var(--maxui_text_accent)', fontSize: '13px', marginTop: '4px' }}>
                    {getCategoryName(task.category_id)}
                  </div>
                </div>
              }
              onClick={() => setSelectedTask(task)}
            />
          ))}
        </CellList>
      )}
    </Flex>
    </div>
  );
};

export default TasksPage;
