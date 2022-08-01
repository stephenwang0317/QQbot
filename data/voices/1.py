import requests
r=requests.get("https://vtbkeyboard.moe/api/audio/7706705/吐了吐了.mp3")
with open("./azi/吐了吐了.mp3","wb") as fp:
    fp.write(r.content)
    fp.close()