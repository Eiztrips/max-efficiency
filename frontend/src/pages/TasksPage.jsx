import { useState } from "react";
import { Container, Flex, Typography, CellList, CellSimple, CellHeader, Button, SearchInput } from "@maxhub/max-ui";
import TaskDetailPage from "./TaskDetailPage";

const TasksPage = () => {
  const [selectedTask, setSelectedTask] = useState(null);
  const [showNewTask, setShowNewTask] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const mockTasks = [
    { 
        id: 1, 
        title: "Купить продукты", 
        description: "До 18:00", 
        category: "Личное",
        tags: ["Срочно", "Важно"],
    },
    { id: 2, title: "Позвонить врачу", description: "Записаться на прием", category: "Личное", tags: ["Tecn", "fdf"] },
    { id: 3, title: "Подготовить презентацию", description: "Пятница, 15:00", category: "Личное", tags: [] },
  ];

  const filteredTasks = mockTasks.filter(task => 
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (selectedTask || showNewTask) {
    return (
      <TaskDetailPage
        task={selectedTask}
        onClose={() => {
          setSelectedTask(null);
          setShowNewTask(false);
        }}
        onSave={(task) => {
          console.log("Save task:", task);
          setSelectedTask(null);
          setShowNewTask(false);
        }}
        onDelete={(id) => {
          console.log("Delete task:", id);
          setSelectedTask(null);
        }}
      />
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

      <CellList mode="island" header={<CellHeader>Сегодня</CellHeader>} style={{ width: "100%" }}>
        {filteredTasks.map(task => (
          <CellSimple
            key={task.id}
            showChevron
            title={task.title}
            subtitle={task.subtitle}
            onClick={() => setSelectedTask(task)}
          />
        ))}
      </CellList>

      <CellList mode="island" header={<CellHeader>На этой неделе</CellHeader>} style={{ width: "100%" }}>
        {filteredTasks.filter(t => t.group === "week").map(task => (
          <CellSimple
            key={task.id}
            showChevron
            title={task.title}
            subtitle={task.subtitle}
            onClick={() => setSelectedTask(task)}
          />
        ))}
      </CellList>
    </Flex>
    </div>
  );
};

export default TasksPage;
