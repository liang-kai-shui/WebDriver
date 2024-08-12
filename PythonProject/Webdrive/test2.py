import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def main():
    chatgpt_url = "https://chat.openai.com/"
    cookies_path = "cookies.json"  

    # 创建 undetected Chrome WebDriver 实例
    options = uc.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\\Users\\liangkaishui\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = uc.Chrome(options=options)

    # 打开 ChatGPT 网页并加载 Cookies
    driver.get(chatgpt_url)
    load_cookies(driver, cookies_path)
    driver.refresh()

    time.sleep(2)

    def get_input_box():
        wait = WebDriverWait(driver, 120)
        return wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))

    # 等待页面加载完成，并找到输入框
    try:
        input_box = get_input_box()
        print("已找到输入框")
    except Exception as e:
        print(f"定位输入框时出错: {e}")
        driver.quit()
        return

    def get_chatgpt_response(message):
        nonlocal input_box
        try:
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
                        # 如果响应文本在4秒内没有变化，假设响应已完成
                        time.sleep(4)
                        new_response = driver.find_elements(By.CSS_SELECTOR, "div[class*='group/conversation-turn']")
                        if new_response[-1].text == response_text:
                            break
            return response_text
        except StaleElementReferenceException:
            print("输入框变得无效，重新获取...")
            input_box = get_input_box()
            return get_chatgpt_response(message)

    # 开始终端交互
    while True:
        user_input = input("请输入你想问ChatGPT的问题（输入'退出'结束程序）：")
        if user_input.lower() == '退出':
            print("程序结束。")
            break
        
        chatgpt_response = get_chatgpt_response(user_input)
        print(f"ChatGPT 回复：{chatgpt_response}")

    driver.quit()

def load_cookies(driver, cookies_path):
    try:
        with open(cookies_path, 'r') as file:
            cookies = json.load(file).split('; ')
            for cookie in cookies:
                name, value = cookie.split('=', 1)
                driver.add_cookie({'name': name, 'value': value, 'domain': '.openai.com', 'path': '/'})
    except FileNotFoundError:
        print("无法加载 Cookies: 文件不存在")

if __name__ == "__main__":
    main()
