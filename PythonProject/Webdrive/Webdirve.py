import time
import os
import requests
import undetected_chromedriver as uc
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置
base_url = "http://localhost:8083"
auth_key = "INITKEYwYI7289c"
qq_number = "3232566494"
cookies_path = "D:\Code\PythonProject\Webdrive\cookies.json"
try:
    # ChatGPT 网页地址
    chatgpt_url = "https://chat.openai.com/"

    # 创建 undetected Chrome WebDriver 实例
    options = uc.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\\Users\\liangkaishui\\AppData\\Local\\Google\\Chrome\\User Data")

    driver = uc.Chrome(options=options)

    time.sleep(1.5)

    # 打开 ChatGPT 网页
    driver.get(chatgpt_url)
    driver.maximize_window

    # 加载 cookies

    with open(cookies_path, "r") as file:
        cookies = eval(file.read())

    # 过滤掉 httpOnly 的 cookies
    filtered_cookies = [cookie for cookie in cookies if not cookie.get('httpOnly', False)]

    # 确保 cookie 有必需的字段，并逐个添加
    for cookie in filtered_cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Unable to set cookie {cookie}: {e}")
    # 刷新页面以应用 cookies
    driver.refresh()

except:
    driver.quit()

# 等待页面加载完成，并找到输入框（可能需要调整时间和元素定位方法）
try:
    wait = WebDriverWait(driver, 120)  # 最多等待120秒
    input_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
    print("已找到输入框")
except Exception as e:
    print(f"Error locating input box: {e}")
    driver.save_screenshot("error_screenshot.png")  # 捕获错误时的屏幕截图
    driver.quit()
    exit(1)

def get_chatgpt_response(message):
    # 清空输入框
    input_box.clear()
    # 输入消息并发送
    input_box.send_keys(message)
    input_box.send_keys(Keys.RETURN)

    # 等待 ChatGPT 响应
    response_text = ""
    while True:
        time.sleep(1)  # 每秒检查一次
        new_response = driver.find_elements(By.CSS_SELECTOR, "div[class*='group/conversation-turn']")
        if new_response:
            new_text = new_response[-1].text
            if new_text != response_text:
                response_text = new_text
            else:
                # 如果响应文本在2秒内没有变化，假设响应已完成
                time.sleep(2)
                new_response = driver.find_elements(By.CSS_SELECTOR, "div[class*='group/conversation-turn']")
                if new_response[-1].text == response_text:
                    break
    return response_text

# 监听消息并回复
def listen_and_respond(session_key):
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        try:
            fetch_response = session.get(f"{base_url}/fetchMessage?sessionKey={session_key}")
            fetch_response.raise_for_status()  # 检查请求是否成功
            messages = fetch_response.json()

            # 打印 messages 内容以调试
            print("Fetched messages:", messages)

            # 检查 messages 是否为字典列表
            if isinstance(messages, dict) and "data" in messages:
                for message in messages["data"]:
                    if isinstance(message, dict):
                        if message.get("type") == "GroupMessage":
                            qq_message = ""
                            for chain in message["messageChain"]:
                                if chain["type"] == "At" and chain["target"] == int(qq_number):
                                    for sub_chain in message["messageChain"]:
                                        if sub_chain["type"] == "Plain":
                                            qq_message += sub_chain["text"]
                                    break

                            sender = message["sender"]["id"]
                            group_id = message["sender"]["group"]["id"]

                            if qq_message.strip():
                                # 获取 ChatGPT 响应
                                chatgpt_response = get_chatgpt_response(qq_message)
                                print(f"ChatGPT Response: {chatgpt_response}")

                                # 发送回复
                                send_response = session.post(f"{base_url}/sendGroupMessage", json={
                                    "sessionKey": session_key,
                                    "target": group_id,
                                    "messageChain": [{"type": "Plain", "text": chatgpt_response}]
                                })
                                send_response.raise_for_status()  # 检查请求是否成功
                                print(send_response.json())
                        elif message.get("type") == "FriendMessage":
                            qq_message = ""
                            for chain in message["messageChain"]:
                                if chain["type"] == "Plain":
                                    qq_message += chain["text"]

                            sender = message["sender"]["id"]

                            if qq_message.strip():
                                # 获取 ChatGPT 响应
                                chatgpt_response = get_chatgpt_response(qq_message)
                                print(f"ChatGPT Response: {chatgpt_response}")

                                # 发送回复
                                send_response = session.post(f"{base_url}/sendFriendMessage", json={
                                    "sessionKey": session_key,
                                    "target": sender,
                                    "messageChain": [{"type": "Plain", "text": chatgpt_response}]
                                })
                                send_response.raise_for_status()  # 检查请求是否成功
                                print(send_response.json())
            else:
                print("Unexpected message format:", messages)
        except requests.exceptions.RequestException as e:
            print(f"Error during message fetching/sending: {e}")
            time.sleep(5)  # 等待一段时间再重试
        except ValueError as ve:
            print(f"Error parsing JSON response: {ve}, response content: {fetch_response.content}")
            time.sleep(5)  # 等待一段时间再重试

if __name__ == "__main__":
    # 认证获取 session key
    try:
        auth_response = requests.post(f"{base_url}/verify", json={"verifyKey": auth_key})
        auth_response.raise_for_status()  # 检查请求是否成功

        # 打印响应内容以帮助调试
        print("Auth Response Content:", auth_response.content)

        session_key = auth_response.json()["session"]
        print("Authenticated successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        driver.quit()
        exit(1)
    except ValueError:
        print(f"Failed to parse JSON response: {auth_response.content}")
        driver.quit()
        exit(1)

    # 使用 session key 验证
    try:
        verify_response = requests.post(f"{base_url}/bind", json={"sessionKey": session_key, "qq": qq_number})
        verify_response.raise_for_status()  # 检查请求是否成功
        print("Verified successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error during verification: {e}")
        driver.quit()
        exit(1)

    listen_and_respond(session_key)
