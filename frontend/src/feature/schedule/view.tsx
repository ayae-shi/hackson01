import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
interface Schedule {
  date: string;
  departure_time: string;
  wake_up_time: string;
  plan_id: number;
  schedule_id: number;
}

const ScheduleList: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`http://localhost:8000/schedules/user/${userId}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        setSchedules(data);
      })
      .catch((error) => {
        setError(error.message);
      });
  }, [userId]);

  const handleButtonClick = (schedule_id: number, plan_id: number) => {
    navigate(`/user/${userId}/${schedule_id}/plan/${plan_id}`);
  };

  useEffect(() => {
    const checkWakeUpTime = () => {
      const currentTime = new Date();
      schedules.forEach((schedule) => {
        const [wakeUpHours, wakeUpMinutes, wakeUpSeconds] =
          schedule.wake_up_time.split(":").map(Number);
        const wakeUpTime = new Date();
        wakeUpTime.setHours(wakeUpHours, wakeUpMinutes, wakeUpSeconds);

        const [departureHours, departureMinutes, departureSeconds] =
          schedule.departure_time.split(":").map(Number);
        const departureTime = new Date();
        departureTime.setHours(
          departureHours,
          departureMinutes,
          departureSeconds
        );

        if (currentTime >= wakeUpTime && currentTime < departureTime) {
          navigate(
            `/user/${userId}/${schedule.schedule_id}/plan/${schedule.plan_id}`
          );
        }
      });
    };

    const interval = setInterval(checkWakeUpTime, 1000);

    return () => clearInterval(interval);
  }, [schedules, navigate, userId]);

  return (
    <div className="flex flex-col items-center justify-center ">
      <h1 className="text-4xl text-white text-center font-semibold text-purple-700 mb-10">
        予定一覧
      </h1>
      <div className="w-full max-w-2xl p-8 space-y-6 bg-white rounded-lg shadow-md">
        {error && <p className="text-red-500 text-center">{error}</p>}
        {schedules.length === 0 && (
          <p className="text-center">予定がありません。</p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2  gap-4">
          {/* <div className="flex justify-center"> */}
          {schedules.map((schedule) => (
            <button
              key={schedule.schedule_id}
              className="p-4 border border-2  border-purple-400 text-purple-400  font-semibold rounded shadow-md transition-colors hover:bg-purple-700 hover:text-white"
              onClick={() =>
                handleButtonClick(schedule.schedule_id, schedule.plan_id)
              }
            >
              <p>日付: {schedule.date}</p>
              <p>家を出る時間: {schedule.departure_time}</p>
              <p>起床時間: {schedule.wake_up_time}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ScheduleList;
