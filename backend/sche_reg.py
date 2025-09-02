from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import uvicorn
import logging
from datetime import datetime, timedelta

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FastAPIのインスタンス作成
app = FastAPI()

# リクエストボディのモデル
class ScheduleRequest(BaseModel):
    date: str
    departure_time: str
    plan_id: str
    user_id: str

# レスポンスモデル
class ScheduleResponse(BaseModel):
    schedule_id: str

# 環境変数の読み込み
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_file_path)

# Supabaseクライアントの設定
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

print("Supabase URL:", supabase_url)
print("Supabase Key:", supabase_key)

# 環境変数が正しく読み込まれているか確認
if not supabase_url or not supabase_key:
    raise Exception("Supabase URL and Key must be set in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

def calculate_wake_up_time(departure_time: str, steps: list) -> str:
    departure_dt = datetime.strptime(departure_time, '%H:%M:%S')  # フォーマットを 'HH:MM:SS' に変更
    
    # process_orderの逆順にstep_timeを引いていく
    for step in sorted(steps, key=lambda x: x['process_order'], reverse=True):
        step_time = step['step_time']
        departure_dt -= timedelta(minutes=step_time)
    
    return departure_dt.strftime('%H:%M:%S')  # フォーマットを 'HH:MM:SS' に変更

@app.post("/register_schedule", response_model=ScheduleResponse)
async def register_schedule(schedule_request: ScheduleRequest):
    try:
        # プランに対応するすべてのステップを取得
        steps_response = supabase.table("process").select("*").eq("plan_id", schedule_request.plan_id).execute()
        
        if not steps_response.data or len(steps_response.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No steps found for the given plan_id")

        steps = steps_response.data

        # wake_up_timeを計算
        wake_up_time = calculate_wake_up_time(schedule_request.departure_time, steps)
        
        # Supabaseにデータを挿入（schedule_id を自動生成）
        response = supabase.table("schedule_reg").insert({
            "date": schedule_request.date,
            "departure_time": schedule_request.departure_time,
            "wake_up_time": wake_up_time,
            "plan_id": schedule_request.plan_id,
            "user_id": schedule_request.user_id
        }).execute()

        # 挿入結果の確認
        if not response.data or len(response.data) == 0:
            logging.error(f"Failed to insert schedule: {response}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register schedule")

        # 挿入結果から schedule_id を取得
        schedule_id = response.data[0].get('schedule_id')  # フィールド名を 'id' に変更

        if schedule_id is None:
            logging.error(f"'id' not found in response: {response.data}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve schedule ID")

        # スケジュールIDを返す
        return ScheduleResponse(schedule_id=str(schedule_id))
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# サーバー起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
