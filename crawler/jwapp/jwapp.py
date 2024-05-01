import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


class Student:
    """
    学生类，用于访问各自的成绩
    """

    enquirer_id = "0212020266"  # 默认账号
    enquirer_token = ""
    headers = {
        "Host": "jwapp.xjtu.edu.cn",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; SDY-AN00 Build/HONORSDY-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36 toon/2122313098 toonType/150 toonVersion/6.3.0 toongine/1.0.12 toongineBuild/12 platform/android language/zh skin/white fontIndex/0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/json;charset=UTF-8",
        "X-Requested-With": "synjones.commerce.xjtu",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    @staticmethod
    def ping(isPrint=False):
        """
        用默认账号检查网络是否联通，返回http://jwapp.xjtu.edu.cn/app/index网页response
        """
        response = requests.get(
            "http://jwapp.xjtu.edu.cn/app/index",
            params={"code": "", "employeeNo": Student.enquirer_id},
            headers=Student.headers,
            allow_redirects=False,
        )
        if isPrint:
            print(response.headers)
        Student.enquirer_token = response.headers["location"].split("token=")[1]
        return response

    @staticmethod
    def default():
        """
        返回默认账号的Student对象
        """
        return Student(Student.enquirer_id)

    def __init__(self, id):
        """
        初始化学号为id的Student对象
        """
        self.id = str(id)
        self.token = (
            requests.get(
                "http://jwapp.xjtu.edu.cn/app/index",
                params={"code": "1", "employeeNo": self.id},
                headers=Student.headers,
                allow_redirects=False,
            )
            .headers["location"]
            .split("token=")[1]
        )
        self.headers = Student.headers.copy()
        self.headers["Authorization"] = self.token
        self.info = self.user_info()

    def post(self, suffix, data="{}"):
        """
        用当前学生账号向http://jwapp.xjtu.edu.cn/suffix发送装有data数据的post信息，返回response
        """
        return requests.post(
            "http://jwapp.xjtu.edu.cn/" + suffix, headers=self.headers, data=data
        )

    def user_info(self):
        """
        返回当前学生的info信息dict
        """
        return json.loads(self.post("api/biz/v410/user/info").text)

    def score_termList(self):
        """
        返回当前学生的termList信息dict
        """
        return json.loads(self.post("api/biz/v410/score/termList").text)["data"]

    def score_statistics(self, termCode="*"):
        """
        返回当前学生termCode学期的整体成绩信息dict
        """
        return json.loads(
            self.post(
                "api/biz/v410/score/statistics", json.dumps({"termCode": termCode})
            ).text
        )["data"]

    def score_statistics_all(self):
        """
        返回当前学生所有学期的整体成绩信息DataFrame
        """
        termList = self.score_termList()
        data = pd.DataFrame(
            columns=["termCode", "termName", "gpa", "credits", "currentFlag", "tipMsg"]
        )
        for term in termList:
            data.loc[len(data)] = {
                **term,
                **self.score_statistics(term["termCode"]),
            }
        return data

    def score_termScore(self, termCode="*"):
        """
        返回当前学生termCode学期的细节成绩信息dict
        """
        return json.loads(
            self.post(
                "api/biz/v410/score/termScore", json.dumps({"termCode": termCode})
            ).text
        )

    def score_all(self, termCode="*"):
        """
        返回当前学生所有学期的细节成绩信息DataFrame
        """
        termScoreList = self.score_termScore(termCode)["data"]["termScoreList"]
        data = pd.DataFrame(
            columns=[
                "id",
                "termCode",
                "courseName",
                "score",
                "passFlag",
                "coursePoint",
                "examType",
                "majorFlag",
                "examProp",
                "replaceFlag",
                "specificReason",
            ]
        )
        for termScore in termScoreList:
            for score in termScore["scoreList"]:
                data.loc[len(data)] = score
        data = data.drop_duplicates(subset=["id"], keep="last").reset_index()
        data.drop("index", inplace=True, axis=1)
        return data

    def get_course(self, name, termCode="*"):
        """
        查询当前学生termCode学期中名称中含有name的一门课程的粗略的成绩信息，返回为dict
        """
        data = self.score_all(termCode)
        for k, v in enumerate(data["courseName"]):
            if name in v:
                break
        course = data.loc[k]
        return dict(course)

    def score_detail(self, id):
        """
        查询当前学生关于get_course所得到的粗略成绩信息id的更详尽的成绩信息，返回为dict
        """
        if isinstance(id, dict):
            id = id["id"]
        return json.loads(
            self.post("api/biz/v410/score/scoreDetail", json.dumps({"id": id})).text
        )["data"]


class Address:
    """
    地址类，用于操作通讯录以获取学生列表
    """

    def __init__(self, enquirer=Student.default()):
        """
        初始化一个地址器
        """
        if (isinstance(enquirer, int) or isinstance(enquirer, str)):
            enquirer = Student(enquirer)
        self.enquirer = enquirer
        self.path = "/"

    def reset(self):
        """
        重置地址器，使其指向通讯录根目录
        """
        self.path = "/"
        return self

    def list(self):
        """
        返回当前地址下的所有学生信息DataFrame
        """
        a = json.loads(
            self.enquirer.post(
                "api/msg/v410/message/listContact",
                json.dumps({"parentPath": self.path}),
            ).text
        )["data"]["rows"]
        data = pd.DataFrame(columns=list(a[0].keys()))
        for v in a:
            data.loc[len(data)] = v
        return data

    def list_id(self):
        """
        返回当前地址下的所有学生学号id dict
        """
        return list(self.list()["objectId"])

    def goto(self, *params):
        """
        使当前地址器往params所列出的（模糊）信息依次往下移动，直至path达最长，此为最小一个班的同学录
        """
        if len(params) == 1:
            name = params[0]
            data = self.list()
            for k, v in enumerate(data["objectName"]):
                if name in v:
                    break
            self.path = data.loc[k]["path"]
        else:
            for i in params:
                self.goto(i)
        return self


class StudentList:
    """
    学生列表类，用于同时管理多个学生
    """

    def __init__(self, ids):
        """
        用学生学号列表ids初始化学生列表
        """
        if (isinstance(ids, Address)):
            ids = ids.list()["objectId"]
        elif (isinstance(ids, pd.DataFrame)):
            if ("objectId" in ids.columns):
                ids = ids["objectId"]
            elif ("xh" in id.columns):
                ids = ids["xh"]
        self.students = []
        for i in ids:
            self.students.append(Student(i))

    def scores_detail(self, name):
        """
        返回当前学生列表下所有学生名称中含有name的一门课程的详尽成绩信息，返回为DataFrame
        """
        data = pd.DataFrame(
            columns=[
                "xh",
                "xm",
                "score",
                "itemList",
                "gpa",
                "coursePoint",
                "phonenumber",
                "zymc",
                "yxmc",
                "classname",
                "courseName",
                "examType",
                "majorFlag",
                "examProp",
                "replaceFlag",
                "passFlag",
                "specificReason",
            ]
        )
        for s in self.students:
            data.loc[len(data)] = {**s.info, **s.score_detail(s.get_course(name))}
        return data

if __name__ == "__main__":
    pass