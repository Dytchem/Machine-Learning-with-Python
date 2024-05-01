import json

import requests


def getAnswer(aId):
    url = "http://www.icourse163.org/mob/course/paperDetail/v1"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = (
        "mob-token=0f09b2b7630c129548d74dddd9eb97619a7891423fd6b617a0b8bde4b64c45ae398b3d63cb5fd52eef52676df13af54c76a799785561dc0ef8c10c98d0192f7529052a64e3eb0e2f6fdddaee44a6ed1e3fe82d8881bd18d30e2ebd9980e23f4b0d7ef1ee30366d043e17db84286433ce431fa5380bde4a7f17bdd49a3580fc84bdf8e751bb17227e812f9f3526a4c2d0a44713ec5840b51a00087d8e176e19a38676b27e0d374f2f0db184284eeb568ef068144cfcbaf5b449620a83b20dcbf5&testId=1242838683&isExercise=false&aId="
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
        print()


if __name__ == "__main__":
    getAnswer(input())