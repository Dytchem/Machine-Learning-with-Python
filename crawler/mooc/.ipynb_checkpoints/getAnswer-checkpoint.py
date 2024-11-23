import json
from pprint import pprint
import requests


def getAnswer(aId):
    url = "http://www.icourse163.org/mob/course/paperDetail/v1"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = (
        "mob-token=8817e1a1d01e93af76dd102b05a6fb886d0b25fd8b19b252175ba33f4e18dedf2543d4ea7e783a58c8551b3f45bb3de406322198119ae64f6263f8326e676386f3276f874c0ec7bb0d95be9d6e4d91cfd75c76b58fbbd619c321b614429bde74ff0d400dfd279a363cbfeb42eb5bf2a7332c51a6107e975449698118cf648d5f0088e9975dce110878690b966a534b57e9752b3e5df78238b6c877f6c588079c24aa40074fc2d585cb89833cb42e25ef571d6d864a360b95ea2b933488934850abdae0793dfb09f8643ced6884c79b818275a1d5be7805387fd996151d7307b0&testId=1242838683&isExercise=false&aId="
        + str(aId)
        + "&withStdAnswerAndAnalyse=true&"
    )
    r = requests.post(url, headers=headers, data=data)
    j = json.loads(r.text)
    q = j["results"]["mocPaperDto"]["objectiveQList"]
    t = 0
    for i in q:
        t += 1
        L = []
        for j, k in enumerate(i["optionDtos"]):
            if k["answer"]:
                L.append(chr(ord("A") + j))
            else:
                L.append("_")
        print(t, ":\t", end=" ")
        for j in L:
            print(j, end=" ")
        if i["stdAnswer"]:
            print(i["stdAnswer"])
        else:
            print()
    # pprint(q)


if __name__ == "__main__":
    getAnswer(input())