// Homeコンポーネントの作成
import React from "react";
import HowtoApp from "../feature/home/howtoapp";
import ScheduleList from "../feature/schedule/view";
import { useParams, useNavigate } from "react-router-dom";
import "../font.css"; // カスタムCSSファイルをインポート

// Homeコンポーネントの作成
const Home = () => {
  const navigate = useNavigate();
  const { userId } = useParams<{ userId: string }>();

  const moveCreatePlan = () => {
    navigate(`/user/${userId}/createPlan`);
  };
  const moveCreateSchedule = () => {
    navigate(`/user/${userId}/createSchedule`);
  };

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col items-center p-8 kiwi-maru-regular">
      <h1 className="text-5xl font-bold text-purple-700 mb-8">HOME</h1>
      <div className="flex space-x-4 mt-10">
        <button
          onClick={moveCreatePlan}
          className="px-6 py-3 bg-purple-600 text-white rounded shadow hover:bg-purple-700 transition-transform transform hover:scale-105"
        >
          準備プラン登録
        </button>
        <button
          onClick={moveCreateSchedule}
          className="px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition-transform transform hover:scale-105"
        >
          予定登録
        </button>
      </div>
      <div className="w-full max-w-2xl mt-20  ">
        <ScheduleList />
      </div>
      <div className="my-20">
        <HowtoApp />
      </div>
    </div>
  );
};

export default Home;
