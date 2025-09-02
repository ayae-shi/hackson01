import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom"; // useNavigateをインポ

interface ScheduleRequest {
  date: string;
  departure_time: string;
  plan_id: string;
  user_id: string;
}

interface Plan {
  plan_id: string;
  plan_name: string;
}

interface Process {
  step_name: string;
  step_time: string;
  process_order: number;
}

interface PlanDetails extends Plan {
  processes: Process[];
}

const ScheduleRegister: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const [date, setDate] = useState<string>("");
  const [departureTime, setDepartureTime] = useState<string>("");
  const [planId, setPlanId] = useState<string>("");
  const [plans, setPlans] = useState<Plan[]>([]);
  const [planDetails, setPlanDetails] = useState<PlanDetails | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // プランのリストを取得する
    fetch(`http://localhost:8000/user/${userId}/plans`)
      .then((res) => res.json())
      .then((data) => {
        // データが配列であるか確認し、そうでない場合は空の配列を設定
        setPlans(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        console.error("Error fetching plans:", error);
      });
  }, [userId]);

  useEffect(() => {
    if (planId) {
      // プランの詳細情報を取得する
      fetch(`http://localhost:8000/plans/${planId}`)
        .then((res) => res.json())
        .then((data) => {
          setPlanDetails(data);
        })
        .catch((error) => {
          console.error("Error fetching plan details:", error);
        });
    } else {
      setPlanDetails(null);
    }
  }, [planId]);

  const handleSubmit = () => {
    const formattedDepartureTime =
      departureTime.length === 5 ? `${departureTime}:00` : departureTime;
    const data: ScheduleRequest = {
      date,
      departure_time: formattedDepartureTime,
      plan_id: planId,
      user_id: userId!,
    };

    fetch("http://localhost:8000/register_schedule", {
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
        予定登録
      </h1>
      <div className="bg-white p-6 rounded-lg shadow-md mb-4 w-full max-w-3xl">
        <div className="mb-4">
          <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
            日付選択
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded p-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
            家を出る時間
          </label>
          <input
            type="time"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded p-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-lg font-medium mb-2 kiwi-maru-regular">
            プラン選択
          </label>
          <select
            value={planId}
            onChange={(e) => setPlanId(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded p-2"
          >
            <option value="">プランを選択してください</option>
            {plans.map((plan) => (
              <option key={plan.plan_id} value={plan.plan_id}>
                {plan.plan_name}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded shadow hover:bg-blue-700 kiwi-maru-regular"
        >
          登録
        </button>
      </div>

      {planDetails && (
        <div className="bg-white p-6 rounded-lg shadow-md mt-8 w-full max-w-lg">
          <h2 className="text-xl font-bold mb-4 kiwi-maru-regular">
            プラン詳細
          </h2>
          <p>プラン名: {planDetails.plan_name}</p>
          <div>
            <h3 className="text-lg font-semibold mt-4 kiwi-maru-regular">
              準備内容
            </h3>
            {planDetails.processes.map((process, index) => (
              <div
                key={index}
                className="p-4 border border-gray-300 rounded mt-2"
              >
                <p>準備内容: {process.step_name}</p>
                <p>かかる時間: {process.step_time}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleRegister;
