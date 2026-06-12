import React from "react";
import { NavLink } from "react-router-dom";

const menuItems = [
  { label: "EXE 분석", path: "/" },
  { label: "분석기록", path: "/mypage" },
  { label: "서비스 안내", path: "/guide" },
];

const Sidebar = ({ onNavigate }) => (
  <nav className="top-nav" aria-label="주요 메뉴">
    {menuItems.map((item) => (
      <NavLink
        key={item.path}
        to={item.path}
        end={item.path === "/"}
        onClick={onNavigate}
        className={({ isActive }) => `top-nav-link ${isActive ? "active" : ""}`}
      >
        {item.label}
      </NavLink>
    ))}
  </nav>
);

export default Sidebar;
