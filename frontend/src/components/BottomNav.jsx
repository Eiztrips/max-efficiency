import { Tappable } from "@maxhub/max-ui";
import "./BottomNav.css";

const BottomNav = ({ activeTab, onTabChange }) => {

  const handleTabChange = (tab) => {
    onTabChange(tab);
  };

  const tabs = [
    {
      id: "tasks",
      text: "Задачи",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M21 12V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
    },
    {
      id: "categories",
      text: "Категории",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="2"/>
          <rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="2"/>
          <rect x="13" y="3" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="2"/>
          <rect x="13" y="13" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="2"/>
        </svg>
      ),
    },
    {
      id: "tags",
      text: "Теги",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20.59 13.41L13.42 20.58C13.2343 20.766 13.0137 20.9135 12.7709 21.0141C12.5281 21.1148 12.2678 21.1666 12.005 21.1666C11.7422 21.1666 11.4819 21.1148 11.2391 21.0141C10.9963 20.9135 10.7757 20.766 10.59 20.58L2 12V2H12L20.59 10.59C20.9625 10.9647 21.1716 11.4716 21.1716 12C21.1716 12.5284 20.9625 13.0353 20.59 13.41Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="7" cy="7" r="1.5" fill="currentColor"/>
        </svg>
      ),
    },
    {
      id: "profile",
      text: "Профиль",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
    },
  ];

  return (
    <div className="bottom-nav">
      {tabs.map((tab) => (
        <Tappable
          key={tab.id}
          className={`bottom-nav__item ${activeTab === tab.id ? "bottom-nav__item--active" : ""}`}
          onClick={() => handleTabChange(tab.id)}
        >
          <div className="bottom-nav__icon">{tab.icon}</div>
          <div className="bottom-nav__text">{tab.text}</div>
        </Tappable>
      ))}
    </div>
  );
};

export default BottomNav;
