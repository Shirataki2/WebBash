import Cookies from "js-cookie";
import axios from 'axios'

// eslint-disable-next-line
const checkToken = async (vue: Vue): Promise<Record<string, string> | null> => {
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    const accessTokenExpire = Cookies.get("access_token_expire");
    // ログイン情報を問い合わせる
    if (accessToken && refreshToken && accessTokenExpire) {
        // 基本情報の取得
        try {
            const { data } = await axios.get("/api/users/me", {
                headers: {
                    "access-token": accessToken
                }
            });
            return data;
        } catch {
            // Refresh Tokenでトークンの更新を図る
            const params = new FormData();
            params.append("access_token", accessToken);
            params.append("refresh_token", refreshToken);
            try {
                await axios.post("/api/token/refresh", params, {
                    headers: {
                        "content-type": "multipart/form-data"
                    }
                });
                const accessToken = Cookies.get("access_token");
                const { data } = await axios.get("/api/users/me", {
                    headers: {
                        "access-token": accessToken
                    }
                });
                return data;
            } catch {
                return null;
            }
        }
    }
    return null;
}

export default checkToken;
