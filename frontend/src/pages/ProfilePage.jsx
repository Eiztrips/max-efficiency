import { useState, useMemo, useEffect } from "react";
import {
  Container,
  Flex,
  Avatar,
  Typography,
  CellList,
  CellHeader,
  CellSimple,
  Spinner,
} from "@maxhub/max-ui";
import { useWebApp } from "../hooks/useWebApp";
import apiService from "../services/api";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import "./ProfilePage.css";

import { FaRegClipboard, FaCheck } from "react-icons/fa6";

const ProfilePage = () => {
  const { user, userId, firstName, lastName, photoUrl } = useWebApp();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [tasks, setTasks] = useState([]);
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(false);

  const displayName = firstName || lastName ? `${firstName} ${lastName}` : user?.username || "Пользователь";
  const fallback = firstName || lastName ? `${firstName[0]}${lastName[0]}` : "ME";

  useEffect(() => {
    if (userId) {
      loadTasks();
      loadUser();
    }
  }, [userId]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await apiService.getUserTasks(userId);
      setTasks(data);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUser = async () => {
    try {
      const userData = await apiService.getUserProfile(userId);
      setUserData(userData);
    } catch (err) {
      console.error('Failed to load user data:', err);
    }
  };


  const handleCopyId = () => {
    if (userId) {
      navigator.clipboard.writeText(userId.toString());
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.is_completed).length;
    const pending = total - completed;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    const ownedCategories = userData?.categories_owned?.length || 0;
    const joinedCategories = userData?.categories_joined?.length || 0;

    const tasksByDate = {};
    tasks.forEach(task => {
      const date = task.updated_at ? task.updated_at.split('T')[0] : task.created_at.split('T')[0];
      if (!tasksByDate[date]) {
        tasksByDate[date] = { completed: 0, pending: 0 };
      }
      if (task.is_completed) {
        tasksByDate[date].completed++;
      } else {
        tasksByDate[date].pending++;
      }
    });

    return { total, completed, pending, completionRate, ownedCategories, joinedCategories, tasksByDate };
  }, [tasks, user]);

  const tasksForSelectedDate = useMemo(() => {
    const dateStr = selectedDate.toISOString().split('T')[0];
    return tasks.filter(task => {
      if(!task.expiration_date) return false;
      const taskDate = task.expiration_date ? task.expiration_date.split('T')[0] : task.expiration_date.split('T')[0];
      return taskDate === dateStr;
    });
  }, [selectedDate, tasks]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="large" />
      </div>
    );
  }

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
              <Flex 
                align="center" 
                gap={8} 
                style={{ 
                  marginTop: '4px',
                  padding: '6px 12px',
                  backgroundColor: 'var(--maxui_background_secondary)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onClick={handleCopyId}
              >
                <Typography.Body variant="small" style={{ color: "var(--maxui_text_secondary)" }}>
                  MAX ID: {userId}
                </Typography.Body>
                <Typography.Body variant="small" style={{ color: "var(--maxui_text_accent)" }}>
                  {copiedId ? <><FaCheck /> Скопировано</> : <><FaRegClipboard /> Копировать</>}
                </Typography.Body>
              </Flex>
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

        <CellList style={{ width: "100%", maxWidth: "100%" }}>
          <CellHeader>Категории</CellHeader>
          <CellSimple
            title="Мои категории"
            after={<Typography.Body variant="medium-strong">{stats.ownedCategories}</Typography.Body>}
          />
          <CellSimple
            title="Участвую в категориях"
            after={<Typography.Body variant="medium-strong">{stats.joinedCategories}</Typography.Body>}
          />
          <CellSimple
            title="Всего категорий"
            after={<Typography.Body variant="medium-strong">{stats.ownedCategories + stats.joinedCategories}</Typography.Body>}
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
                    backgroundColor: task.is_completed ? 'var(--max_color_positive)' : 'var(--max_color_warning)'
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
