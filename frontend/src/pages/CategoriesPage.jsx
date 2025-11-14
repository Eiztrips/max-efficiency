import { useState, useEffect } from "react";
import { Container, Flex, Typography, CellList, CellSimple, CellHeader, Counter, Button, Spinner } from "@maxhub/max-ui";
import { useWebApp } from "../hooks/useWebApp";
import apiService from "../services/api";
import CategoryDetailModal from "../components/CategoryDetailModal";

const CategoriesPage = () => {
  const { userId } = useWebApp();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newCategoryDesc, setNewCategoryDesc] = useState("");
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    if (userId) {
      loadCategories();
    }
  }, [userId]);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await apiService.getUserCategories(userId);
      setCategories(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load categories:', err);
      setError('Не удалось загрузить категории');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) return;
    
    try {
      await apiService.createCategory({
        max_user_id: userId,
        name: newCategoryName,
        description: newCategoryDesc || null
      });
      setNewCategoryName("");
      setNewCategoryDesc("");
      setShowCreateForm(false);
      await loadCategories();
    } catch (err) {
      console.error('Failed to create category:', err);
      alert('Ошибка при создании категории');
    }
  };

  const handleDeleteCategory = async (id) => {
    try {
      await loadCategories();
      setSelectedCategory(null);
    } catch (err) {
      console.error('Failed to refresh categories:', err);
    }
  };

  if (selectedCategory) {
    return (
      <CategoryDetailModal
        category={selectedCategory}
        onClose={() => setSelectedCategory(null)}
        onUpdate={loadCategories}
        onDelete={handleDeleteCategory}
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

  return (
    <div style={{ width: "100%", maxWidth: "640px", margin: "0 auto", padding: "16px" }}>
    <Flex direction="column" gap={16} style={{ width: "100%" }}>
      <Container style={{ width: "100%", maxWidth: "100%", paddingLeft: 0, paddingRight: 0 }}>
        <Flex direction="row" justify="space-between" align="center" style={{ width: "100%" }}>
          <Typography.Headline variant="large-strong">Категории</Typography.Headline>
          <Button
            size="medium"
            mode="primary"
            appearance="themed"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Отмена' : 'Создать'}
          </Button>
        </Flex>
      </Container>

      {showCreateForm && (
        <Container style={{ width: "100%", padding: '16px' }}>
          <Flex direction="column" gap={12}>
            <input
              type="text"
              placeholder="Название категории"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
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
            <input
              type="text"
              placeholder="Описание (необязательно)"
              value={newCategoryDesc}
              onChange={(e) => setNewCategoryDesc(e.target.value)}
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
            <Button
              size="large"
              mode="primary"
              appearance="themed"
              stretched
              onClick={handleCreateCategory}
              disabled={!newCategoryName.trim()}
            >
              Добавить категорию
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
            У вас пока нет категорий
          </Typography.Body>
        </Container>
      ) : (
        <CellList mode="island" header={<CellHeader>Мои категории</CellHeader>} style={{ width: "100%" }}>
          {categories.map(category => (
            <CellSimple
              key={category.id}
              showChevron
              title={category.name}
              subtitle={category.description}
              after={<Counter value={category.tasks?.length || 0} rounded />}
              onClick={() => setSelectedCategory(category)}
            />
          ))}
        </CellList>
      )}
    </Flex>
    </div>
  );
};

export default CategoriesPage;
