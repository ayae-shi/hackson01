from fastapi import FastAPI, HTTPException,status, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import uvicorn
#パスワードのハッシュ化を行うためのライブラリ
import bcrypt
import logging
from typing import List
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#FastAPIを使っていきますよって設定
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 実際の運用では適切なオリジンを指定する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    username: str
    password: str

class ScheduleRegisterRequest(BaseModel):
    date: str
    departure_time: str
    plan_id: str
    user_id: str

class ScheduleRegisterResponse(BaseModel):
    schedule_id: str

# スケジュールのレスポンス
class ScheduleResponse(BaseModel):
    date: str  # 日付
    departure_time: str  # 出発時間
    wake_up_time: str  # 起床時間

class ScheduleListResponse(BaseModel):
    schedules: List[ScheduleResponse]


class ProcessCreate(BaseModel):
    step_name: str
    step_time: int

class PlanCreate(BaseModel):
    user_id: int
    plan_name: str
    steps: List[ProcessCreate]

def calculate_wake_up_time(departure_time: str, steps: list) -> str:
    departure_dt = datetime.strptime(departure_time, '%H:%M:%S')  # フォーマットを 'HH:MM:SS' に変更
    
    # process_orderの逆順にstep_timeを引いていく
    for step in sorted(steps, key=lambda x: x['process_order'], reverse=True):
        step_time = step['step_time']
        departure_dt -= timedelta(minutes=step_time)

    return departure_dt.strftime('%H:%M:%S')  # フォーマットを 'HH:MM:SS' に変更


env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_file_path)

# Supabaseクライアントの設定
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

# 環境変数が正しく読み込まれているか確認
if not supabase_url or not supabase_key:
    raise Exception("Supabase URL and Key must be set in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)


#####ユーザー登録エンドポイント (POST)#####
@app.post("/register")
async def register_user(user: User):
    try:
        response = supabase.table("user_reg_log").select("user_name").eq("user_name", user.username).execute()
        if response.data:
            raise HTTPException(status_code=400, detail="User already exists")

        else:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

            insert_response = supabase.table("user_reg_log").insert({
                "user_name": user.username,
                "password": hashed_password.decode('utf-8')
            }).execute()

            print(insert_response)

        # ここでステータスコードを確認
        if insert_response.data is None:
            raise HTTPException(status_code=500, detail="Error inserting data into database")
        return {"user_name": user.username, "status": "User registered successfully"}
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    # エラーログを記録
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ユーザー取得エンドポイント (GET)
@app.get("/users/{user_name}")
async def get_user(user_name: str):
    # ユーザー情報を取得
    response = supabase.table("user_reg_log").select("*").eq("user_name", user_name).execute()

    # ユーザーが存在しない場合
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = response.data[0]  # ユーザーデータを取得
    return {"user_id": user_data["user_id"], "user_name": user_data["user_name"]}



# 予定一覧エンドポイント
@app.get("/schedules/", response_model=ScheduleListResponse)
async def read_schedules(username: str):
    try:
        # ユーザの取得
        user_response = supabase.from_("user_reg_log").select("*").eq("user_name", username).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        user = user_response.data[0]

        # 予定の取得
        schedule_response = supabase.from_("schedule_reg").select("*").eq("user_id", user["user_id"]).execute()
        if not schedule_response.data:
            raise HTTPException(status_code=404, detail="No schedules found for the user")
        
        # レスポンスの作成
        schedule_list = [
            ScheduleResponse(
                date=schedule[" "],
                departure_time=schedule["departure_time"],
                wake_up_time=schedule["wake_up_time"]
            ) for schedule in schedule_response.data
        ]
        
        return ScheduleListResponse(schedules=schedule_list)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#ログインのエンドポイント
@app.post("/login")
async def login_user(user: User):
    try:
        if not user.username or not user.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

        response = supabase.table("user_reg_log").select("user_id", "user_name", "password").eq("user_name", user.username).execute()

        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_data = response.data[0]
        
        logging.info(f"User data received: {user_data}")

        if bcrypt.checkpw(user.password.encode('utf-8'), user_data["password"].encode('utf-8')):
            return {"user_id": user_data["user_id"], "user_name": user_data["user_name"]}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# 予定登録エンドポイント (POST)
#出発時間から起床時間を計算



# プラン登録エンドポイント (POST)
@app.post("/plans/")
async def create_plan(request: Request,plan: PlanCreate):
    try:
        # 新しいプランを作成
        response = supabase.table("plan_reg").insert({"user_id": plan.user_id,"plan_name": plan.plan_name}).execute()
        logging.info(f"Plan creation response: {response.data}")
        plan_id = response.data[0].get("plan_id")

        # Supabaseレスポンスをチェック
        if not response.data or not response.data[0]:
            logging.error(f"Failed to create plan: {response.data}")
            raise HTTPException(status_code=500, detail="Failed to create plan")

        if plan_id is None:
            logging.error(f"Plan ID not found in response: {response.data}")
            raise HTTPException(status_code=500, detail="Plan ID not found in response")

        # 各ステップを作成して関連付け
        for index, step in enumerate(plan.steps):
            step_data = {
                "plan_id": plan_id,
                "step_name": step.step_name,
                "step_time": step.step_time,
                "process_order": index + 1  # 順番は0から始まるインデックスに1を足して設定
            }
            print(step_data)
            step_response = supabase.table("process").insert(step_data).execute()
            logging.info(f"Step creation response for step {index+1}: {step_response.data}")
            
            # Supabaseレスポンスをチェック
            if not step_response.data or not step_response.data[0]:
                logging.error(f"Failed to create plan step: {step_response.data}")
                raise HTTPException(status_code=500, detail="Failed to create plan step")
        
        return {"message": "Plan created successfully"}
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/register_schedule", response_model=ScheduleRegisterResponse)
async def register_schedule(schedule_request: ScheduleRegisterRequest):
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
        return ScheduleRegisterResponse(schedule_id=str(schedule_id))
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# プロセス詳細エンドポイント
@app.get("/plans/name/{plan_id}")
async def get_plan_by_name(schedule_id: str):
    try:
        # plan_nameでプラン情報を取得
        print("hoge")
        plan_response = supabase.table("schedule_reg").select("*").eq("schedule_id", schedule_id).execute()

        logging.info(f"Plan fetch response: {plan_response.data}")

        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        plan_id = plan_response.data[0].get("plan_id")

        # 各工程の情報を取得
        steps_response = supabase.table("process").select("*").eq("plan_id", plan_id).order("process_order", desc=True).execute()
        logging.info(f"Steps fetch response: {steps_response.data}")

        if not steps_response.data:
            logging.error(f"Steps not found for plan: {plan_id}")
            raise HTTPException(status_code=404, detail="Steps not found for plan")

        steps = steps_response.data

        # 結果を整形
        result = {
            "steps": [{"step_name": step["step_name"], "step_time": step["step_time"], "process_order": step["process_order"]} for step in steps],

        }

        return result
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    



# 予定一覧エンドポイント
@app.get("/schedules/user/{user_id}")
async def get_schedules_by_user_id(user_id: str):
    try:
        # user_idでschedule_reg情報を取得
        schedules_response = supabase.table("schedule_reg").select("*").eq("user_id", user_id).execute()

        logging.info(f"Schedules fetch response: {schedules_response.data}")

        if not schedules_response.data:
            raise HTTPException(status_code=404, detail="Schedules not found for user")

        schedules = schedules_response.data

        return schedules
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# プラン取得エンドポイント
@app.get("/plans/{plan_id}")
async def get_plan_by_id(plan_id: str):
    try:
        # plan_idでplan_reg情報を取得
        plan_response = supabase.table("plan_reg").select("plan_id, plan_name").eq("plan_id", plan_id).execute()

        logging.info(f"Plan fetch response: {plan_response.data}")

        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        plan = plan_response.data[0]

        # plan_idに基づいてprocess情報を取得
        process_response = supabase.table("process").select("*").eq("plan_id", plan_id).order("process_order", desc=True).execute()
        logging.info(f"Process fetch response: {process_response.data}")

        if not process_response.data:
            logging.warning(f"No processes found for plan {plan_id}")
            processes = []
        else:
            processes = process_response.data

        # 結果を整形
        result = {
            "plan_id": plan["plan_id"],
            "plan_name": plan["plan_name"],
            "processes": [{"step_name": step["step_name"], "step_time": step["step_time"], "process_order": step["process_order"]} for step in processes]
        }
        return result
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ユーザのすべてのプランを取得するエンドポイント
@app.get("/user/{user_id}/plans")
async def get_plans_by_user_id(user_id: str):
    try:
        # user_idでplan_reg情報を取得
        plans_response = supabase.table("plan_reg").select("plan_id, plan_name").eq("user_id", user_id).execute()

        logging.info(f"Plans fetch response: {plans_response.data}")

        if not plans_response.data:
            raise HTTPException(status_code=404, detail="No plans found for user")

        return plans_response.data
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



# 選択されたプランの詳細を取得するエンドポイント
@app.get("/plans/{plan_id}")
async def get_plan_by_id(plan_id: str):
    try:
        # plan_idでplan_reg情報を取得
        plan_response = supabase.table("plan_reg").select("plan_id, plan_name").eq("plan_id", plan_id).execute()

        logging.info(f"Plan fetch response: {plan_response.data}")

        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        plan = plan_response.data[0]

        # plan_idに対してprocess情報を取得
        process_response = supabase.table("process").select("*").eq("plan_id", plan["plan_id"]).order("process_order", desc=True).execute()
        logging.info(f"Process fetch response for plan {plan['plan_id']}: {process_response.data}")

        if not process_response.data:
            logging.warning(f"No processes found for plan {plan['plan_id']}")
            plan["processes"] = []
        else:
            plan["processes"] = process_response.data

        return plan
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# schedule_idを受け取ってdeparture_timeとwake_up_timeを取得するエンドポイント
@app.get("/schedule/{schedule_id}/times")
async def get_schedule_times(schedule_id: str):
    try:
        # schedule_idでschedule_reg情報を取得
        schedule_response = supabase.table("schedule_reg").select("departure_time, wake_up_time").eq("schedule_id", schedule_id).execute()

        logging.info(f"Schedule fetch response: {schedule_response.data}")

        if not schedule_response.data:
            raise HTTPException(status_code=404, detail="Schedule not found")

        schedule = schedule_response.data[0]

        return {
            "departure_time": schedule["departure_time"],
            "wake_up_time": schedule["wake_up_time"]
        }
    except Exception as e:
        logging.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# サーバー起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
