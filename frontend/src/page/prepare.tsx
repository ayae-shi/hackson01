// Homeコンポーネントの作成
import React from "react";
import PreparationTimer from "../feature/prepare/view";
import "../font.css";
// Homeコンポーネントの作成
const PreparePage = () => {
  return (
    <div className="bg-blue-200 kiwi-maru-regular">
      <PreparationTimer />
    </div>
  );
};

export default PreparePage;
