import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../../font.css"; // カスタムCSSファイルをインポート

interface Preparation {
  content: string;
  time: number;
}

const PreparationPlan: React.FC = () => {
  const { userId } = useParams<{ userId: string }>(); // URLからuserIdを取得
  const [planName, setPlanName] = useState<string>("");
  const [preparations, setPreparations] = useState<Preparation[]>([
    { content: "", time: 0 },
  ]);
  const navigate = useNavigate();

  const handlePlanNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPlanName(e.target.value);
  };

  const handlePreparationChange = (
    index: number,
    field: keyof Preparation,
    value: string
  ) => {
    const newPreparations = preparations.slice();
    if (field === "time") {
      newPreparations[index][field] = Number(value);
    } else {
      newPreparations[index][field] = value as any;
    }
    setPreparations(newPreparations);
  };

  const addPreparation = () => {
    setPreparations([...preparations, { content: "", time: 0 }]);
  };

  const handleSubmit = () => {
    const data = {
      user_id: userId,
      plan_name: planName,
      steps: preparations.map((prep) => ({
        step_name: prep.content,
        step_time: prep.time,
      })),
    };
    console.log(data);

    fetch("http://0.0.0.0:8000/plans/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((response) => {
        console.log(response);
        navigate(`/user/${userId}`);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-400 via-blue-300 to-blue-200 p-6 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-12 mt-12 kiwi-maru-regular">
        準備プラン作成
      </h1>
      <div className="w-full max-w-3xl bg-white p-6 rounded shadow-md">
        <div className="mb-4">
          <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
            準備プラン名
          </label>
          <input
            type="text"
            value={planName}
            onChange={handlePlanNameChange}
            className="w-full px-4 py-2 border border-gray-300 rounded"
          />
        </div>
        {preparations.map((prep, index) => (
          <div key={index} className="mb-6">
            <h3 className="text-2xl font-semibold mb-2 kiwi-maru-regular">
              {index + 1}つ目の準備
            </h3>
            <div className="mb-4">
              <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
                準備内容
              </label>
              <input
                type="text"
                value={prep.content}
                onChange={(e) =>
                  handlePreparationChange(index, "content", e.target.value)
                }
                className="w-full px-4 py-2 border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
                かかる時間 (分)
              </label>
              <input
                type="text"
                value={prep.time}
                onChange={(e) =>
                  handlePreparationChange(index, "time", e.target.value)
                }
                className="w-full px-4 py-2 border border-gray-300 rounded"
              />
            </div>
          </div>
        ))}
        <button
          onClick={addPreparation}
          className="w-full bg-green-400 text-white px-4 py-2 rounded shadow hover:bg-green-500 mb-6 kiwi-maru-regular"
        >
          準備内容を追加する
        </button>
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded shadow hover:bg-blue-700 kiwi-maru-regular"
        >
          登録
        </button>
      </div>
    </div>
  );
};

export default PreparationPlan;
