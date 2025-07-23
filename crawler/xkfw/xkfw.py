# 配置参数（需根据实际情况修改）
id = 2225015585
addParam = '{"data":{"operationType":"1","studentCode":"2225015585","electiveBatchCode":"993582fa4e8a427aad4ed70ae992212e","teachingClassId":"202520261GNED10831001","isMajor":"1","campus":"5","teachingClassType":"XGXK","isAlternate":"0"}}'
deltaT = (0.5, 1.5)  # 随机间隔范围（秒）

# 邮件配置（需替换为真实信息）
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",  # QQ邮箱用smtp.qq.com，163邮箱用smtp.163.com
    "smtp_port": 465,  # SSL端口（常用465或587）
    "sender": "your_email@qq.com",  # 发件人邮箱
    "password": "your_auth_code",  # 发件人邮箱授权码（非登录密码）
    "receiver": "target@email.com",  # 收件人邮箱
}

import json
import random
import smtplib
import time
from email.mime.text import MIMEText

import requests


def send_email(subject, content):
    """发送邮件提醒"""
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["sender"]
    msg["To"] = EMAIL_CONFIG["receiver"]

    try:
        with smtplib.SMTP_SSL(
            EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]
        ) as server:
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.sendmail(
                EMAIL_CONFIG["sender"], [EMAIL_CONFIG["receiver"]], msg.as_string()
            )
        print("邮件提醒发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")


def main():
    url = "https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do"
    headers = {
        "Cookie": "GS_SESSIONID=1; _WEU=1; JSESSIONID=1",
        "token": None,
    }
    post_data = {"addParam": addParam}
    count = 0  # 监控计数器

    # 初始化获取token和基准msg
    try:
        login_res = requests.get(
            f"https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/mobile/register.do?number={id}",
            headers=headers,
            timeout=30,
        )
        headers["token"] = json.loads(login_res.text)["data"]["token"]

        baseline_res = requests.post(url, headers=headers, data=post_data, timeout=30)
        baseline_res.raise_for_status()
        baseline_msg = baseline_res.json().get("msg")
        if not baseline_msg:
            print("首次响应无有效'msg'字段，终止")
            return
        print(f"基准msg: {baseline_msg}")

    except Exception as e:
        print(f"初始化失败: {str(e)}")
        return

    # 监控主循环（保留原始302处理逻辑）
    while True:
        try:
            current_res = requests.post(
                url, headers=headers, data=post_data, timeout=30
            )
            current_res.raise_for_status()
            # 处理302重定向（保留原始逻辑）
            if current_res.json().get("code") == "302":
                re = requests.get(
                    f"https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/mobile/register.do?number={id}",
                    headers=headers,
                )
                headers["token"] = json.loads(re.text)["data"]["token"]
                continue  # 刷新token后继续当前循环

            count += 1  # 每次循环递增计数器
            current_msg = current_res.json().get("msg")

            # 核心判断逻辑（保留原始判断条件）
            if current_msg != baseline_msg:
                change_info = (
                    f"检测到msg变化！\n"
                    f"基准: {baseline_msg}\n"
                    f"当前: {current_msg}\n"
                    f"监控次数: {count}"
                )
                print(change_info)
                send_email("选课状态变更提醒", change_info)  # 触发邮件提醒
                break  # 终止监控

            # 正常监控提示（精简输出）
            print(f"第{count}次监控：msg一致，继续...")
            time.sleep(random.uniform(*deltaT))  # 随机间隔控制

        except json.JSONDecodeError:
            print("错误：响应非JSON格式，终止")
            break
        except Exception as e:
            print(f"请求异常（5秒后重试）: {str(e)}")
            time.sleep(5)


if __name__ == "__main__":
    main()