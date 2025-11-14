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

import { useBackButton } from "../hooks/useWebApp";

import { RiRobot2Fill, RiPencilFill } from "react-icons/ri";

const CreateTaskModal = ({ categories = [], onClose, onCreateManual, onGenerateAI }) => {
  const [mode, setMode] = useState("ai"); // "ai" или "manual"
  const [categoryId, setCategoryId] = useState(categories[0]?.id || null);
  
  // Для AI генерации
  const [prompt, setPrompt] = useState("");
  
  // Для ручного создания
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [deadline, setDeadline] = useState("");

  useBackButton(() => {
    onClose?.();
  }, { visible: true });

  const handleCreate = () => {
    if (!categoryId) {
      alert('Выберите категорию');
      return;
    }

    if (mode === "ai") {
      if (!prompt.trim()) {
        alert('Введите описание для генерации задачи');
        return;
      }
      onGenerateAI?.({
        prompt,
        category_id: categoryId,
      });
    } else {
      if (!title.trim()) {
        alert('Введите название задачи');
        return;
      }
      onCreateManual?.({
        title,
        description,
        category_id: categoryId,
        expiration_date: deadline ? new Date(deadline).toISOString() : null,
      });
    }
  };

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px 16px 100px 16px" }}>
      <Flex direction="column" gap={20} style={{ width: "100%" }}>
        {/* Header */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Typography.Headline variant="large-strong">
            Новая задача
          </Typography.Headline>
        </Container>

        {/* Mode Selector */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex gap={8} style={{ width: "100%" }}>
            <Button
              size="medium"
              mode={mode === "ai" ? "primary" : "secondary"}
              appearance={mode === "ai" ? "themed" : "neutral"}
              stretched
              onClick={() => setMode("ai")}
            >
              <RiRobot2Fill style={{ marginRight: 8 }} /> AI генерация
            </Button>
            <Button
              size="medium"
              mode={mode === "manual" ? "primary" : "secondary"}
              appearance={mode === "manual" ? "themed" : "neutral"}
              stretched
              onClick={() => setMode("manual")}
            >
              <RiPencilFill style={{ marginRight: 8 }} /> Вручную
            </Button>
          </Flex>
        </Container>

        {/* Category Selection */}
        <CellList mode="island" header={<CellHeader>Категория</CellHeader>} style={{ width: "100%" }}>
          <div style={{ padding: '12px 16px' }}>
            <select
              value={categoryId || ''}
              onChange={(e) => setCategoryId(Number(e.target.value))}
              disabled={categories.length === 0}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid var(--maxui_separator_primary)',
                borderRadius: '8px',
                fontSize: '15px',
                backgroundColor: 'var(--maxui_background_content)',
                color: 'var(--maxui_text_primary)',
                outline: 'none',
                cursor: categories.length === 0 ? 'not-allowed' : 'pointer',
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
          </div>
        </CellList>

        {/* AI Mode */}
        {mode === "ai" && (
          <CellList mode="island" header={<CellHeader>Описание для AI</CellHeader>} style={{ width: "100%" }}>
            <div style={{ padding: '12px 16px' }}>
              <Textarea
                mode="secondary"
                placeholder="Опишите задачу своими словами, и AI создаст структурированную задачу с названием, описанием и подходящими тегами...&#10;&#10;Например: 'Нужно сделать презентацию по итогам квартала для встречи с инвесторами до пятницы'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={8}
                style={{ 
                  width: "100%", 
                  fontSize: "15px",
                  lineHeight: "1.5"
                }}
              />
              <Typography.Body variant="small" style={{ color: 'var(--maxui_text_secondary)', marginTop: '8px' }}>
                <RiRobot2Fill style={{ marginRight: 8 }} /> AI автоматически создаст заголовок, описание и подберёт подходящие теги
              </Typography.Body>
            </div>
          </CellList>
        )}

        {/* Manual Mode */}
        {mode === "manual" && (
          <>
            <CellList mode="island" header={<CellHeader>Основная информация</CellHeader>} style={{ width: "100%" }}>
              <CellInput
                before="Название"
                placeholder="Название задачи"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <CellInput
                before="Дедлайн"
                type="datetime-local"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
            </CellList>

            <CellList mode="island" header={<CellHeader>Описание</CellHeader>} style={{ width: "100%" }}>
              <div style={{ padding: '12px 16px' }}>
                <Textarea
                  mode="secondary"
                  placeholder="Подробное описание задачи..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={6}
                  style={{ 
                    width: "100%", 
                    resize: "vertical",
                    fontSize: "15px",
                    lineHeight: "1.5"
                  }}
                />
              </div>
            </CellList>
          </>
        )}

        {/* Actions */}
        <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
          <Flex gap={8} style={{ width: "100%" }}>
            <Button
              size="large"
              mode="secondary"
              appearance="neutral"
              stretched
              onClick={onClose}
            >
              Отмена
            </Button>
            <Button
              size="large"
              mode="primary"
              appearance="themed"
              stretched
              onClick={handleCreate}
              disabled={
                !categoryId || 
                (mode === "ai" ? !prompt.trim() : !title.trim())
              }
            >
              {mode === "ai" ? <><RiRobot2Fill style={{ marginRight: 8 }} /> Сгенерировать</> : <><RiPencilFill style={{ marginRight: 8 }} /> Создать</>}
            </Button>
          </Flex>
        </Container>
      </Flex>
    </div>
  );
};

export default CreateTaskModal;
