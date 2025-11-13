import { useState } from "react";
import {
  Container,
  Flex,
  Typography,
  CellList,
  CellHeader,
  CellInput,
  Button,
  Textarea,
} from "@maxhub/max-ui";

const TaskDetailPage = ({ task, onClose, onSave, onDelete }) => {
  const [isEditing, setIsEditing] = useState(!task);
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [comment, setComment] = useState(task?.comment || "");
  const [tags, setTags] = useState(task?.tags || []);
  const [newTag, setNewTag] = useState("");
  const [category, setCategory] = useState(task?.category || "");
  const [deadline, setDeadline] = useState(task?.deadline || "");

  useBackButton(() => {
    onClose?.();
  }, { visible: true });

  const handleSave = () => {
    onSave?.({
      ...task,
      title,
      description,
      comment,
      tags,
      category,
      deadline,
    });
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDelete = () => {
    onDelete?.(task?.id);
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag("");
    }
  };

  const removeTag = (tagToRemove) => {
    if (isEditing) {
      setTags(tags.filter(tag => tag !== tagToRemove));
    }
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
              {category && (
                <Typography.Body variant="small" style={{ 
                  color: "var(--maxui_text_accent)", 
                  fontWeight: 600,
                  whiteSpace: "nowrap",
                  marginLeft: "12px"
                }}>
                  {category}
                </Typography.Body>
              )}
            </Flex>
            {task?.id && (
              <Typography.Body variant="small" style={{ color: "var(--maxui_text_secondary)" }}>
                ID: #{task.id}
              </Typography.Body>
            )}
          </Flex>
        </Container>

        {/* Main Info */}
        <CellList mode="island" header={<CellHeader>Основная информация</CellHeader>} style={{ width: "100%" }}>
          <CellInput
            before="Название"
            placeholder="Введите название задачи"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={!isEditing}
          />
          <CellInput
            before="Категория"
            placeholder="Например: Работа, Личное"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            disabled={!isEditing}
          />
          <CellInput
            before="Дедлайн"
            placeholder="15.11.2025 14:00"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            disabled={!isEditing}
          />
        </CellList>

        {/* Tags */}
        <CellList mode="island" header={<CellHeader>Теги</CellHeader>} style={{ width: "100%" }}>
          {tags.length > 0 && (
            <div style={{ padding: "12px 16px" }}>
              <Flex gap={8} wrap="wrap" style={{ width: "100%" }}>
                {tags.map((tag, index) => (
                  <div
                    key={index}
                    onClick={() => removeTag(tag)}
                    style={{
                      padding: "6px 12px",
                      backgroundColor: "var(--maxui_background_accent_themed)",
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
                      opacity: isEditing ? 1 : 0.7
                    }}
                  >
                    {tag}
                    {isEditing && <span style={{ fontSize: "16px", lineHeight: 1 }}>×</span>}
                  </div>
                ))}
              </Flex>
            </div>
          )}
          {isEditing && (
          <div style={{ padding: "12px 16px", borderTop: tags.length > 0 ? "1px solid var(--maxui_separator_primary)" : "none" }}>
            <Flex gap={8} style={{ width: "100%" }}>
              <input
                type="text"
                placeholder="Добавить тег"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addTag()}
                style={{
                  flex: 1,
                  padding: "8px 12px",
                  border: "1px solid var(--maxui_separator_primary)",
                  borderRadius: "8px",
                  fontSize: "15px",
                  backgroundColor: "var(--maxui_background_content)",
                  color: "var(--maxui_text_primary)",
                  outline: "none"
                }}
              />
              <Button
                size="medium"
                mode="secondary"
                appearance="themed"
                onClick={addTag}
              >
                Добавить
              </Button>
            </Flex>
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
                disabled={!title.trim()}
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
        </Container>
      </Flex>
    </div>
  );
};

export default TaskDetailPage;
