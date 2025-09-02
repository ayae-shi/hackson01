from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import uvicorn
#パスワードのハッシュ化を行うためのライブラリ
import bcrypt
import logging


#FastAPIを使っていきますよって設定
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


#####ユーザー登録エンドポイント (POST)#####

#HTTP POSTリクエストが/registerというパスに送信されたときにこの関数が呼び出される
@app.post("/register")
async def register_user(user: User):
    try:
        response = supabase.table("user_reg_log").select("user_name").eq("user_name", user.user_name).execute()
        if response.data:
            raise HTTPException(status_code=400, detail="User already exists")
        


        else:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
            insert_response = supabase.table("user_reg_log").insert({
                "user_name": user.user_name,
                "password": hashed_password.decode('utf-8')
            }).execute()

            print(insert_response)

        # ここでステータスコードを確認
        if insert_response.data is None:
            raise HTTPException(status_code=500, detail="Error inserting data into database")
        return {"user_name": user.user_name, "status": "User registered successfully"} 
    except Exception as e:
        logging.error(f"Error occurred: {e}") 
    # エラーログを記録
        raise HTTPException(status_code=500, detail="Internal Server Error")
########################################



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

# サーバー起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
