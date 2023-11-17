from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
import requests
from fastapi.responses import RedirectResponse
# from jose import jwt
from fastapi.responses import HTMLResponse

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace these with your own values from the Google Developer Console



@app.get("/school/oauth/login")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }


@app.get("/school/oauth/redirect")
async def auth_google(code: str):  # last param not needed
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                             headers={"Authorization": f"Bearer {access_token}"})
    jsonn = user_info.json()
    print(jsonn)
    redirect_url = f"exp://?id={jsonn['id']}&email={jsonn['email']}&name={jsonn['name']}"  # Replace with your actual redirect URL
    return RedirectResponse(url=redirect_url)

    return user_info.json()


@app.get("/school/oauth/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
