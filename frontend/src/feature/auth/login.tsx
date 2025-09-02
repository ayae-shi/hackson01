// Homeコンポーネントの作成
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import '../../font.css'; // カスタムCSSファイルをインポート
// Homeコンポーネントの作成
const Login = () => {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const navigate = useNavigate();

  const handleClick = () => {
    console.log(username);
    fetch("http://0.0.0.0:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        const userId = data.user_id;
        navigate(`/user/${userId}`);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-purple-200">
      <div className="p-24 bg-white rounded shadow-md w-full max-w-lg">
        <h1 className="text-center mb-10 font-medium text-5xl kiwi-maru-regular">ログイン</h1>
        <div>
          <div className="mb-8">
            <p className="text-center text-xl kiwi-maru-regular">ユーザ名</p>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-6 py-3 border rounded text-xl"
            />
          </div>
          <div className="mb-8">
            <p className="text-center text-xl kiwi-maru-regular">パスワード</p>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-6 py-3 border rounded text-xl"
            />
          </div>
          <div className="text-center">
            <button
              onClick={handleClick}
              className="px-10 py-4 bg-pink-300 text-white rounded text-xl 
                         hover:bg-pink-400 active:bg-pink-500 transition-colors duration-300 kiwi-maru-regular"
            >
              ログイン
            </button>
          </div>
        </div>
        <p className="text-center mt-10 font-medium kiwi-maru-regular">
          サインアップがまだな方は
          <Link to="/signup" className="text-blue-500 underline kiwi-maru-regular">
            こちらから
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
