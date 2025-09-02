// src/Routes.tsx
import { Routes, Route } from "react-router-dom";
import LoginPage from "./page/login";
import SignPage from "./page/signup";
import Home from "./page/home";
import CreatePlanPage from "./page/createPlan";
import CreateSchedulePage from "./page/createSchedule";
import PreparePage from "./page/prepare";

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/signup" element={<SignPage />} />
      <Route path="/user/:userId" element={<Home />} />
      <Route path="/user/:userId/createPlan" element={<CreatePlanPage />} />
      <Route
        path="/user/:userId/createSchedule"
        element={<CreateSchedulePage />}
      />
      <Route
        path="/user/:userId/:scheduleId/plan/:planId"
        element={<PreparePage />}
      />
    </Routes>
  );
};
