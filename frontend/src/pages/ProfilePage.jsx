import { useState, useMemo } from "react";
import {
  Container,
  Flex,
  Avatar,
  Typography,
  CellList,
  CellHeader,
  CellSimple,
} from "@maxhub/max-ui";
import { useWebApp } from "../hooks/useWebApp";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import "./ProfilePage.css";

const ProfilePage = () => {
  const { user, firstName, lastName, photoUrl } = useWebApp();
  const [selectedDate, setSelectedDate] = useState(new Date());

  const displayName = firstName || lastName ? `${firstName} ${lastName}` : user?.username || "Пользователь";
  const fallback = firstName || lastName ? `${firstName[0]}${lastName[0]}` : "ME";

  const tasks = [
    { id: 1, title: "Задача 1", completed: true, createdAt: "2025-11-10", completedAt: "2025-11-11" },
    { id: 2, title: "Задача 2", completed: true, createdAt: "2025-11-10", completedAt: "2025-11-12" },
    { id: 3, title: "Задача 3", completed: false, createdAt: "2025-11-11", completedAt: null },
    { id: 4, title: "Задача 4", completed: true, createdAt: "2025-11-12", completedAt: "2025-11-13" },
    { id: 5, title: "Задача 5", completed: false, createdAt: "2025-11-13", completedAt: null },
  ];

  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const pending = total - completed;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    const tasksByDate = {};
    tasks.forEach(task => {
      const date = task.completedAt || task.createdAt;
      if (!tasksByDate[date]) {
        tasksByDate[date] = { completed: 0, pending: 0 };
      }
      if (task.completed) {
        tasksByDate[date].completed++;
      } else {
        tasksByDate[date].pending++;
      }
    });

    return { total, completed, pending, completionRate, tasksByDate };
  }, [tasks]);

  const tasksForSelectedDate = useMemo(() => {
    const dateStr = selectedDate.toISOString().split('T')[0];
    return tasks.filter(task => {
      const taskDate = task.completedAt || task.createdAt;
      return taskDate === dateStr;
    });
  }, [selectedDate, tasks]);

  const tileContent = ({ date, view }) => {
    if (view === 'month') {
      const dateStr = date.toISOString().split('T')[0];
      const dayStats = stats.tasksByDate[dateStr];
      if (dayStats) {
        return (
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2px', marginTop: '2px' }}>
            {dayStats.completed > 0 && (
              <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: 'var(--max_color_positive)' }} />
            )}
            {dayStats.pending > 0 && (
              <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: 'var(--max_color_warning)' }} />
            )}
          </div>
        );
      }
    }
    return null;
  };

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px", paddingBottom: "80px" }}>
      <Flex direction="column" gap={16} style={{ width: "100%" }}>
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex direction="column" align="center" gap={16} style={{ width: "100%" }}>
            <Avatar.Container size={96} rightBottomCorner={<Avatar.OnlineDot />}>
              <Avatar.Image
                fallback={fallback}
                src={photoUrl}
              />
            </Avatar.Container>

            <Flex direction="column" align="center" style={{ width: "100%" }}>
              <Typography.Headline variant="large-strong">
                {displayName}
              </Typography.Headline>
            </Flex>
          </Flex>
        </Container>

        <CellList style={{ width: "100%", maxWidth: "100%" }}>
          <CellHeader>Общая статистика</CellHeader>
          <CellSimple
            title="Всего задач"
            after={<Typography.Body variant="medium-strong">{stats.total}</Typography.Body>}
          />
          <CellSimple
            title="Выполнено"
            after={<Typography.Body variant="medium-strong" style={{ color: 'var(--max_color_positive)' }}>{stats.completed}</Typography.Body>}
          />
          <CellSimple
            title="В процессе"
            after={<Typography.Body variant="medium-strong" style={{ color: 'var(--max_color_warning)' }}>{stats.pending}</Typography.Body>}
          />
          <CellSimple
            title="Процент выполнения"
            after={<Typography.Body variant="medium-strong">{stats.completionRate}%</Typography.Body>}
          />
        </CellList>

        <div style={{ width: "100%" }}>
          <Typography.Headline variant="medium-strong" style={{ marginBottom: '12px', paddingLeft: '4px' }}>
            Календарь задач
          </Typography.Headline>
          <Container style={{ 
            width: "100%", 
            padding: '12px',
            '--react-calendar-navigation-height': '44px',
            '--react-calendar-tile-height': '44px',
          }}>
            <Calendar
              onChange={setSelectedDate}
              value={selectedDate}
              locale="ru-RU"
              tileContent={tileContent}
              className="max-calendar"
            />
          </Container>
        </div>

        {tasksForSelectedDate.length > 0 && (
          <CellList style={{ width: "100%", maxWidth: "100%" }}>
            <CellHeader>
              Задачи на {selectedDate.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })}
            </CellHeader>
            {tasksForSelectedDate.map(task => (
              <CellSimple
                key={task.id}
                title={task.title}
                after={
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: task.completed ? 'var(--max_color_positive)' : 'var(--max_color_warning)'
                  }} />
                }
              />
            ))}
          </CellList>
        )}
      </Flex>
    </div>
  );
};

export default ProfilePage;
