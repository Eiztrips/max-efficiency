import { useState, useEffect } from "react";
import { Container, Flex, Typography, CellList, CellSimple, CellHeader, Button, Spinner } from "@maxhub/max-ui";
import { useWebApp } from "../hooks/useWebApp";
import apiService from "../services/api";

const TagsPage = () => {
  const { userId } = useWebApp();
  const [tags, setTags] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [newTagColor, setNewTagColor] = useState("#FFFFFF");
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);

  useEffect(() => {
    if (userId) {
      loadData();
    }
  }, [userId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tagsData, categoriesData] = await Promise.all([
        apiService.getUserTags(userId),
        apiService.getUserCategories(userId)
      ]);
      setTags(tagsData);
      setCategories(categoriesData);
      if (categoriesData.length > 0 && !selectedCategoryId) {
        setSelectedCategoryId(categoriesData[0].id);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim() || !selectedCategoryId) return;
    
    try {
      await apiService.createTag({
        category_id: selectedCategoryId,
        name: newTagName,
        color: newTagColor
      });
      setNewTagName("");
      setNewTagColor("#FFFFFF");
      setShowCreateForm(false);
      await loadData();
    } catch (err) {
      console.error('Failed to create tag:', err);
      alert('Ошибка при создании тега');
    }
  };

  const handleDeleteTag = async (id) => {
    if (!confirm('Вы уверены, что хотите удалить этот тег?')) return;
    
    try {
      await apiService.deleteTag(id);
      await loadData();
    } catch (err) {
      console.error('Failed to delete tag:', err);
      alert('Ошибка при удалении тега');
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.name || '';
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="large" />
      </div>
    );
  }

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px" }}>
    <Flex direction="column" gap={16} style={{ width: "100%" }}>
      <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
        <Flex direction="row" justify="space-between" align="center" style={{ width: "100%" }}>
          <Typography.Headline variant="large-strong">Теги</Typography.Headline>
          <Button
            size="medium"
            mode="primary"
            appearance="themed"
            onClick={() => setShowCreateForm(!showCreateForm)}
            disabled={categories.length === 0}
          >
            {showCreateForm ? 'Отмена' : 'Создать'}
          </Button>
        </Flex>
      </Container>

      {showCreateForm && (
        <Container style={{ width: "100%", padding: '16px' }}>
          <Flex direction="column" gap={12}>
            <select
              value={selectedCategoryId || ''}
              onChange={(e) => setSelectedCategoryId(Number(e.target.value))}
              style={{
                padding: '12px',
                border: '1px solid var(--maxui_separator_primary)',
                borderRadius: '8px',
                fontSize: '15px',
                backgroundColor: 'var(--maxui_background_content)',
                color: 'var(--maxui_text_primary)',
                outline: 'none'
              }}
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Название тега"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              style={{
                padding: '12px',
                border: '1px solid var(--maxui_separator_primary)',
                borderRadius: '8px',
                fontSize: '15px',
                backgroundColor: 'var(--maxui_background_content)',
                color: 'var(--maxui_text_primary)',
                outline: 'none'
              }}
            />
            <Flex gap={8} align="center">
              <input
                type="color"
                value={newTagColor}
                onChange={(e) => setNewTagColor(e.target.value)}
                style={{
                  width: '50px',
                  height: '40px',
                  border: '1px solid var(--maxui_separator_primary)',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              />
              <Typography.Body variant="medium">Цвет тега</Typography.Body>
            </Flex>
            <Button
              size="large"
              mode="primary"
              appearance="themed"
              stretched
              onClick={handleCreateTag}
              disabled={!newTagName.trim()}
            >
              Добавить тег
            </Button>
          </Flex>
        </Container>
      )}

      {error && (
        <Container style={{ textAlign: 'center', padding: '16px' }}>
          <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
            {error}
          </Typography.Body>
        </Container>
      )}

      {categories.length === 0 ? (
        <Container style={{ textAlign: 'center', padding: '40px 16px' }}>
          <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
            Сначала создайте категорию
          </Typography.Body>
        </Container>
      ) : tags.length === 0 ? (
        <Container style={{ textAlign: 'center', padding: '40px 16px' }}>
          <Typography.Body variant="medium" style={{ color: 'var(--maxui_text_secondary)' }}>
            У вас пока нет тегов
          </Typography.Body>
        </Container>
      ) : (
        <CellList mode="island" header={<CellHeader>Все теги</CellHeader>} style={{ width: "100%" }}>
          {tags.map(tag => (
            <CellSimple
              key={tag.id}
              showChevron
              title={tag.name}
              subtitle={getCategoryName(tag.category_id)}
              before={
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '6px',
                  backgroundColor: tag.color,
                  border: '1px solid var(--maxui_separator_primary)'
                }} />
              }
              onClick={() => handleDeleteTag(tag.id)}
            />
          ))}
        </CellList>
      )}
    </Flex>
    </div>
  );
};

export default TagsPage;
