import { useState, useEffect } from "react";
import {
  Container,
  Flex,
  Typography,
  CellList,
  CellSimple,
  CellHeader,
  CellInput,
  Button,
  Spinner,
  Counter,
} from "@maxhub/max-ui";

import { useBackButton } from "../hooks/useWebApp";
import apiService from "../services/api";

const CategoryDetailModal = ({ category, onClose, onUpdate, onDelete }) => {
  const [users, setUsers] = useState([]);
  const [tags, setTags] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingTags, setLoadingTags] = useState(true);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [newUserId, setNewUserId] = useState("");

  useBackButton(() => {
    onClose?.();
  }, { visible: true });

  useEffect(() => {
    if (category?.id) {
      loadCategoryData();
    }
  }, [category?.id]);

  const loadCategoryData = async () => {
    try {
      const [usersData, tagsData, tasksData] = await Promise.all([
        apiService.getCategoryUsers(category.id).catch(() => []),
        apiService.getCategoryTags(category.id).catch(() => []),
        apiService.getCategoryTasks(category.id).catch(() => []),
      ]);
      
      setUsers(usersData);
      setTags(tagsData);
      setTasks(tasksData);
    } catch (err) {
      console.error('Failed to load category data:', err);
    } finally {
      setLoadingUsers(false);
      setLoadingTags(false);
      setLoadingTasks(false);
    }
  };

  const handleAddUser = async () => {
    const userId = parseInt(newUserId.trim());
    if (!userId || isNaN(userId)) {
      alert('Введите корректный ID пользователя');
      return;
    }

    try {
      await apiService.addUserToCategory(category.id, userId, {
        id: category.id,
        max_user_id: userId
      });
      setNewUserId("");
      await loadCategoryData();
      onUpdate?.();
    } catch (err) {
      console.error('Failed to add user:', err);
      alert('Ошибка при добавлении пользователя');
    }
  };

  const handleRemoveUser = async (userId) => {
    if (!confirm('Удалить пользователя из категории?')) return;

    try {
      await apiService.removeUserFromCategory(category.id, userId);
      await loadCategoryData();
      onUpdate?.();
    } catch (err) {
      console.error('Failed to remove user:', err);
      alert('Ошибка при удалении пользователя');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Вы уверены, что хотите удалить эту категорию? Все связанные задачи и теги также будут удалены.')) {
      return;
    }

    try {
      await apiService.deleteCategory(category.id);
      onDelete?.(category.id);
    } catch (err) {
      console.error('Failed to delete category:', err);
      alert('Ошибка при удалении категории');
    }
  };

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px 16px 100px 16px" }}>
      <Flex direction="column" gap={20} style={{ width: "100%" }}>
        {/* Header */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex direction="column" gap={8} style={{ width: "100%" }}>
            <Typography.Headline variant="large-strong">
              {category.name}
            </Typography.Headline>
            {category.description && (
              <Typography.Body variant="medium" style={{ color: "var(--maxui_text_secondary)" }}>
                {category.description}
              </Typography.Body>
            )}
            <Typography.Body variant="small" style={{ color: "var(--maxui_text_secondary)" }}>
              ID: #{category.id}
            </Typography.Body>
          </Flex>
        </Container>

        {/* Statistics */}
        <CellList mode="island" header={<CellHeader>Статистика</CellHeader>} style={{ width: "100%" }}>
          <CellSimple
            title="Задач"
            after={<Counter value={tasks.length} rounded />}
          />
          <CellSimple
            title="Тегов"
            after={<Counter value={tags.length} rounded />}
          />
          <CellSimple
            title="Участников"
            after={<Counter value={users.length} rounded />}
          />
        </CellList>

        {/* Users */}
        <CellList mode="island" header={<CellHeader>Участники</CellHeader>} style={{ width: "100%" }}>
          {loadingUsers ? (
            <div style={{ padding: '20px', textAlign: 'center' }}>
              <Spinner size="medium" />
            </div>
          ) : users.length === 0 ? (
            <div style={{ padding: '16px', textAlign: 'center' }}>
              <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
                Нет участников
              </Typography.Body>
            </div>
          ) : (
            users.map(user => (
              <CellSimple
                key={user.id}
                title={user.username || `User #${user.max_user_id}`}
                subtitle={`ID: ${user.max_user_id}`}
                after={
                  user.id !== category.owner_id && (
                    <Button
                      size="small"
                      mode="secondary"
                      appearance="negative"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveUser(user.max_user_id);
                      }}
                    >
                      Удалить
                    </Button>
                  )
                }
              />
            ))
          )}
          
          {/* Add User Form */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid var(--maxui_separator_primary)' }}>
            <Flex direction="column" gap={8}>
              <Typography.Body variant="medium" style={{ fontWeight: 500 }}>
                Добавить участника
              </Typography.Body>
              <Flex gap={8} align="center">
                <input
                  type="number"
                  placeholder="ID пользователя"
                  value={newUserId}
                  onChange={(e) => setNewUserId(e.target.value)}
                  style={{
                    flex: 1,
                    padding: '10px 12px',
                    border: '1px solid var(--maxui_separator_primary)',
                    borderRadius: '8px',
                    fontSize: '15px',
                    backgroundColor: 'var(--maxui_background_content)',
                    color: 'var(--maxui_text_primary)',
                    outline: 'none'
                  }}
                />
                <Button
                  size="medium"
                  mode="primary"
                  appearance="themed"
                  onClick={handleAddUser}
                  disabled={!newUserId.trim()}
                >
                  Добавить
                </Button>
              </Flex>
            </Flex>
          </div>
        </CellList>

        {/* Tags */}
        {tags.length > 0 && (
          <CellList mode="island" header={<CellHeader>Теги категории</CellHeader>} style={{ width: "100%" }}>
            <div style={{ padding: '12px 16px' }}>
              <Flex gap={8} wrap="wrap" style={{ width: "100%" }}>
                {tags.map(tag => (
                  <div
                    key={tag.id}
                    style={{
                      padding: "6px 12px",
                      backgroundColor: tag.color || "var(--maxui_background_accent_themed)",
                      color: "var(--maxui_text_contrast)",
                      borderRadius: "12px",
                      fontSize: "14px",
                      fontWeight: 500,
                    }}
                  >
                    {tag.name}
                  </div>
                ))}
              </Flex>
            </div>
          </CellList>
        )}

        {/* Actions */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Button
            size="large"
            mode="secondary"
            appearance="negative"
            stretched
            onClick={handleDelete}
          >
            Удалить категорию
          </Button>
        </Container>
      </Flex>
    </div>
  );
};

export default CategoryDetailModal;
