import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

interface Process {
  step_name: string;
  step_time: string;
  process_order: number;
}

interface Plan {
  plan_id: string;
  plan_name: string;
  processes: Process[];
}

interface ScheduleTimes {
  departure_time: string;
  wake_up_time: string;
}

const PreparationTimer: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const { planId, scheduleId } = useParams<{
    planId: string;
    scheduleId: string;
  }>();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [scheduleTimes, setScheduleTimes] = useState<ScheduleTimes | null>(
    null
  );
  const navigate = useNavigate();

  // Fetch the plan details
  useEffect(() => {
    fetch(`http://localhost:8000/plans/${planId}`)
      .then((res) => res.json())
      .then((data) => {
        setPlan(data);
        setCurrentStep(0);
        if (data.processes.length > 0) {
          setTimeLeft(parseInt(data.processes[0].step_time, 10) * 60);
        }
      })
      .catch((error) => {
        console.error("Error fetching plan:", error);
      });
  }, [planId]);

  // Fetch the schedule times
  useEffect(() => {
    fetch(`http://localhost:8000/schedule/${scheduleId}/times`)
      .then((res) => res.json())
      .then((data) => {
        setScheduleTimes(data);
      })
      .catch((error) => {
        console.error("Error fetching schedule times:", error);
      });
  }, [scheduleId]);

  // Handle the countdown timer
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft((prevTime) => prevTime - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else if (timeLeft === 0 && plan) {
      if (currentStep < plan.processes.length - 1) {
        setCurrentStep((prevStep) => prevStep + 1);
        setTimeLeft(
          parseInt(plan.processes[currentStep + 1].step_time, 10) * 60
        );
      } else {
        navigate(`/user/${userId}`);
      }
    }
  }, [timeLeft, plan, currentStep, navigate, userId]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  if (!plan || !scheduleTimes) {
    return <div>Loading...</div>;
  }

  const nowTime = new Date(); // 現在時刻を取得
  // 現在時刻を取得
  const nowHours = nowTime.getHours();
  const nowMinutes = nowTime.getMinutes();

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-full max-w-2xl p-8 space-y-6 bg-white rounded shadow-md">
        <div className="flex justify-between items-cente text-blue-500 font-semibold">
          <div>出発時間: {scheduleTimes.departure_time}</div>
          <div>
            現在: {nowHours}:{nowMinutes}
          </div>
        </div>
        <div className=" text-center">
          <h2 className="text-4xl text-blue-700 font-semibold">
            {plan.processes[currentStep] &&
              `${plan.processes[currentStep].step_name}`}
          </h2>
          <p className="mt-5">終了まで残り</p>
        </div>
        <div className="text-center text-8xl font-bold">
          <div>{formatTime(timeLeft)}</div>
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-4">以降の準備</h2>
          <div className="space-y-4">
            {plan.processes.slice(currentStep + 1).map((process, index) => (
              <div
                key={index}
                className="p-4 border border-blue-500 rounded flex justify-center"
              >
                <p className="mx-10">準備内容: {process.step_name}</p>
                <p>かかる時間: {process.step_time} 分</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreparationTimer;
