// Homeコンポーネントの作成
import React from "react";

// Homeコンポーネントの作成
const HowtoApp = () => {
  return (
    <div className="container mx-auto">
      <h2 className="text-4xl text-white text-center font-semibold text-purple-700 mb-10">
        アプリの使い方
      </h2>
      <div className="bg-white p-8 rounded-lg shadow-lg text-purple-500">
        <div className="mb-4">
          <p className="font-semibold  ">1. 準備プランを登録する</p>
          <p className="">「準備内容」と「かかる時間」を登録！</p>
        </div>
        <div className="mb-4">
          <p className="font-semibold ">2. 予定を登録する</p>
          <p className="">「日付」「準備プラン」「出発時間」を登録！</p>
        </div>
        <div className="mb-4">
          <p className="font-semibold ">
            3. 当日、寝ながらアラームが鳴るのを待つ
          </p>
          <p className="">
            起床時間にアラームがかかる。準備内容ごとにカウントダウンを表示！
            一緒に準備をしよう！
          </p>
        </div>
      </div>
    </div>
  );
};

export default HowtoApp;
