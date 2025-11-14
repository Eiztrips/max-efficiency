import { useState, useEffect } from "react";
import {
  Container,
  Flex,
  Typography,
  CellList,
  CellHeader,
  CellInput,
  Button,
  Textarea,
  Spinner,
} from "@maxhub/max-ui";

import { useBackButton } from "../hooks/useWebApp";
import apiService from "../services/api";

import { GiBackwardTime, GiCheckMark } from "react-icons/gi";

const TaskDetailPage = ({ task, categories = [], onClose, onSave, onDelete }) => {
  const [isEditing, setIsEditing] = useState(!task);
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [comment, setComment] = useState(task?.comment || "");
  const [prompt, setPrompt] = useState("");
  const [selectedTagIds, setSelectedTagIds] = useState(task?.tags || []);
  const [availableTags, setAvailableTags] = useState([]);
  const [loadingTags, setLoadingTags] = useState(false);
  const [categoryId, setCategoryId] = useState(task?.category_id || (categories[0]?.id || null));
  const [deadline, setDeadline] = useState(task?.expiration_date ? new Date(task.expiration_date).toISOString().slice(0, 16) : "");

  useBackButton(() => {
    onClose?.();
  }, { visible: true });

  useEffect(() => {
    if (categoryId) {
      loadCategoryTags();
    }
  }, [categoryId]);

  const loadCategoryTags = async () => {
    try {
      setLoadingTags(true);
      const tags = await apiService.getCategoryTags(categoryId);
      setAvailableTags(tags);
    } catch (err) {
      console.error('Failed to load tags:', err);
    } finally {
      setLoadingTags(false);
    }
  };

  const handleSave = async () => {
    if (!task && !prompt.trim()) {
      alert('Введите описание задачи');
      return;
    }
    if (!categoryId) {
      alert('Выберите категорию');
      return;
    }
    
    if (task && isEditing) {
      try {

        const originalTagIds = task.tags || [];
        const tagsChanged = originalTagIds.length !== selectedTagIds.length || 
          !originalTagIds.every(id => selectedTagIds.includes(id));
        
        const originalDeadline = task.expiration_date ? new Date(task.expiration_date).toISOString().slice(0, 16) : "";
        const taskDataChanged = title !== task.title || 
          description !== task.description || 
          deadline !== originalDeadline || 
          categoryId !== task.category_id;
        
        if (!tagsChanged && !taskDataChanged) {
          setIsEditing(false);
          return;
        }
        
        if (tagsChanged) {
          await apiService.updateTaskTags(task.id, selectedTagIds);
        }
        
        if (taskDataChanged) {
          await apiService.updateTask(task.id, {
            title,
            description,
            expiration_date: deadline ? new Date(deadline).toISOString() : null,
            category_id: categoryId
          });
        }
        
        if (onSave) {
          const updatedTask = await apiService.getTask(task.id);
          onSave(updatedTask);
        }
        
        onClose?.();
      } catch (err) {
        console.error('Failed to update task:', err);
        alert('Ошибка при обновлении задачи');
      }
      return;
    }
    
    onSave?.({
      ...task,
      title,
      description,
      prompt,
      comment,
      tags: selectedTagIds,
      category_id: categoryId,
      expiration_date: deadline ? new Date(deadline).toISOString() : null,
    });
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDelete = () => {
    onDelete?.(task?.id);
  };

  const handleToggleComplete = async () => {
    if (!task) return;
    
    try {
      await apiService.updateTask(task.id, {
        is_completed: !task.is_completed
      });
      
      if (onSave) {
        const updatedTask = await apiService.getTask(task.id);
        onSave(updatedTask);
      }
      
      onClose?.();
    } catch (err) {
      console.error('Failed to toggle task completion:', err);
      alert('Ошибка при изменении статуса задачи');
    }
  };

  const toggleTag = (tagId) => {
    if (!isEditing) return;
    
    if (selectedTagIds.includes(tagId)) {
      setSelectedTagIds(selectedTagIds.filter(id => id !== tagId));
    } else {
      setSelectedTagIds([...selectedTagIds, tagId]);
    }
  };

  const getTagById = (tagId) => {
    return availableTags.find(tag => tag.id === tagId);
  };

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px 16px 100px 16px" }}>
      <Flex direction="column" gap={20} style={{ width: "100%" }}>
        {/* Header */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex direction="column" gap={8} style={{ width: "100%" }}>
            <Flex direction="row" justify="space-between" align="center" style={{ width: "100%" }}>
              <Typography.Headline variant="large-strong" style={{ flex: 1 }}>
                {title || "Новая задача"}
              </Typography.Headline>
              {categoryId && (
                <Typography.Body variant="small" style={{ 
                  color: "var(--maxui_text_accent)", 
                  fontWeight: 600,
                  whiteSpace: "nowrap",
                  marginLeft: "12px"
                }}>
                  {categories.find(c => c.id === categoryId)?.name || ''}
                </Typography.Body>
              )}
            </Flex>
            {task?.id && (
              <Flex direction="row" align="center" gap={8}>
                <Typography.Body variant="small" style={{ color: "var(--maxui_text_secondary)" }}>
                  ID: #{task.id}
                </Typography.Body>
                <div style={{
                  padding: "4px 8px",
                  backgroundColor: task.is_completed ? 'var(--maxui_background_positive)' : 'var(--maxui_background_warning)',
                  color: task.is_completed ? 'var(--maxui_text_positive)' : 'var(--maxui_text_warning)',
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontWeight: 600
                }}>
                  {task.is_completed ? '✓ Выполнено' : '⏳ В процессе'}
                </div>
              </Flex>
            )}
          </Flex>
        </Container>

        {/* Main Info */}
        <CellList mode="island" header={<CellHeader>Основная информация</CellHeader>} style={{ width: "100%" }}>
          {!task && isEditing && (
            <div style={{ padding: '12px 16px' }}>
              <Textarea
                mode="secondary"
                placeholder="Опишите задачу своими словами (ИИ создаст структурированную задачу)..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                style={{ 
                  width: "100%", 
                  fontSize: "15px",
                  lineHeight: "1.5"
                }}
              />
            </div>
          )}
          {task && (
            <CellInput
              before="Название"
              placeholder="Название задачи"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={!isEditing}
            />
          )}
          <div style={{ padding: '12px 16px', borderTop: '1px solid var(--maxui_separator_primary)' }}>
            <Flex direction="column" gap={8}>
              <Typography.Body variant="medium" style={{ fontWeight: 500 }}>Категория</Typography.Body>
              <select
                value={categoryId || ''}
                onChange={(e) => setCategoryId(Number(e.target.value))}
                disabled={!isEditing || categories.length === 0}
                style={{
                  padding: '10px 12px',
                  border: '1px solid var(--maxui_separator_primary)',
                  borderRadius: '8px',
                  fontSize: '15px',
                  backgroundColor: 'var(--maxui_background_content)',
                  color: 'var(--maxui_text_primary)',
                  outline: 'none',
                  cursor: isEditing ? 'pointer' : 'not-allowed',
                  opacity: isEditing ? 1 : 0.6
                }}
              >
                {categories.length === 0 ? (
                  <option value="">Нет доступных категорий</option>
                ) : (
                  categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))
                )}
              </select>
            </Flex>
          </div>
          <CellInput
            before="Дедлайн"
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            disabled={!isEditing}
          />
        </CellList>

        {/* Tags */}
        <CellList mode="island" header={<CellHeader>Теги</CellHeader>} style={{ width: "100%" }}>
          {selectedTagIds.length > 0 && (
            <div style={{ padding: "12px 16px" }}>
              <Flex gap={8} wrap="wrap" style={{ width: "100%" }}>
                {selectedTagIds.map((tagId) => {
                  const tag = getTagById(tagId);
                  if (!tag) return null;
                  return (
                    <div
                      key={tagId}
                      onClick={() => toggleTag(tagId)}
                      style={{
                        padding: "6px 12px",
                        backgroundColor: tag.color || "var(--maxui_background_accent_themed)",
                        color: "var(--maxui_text_contrast)",
                        borderRadius: "12px",
                        fontSize: "14px",
                        fontWeight: 500,
                        cursor: isEditing ? "pointer" : "default",
                        userSelect: "none",
                        transition: "all 0.2s",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        opacity: isEditing ? 1 : 0.7,
                        border: `2px solid ${tag.color || "var(--maxui_background_accent_themed)"}`
                      }}
                    >
                      {tag.name}
                      {isEditing && <span style={{ fontSize: "16px", lineHeight: 1 }}>×</span>}
                    </div>
                  );
                })}
              </Flex>
            </div>
          )}
          {isEditing && (
            <div style={{ padding: "12px 16px", borderTop: selectedTagIds.length > 0 ? "1px solid var(--maxui_separator_primary)" : "none" }}>
              {loadingTags ? (
                <Flex justify="center" style={{ padding: '20px' }}>
                  <Spinner size="medium" />
                </Flex>
              ) : availableTags.length === 0 ? (
                <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)', textAlign: 'center', padding: '20px' }}>
                  Нет доступных тегов в этой категории
                </Typography.Body>
              ) : (
                <>
                  <Typography.Body variant="small" style={{ marginBottom: '12px', color: 'var(--maxui_text_secondary)' }}>
                    Выберите теги из доступных:
                  </Typography.Body>
                  <Flex gap={8} wrap="wrap" style={{ width: "100%" }}>
                    {availableTags.filter(tag => !selectedTagIds.includes(tag.id)).map((tag) => (
                      <div
                        key={tag.id}
                        onClick={() => toggleTag(tag.id)}
                        style={{
                          padding: "6px 12px",
                          backgroundColor: 'transparent',
                          color: "var(--maxui_text_primary)",
                          border: `2px solid ${tag.color}`,
                          borderRadius: "12px",
                          fontSize: "14px",
                          fontWeight: 500,
                          cursor: "pointer",
                          userSelect: "none",
                          transition: "all 0.2s",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                      >
                        {tag.name}
                      </div>
                    ))}
                  </Flex>
                </>
              )}
            </div>
          )}
        </CellList>

        {/* Description */}
        <CellList mode="island" header={<CellHeader>Описание</CellHeader>} style={{ width: "100%" }}>
          <div style={{ padding: "12px 16px" }}>
            <Textarea
              mode="secondary"
              placeholder="Подробное описание задачи..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              disabled={!isEditing}
              style={{ 
                width: "100%", 
                resize: "vertical",
                fontSize: "15px",
                lineHeight: "1.5"
              }}
            />
          </div>
        </CellList>

        {/* Comment */}
        <CellList mode="island" header={<CellHeader>Комментарий</CellHeader>} style={{ width: "100%" }}>
          <div style={{ padding: "12px 16px" }}>
            <Textarea
              mode="secondary"
              placeholder="Дополнительные заметки или комментарии..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              disabled={!isEditing}
              style={{ 
                width: "100%", 
                resize: "vertical",
                fontSize: "15px",
                lineHeight: "1.5"
              }}
            />
          </div>
        </CellList>

        {/* Actions */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex direction="column" gap={8} style={{ width: "100%" }}>
            {task && !isEditing && (
              <Button
                size="large"
                mode="primary"
                appearance={task.is_completed ? "neutral" : "positive"}
                stretched
                onClick={handleToggleComplete}
              >
                {task.is_completed ? <><GiBackwardTime style={{ marginRight: 8 }} /> Вернуть в работу</> : <><GiCheckMark style={{ marginRight: 8 }} /> Отметить как выполненное</>}
              </Button>
            )}
            <Flex gap={8} style={{ width: "100%" }}>
              {task && (
                <Button
                  size="large"
                  mode="secondary"
                  appearance="negative"
                  stretched
                  onClick={handleDelete}
                >
                  Удалить
                </Button>
              )}
              {isEditing ? (
                <Button
                  size="large"
                  mode="primary"
                  appearance="themed"
                  stretched
                  onClick={handleSave}
                  disabled={task ? !title.trim() : !prompt.trim() || !categoryId}
                >
                  Сохранить
                </Button>
              ) : (
                <Button
                  size="large"
                  mode="primary"
                  appearance="themed"
                  stretched
                  onClick={handleEdit}
                >
                  Редактировать
                </Button>
              )}
            </Flex>
          </Flex>
        </Container>
      </Flex>
    </div>
  );
};

export default TaskDetailPage;
