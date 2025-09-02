from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import uvicorn
import bcrypt
import logging

# FastAPIを使っていきますよって設定
app = FastAPI()

# ユーザーのリクエストボディを定義
class User(BaseModel):
    user_name: str
    password: str

# 環境変数の読み込み
# .envファイルのパスを指定
env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
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

# ログインエンドポイント (POST)
@app.post("/login")
async def login_user(user: User):
    try:
        # デバッグ用出力
        logging.info(f"Trying to login with user_name: {user.user_name}")

        response = supabase.table("user_reg_log").select("user_id", "user_name", "password").eq("user_name", user.user_name).execute()

        # レスポンスの内容をログに出力
        logging.info(f"Supabase response: {response}")

        if not response.data:
            logging.error(f"User {user.user_name} not found")
            raise HTTPException(status_code=404, detail="User not found")

        user_data = response.data[0]
        logging.info(f"User data: {user_data}")

        if bcrypt.checkpw(user.password.encode('utf-8'), user_data["password"].encode('utf-8')):
            return {"user_id": user_data["user_id"], "user_name": user_data["user_name"]}
        else:
            logging.error("Incorrect password")
            raise HTTPException(status_code=400, detail="Incorrect password")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# サーバー起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
