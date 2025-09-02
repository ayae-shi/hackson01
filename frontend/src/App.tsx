import React from "react";
import "./App.css";
import Home from "./page/home";
import SignPage from "./page/signup";
import LoginPage from "./page/login";
// import createPlan from "./page/createPlan";
import PreparationPlan from "./feature/plan/create";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <PreparationPlan />
      </header>
    </div>
  );
}

export default App;
