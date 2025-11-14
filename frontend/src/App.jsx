import { useEffect, useState } from "react";
import { Panel, Flex, Spinner } from "@maxhub/max-ui";
import "@maxhub/max-ui/dist/styles.css";
import { useWebApp } from "./hooks/useWebApp";
import BottomNav from "./components/BottomNav";
import TasksPage from "./pages/TasksPage";
import CategoriesPage from "./pages/CategoriesPage";
import TagsPage from "./pages/TagsPage";
import ProfilePage from "./pages/ProfilePage";

const App = () => {
  const { isReady } = useWebApp();
  const [activeTab, setActiveTab] = useState("tasks");

  if (!isReady) {
    return (
      <Panel mode="secondary" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
        <Spinner size="large" />
      </Panel>
    );
  }

  const renderPage = () => {
    switch (activeTab) {
      case "tasks":
        return <TasksPage />;
      case "categories":
        return <CategoriesPage />;
      case "tags":
        return <TagsPage />;
      case "profile":
        return <ProfilePage />;
      default:
        return <TasksPage />;
    }
  };

  return (
    <Panel mode="secondary" style={{ width: "100%", minHeight: "100vh" }}>
      <div style={{ width: "100%", minHeight: "100vh", paddingBottom: "80px" }}>
        {renderPage()}
      </div>
      <div style={{ 
        position: "fixed", 
        bottom: 0, 
        left: 0, 
        right: 0,
        zIndex: 1000
      }}>
        <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
      </div>
    </Panel>
  );
};

export default App;