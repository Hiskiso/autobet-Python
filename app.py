import requests
import websocket
import threading
import time
import uuid
from multiprocessing import Process
accounts = ["UUID KNIFEX"]
array_times = []


def getProfileInfo(uuid):
    r = requests.get("https://knifex.top/api/user/initial", headers={
        "content-type": "application/json", "meta-data": uuid, "cookie": "id=" + uuid+";"})
    return r.json()


def start():
    print("         Всего аккаутов: " + str(len(accounts)))
    range = input("Диапазон (пример 0-100): ")
    target = input("Цель cla - clash, c - crash: ")
    cef = input("Кефф (пример 3.5 - 350): ")
    onlyBonus = input("Только бонусные предметы true/false (t/f): ")
    print("\n")
    bet(range, target, cef, onlyBonus)


def soketBet(profile, target, cef, onlyBonus, uuid):
    if profile["data"]["u"] is None:
        print("         ("+uuid+") - инвалидный")
        return

    items = []
    for item in profile["data"]["i"]:
        if item["b"] == onlyBonus:
            items.append(str(item["i"]))
    if len(items) < 1:
        print("         ("+profile["data"]['u']['name']+") Нет подходящих предметов")
        return


    def fastBet(ws):
            # 422
            msg = '422["b", { "autoCashOut": "'+cef+'", "i": [' + (
                items[0] if len(items) < 2 else ",".join(items)) + '], "rm": "'+target+'" }]'
            # print(msg)
            # ws.send(msg)
            print("         ("+profile["data"]['u']['name']+") Поставлено " + str(len(items)) + " предметов на " + str(int(cef)/100)+"")
            ws.close()

    def on_message(ws, message):
        # if len(message) >= 200:
        #     print(message[0:199])
        # else:
        #     print(message)
        if (message == "40"):
            msg = '420["join",{"ott":"'+profile["data"]["u"]["gauth"]+'"}]'
            # print(msg)
            ws.send(msg)
            msg = '421["joy",{"rm":"'+target+'"}]'
            # print(msg)
            ws.send(msg)

        if "STARTING" in message:
            fastBet(ws)

        if "gsi" in message:
            fastBet(ws)

        if "IN_PROGRESS" in message:
            print("         ("+profile["data"]['u']['name']+") Игра еще не закончилась, ждем... ")

        if "ENDED" in message:
            print("         ("+profile["data"]['u']['name']+") Игра заканчивается, ждем... ")

    def on_close(ws, _, __):
        print("closed")

    def on_error(ws, error):
        print(error)

    def on_open(ws):
        def ping():
            while ws.keep_running:
    
                if ws.keep_running:
                    
                    ws.send("2")
                    time.sleep("25")
                else:
                    ws.close()
        pingThread = threading.Thread(target=ping)
        pingThread.start()
    ws = websocket.WebSocketApp("wss://knifex.top/socket/sock1/?EIO=3&transport=websocket",
                                on_message=on_message,
                                on_close=on_close,
                                on_error=on_error,
                                on_open=on_open)
    ws.run_forever()


def bet(rng="0-2", target="cla", cef="350", onlyBonus="true"):
    rng = rng.split("-")

    if int(rng[1]) > len(accounts):
        print("Неверное значение диапазона\n=======================================================\n")
        start()
    if target not in ["cla", "c"]:
        print("Неверное значение цели\n=======================================================\n")
        start()
    onlyBonus = True if onlyBonus in ["t", "true", "True"] else False
    threads = []
    for acc in accounts[int(rng[0]):int(rng[1])+1]:
        profile = getProfileInfo(acc)
        t = threading.Thread(target=soketBet, args=[
                             profile, target, cef, onlyBonus, acc])
        threads.append(t)
        t.start()
        # continue
    for t in threads:
        t.join()
    print("\n\n")
    start()


start()
