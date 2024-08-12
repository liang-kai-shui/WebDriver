import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import requests
import os

def save_image(image_url, save_path):
    try:
        img_data = requests.get(image_url).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)
        print(f"图像已保存到 {save_path}")
    except Exception as e:
        print(f"保存图像时出错: {e}")

def load_cookies(driver, cookies_path):
    try:
        with open(cookies_path, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        print("无法加载 Cookies: 文件不存在")
    except json.JSONDecodeError:
        print("无法解析 Cookies 文件")

def chat_mode(driver, input_box):
    while True:
        user_input = input("请输入你想问ChatGPT的问题（输入'切换模式'切换到画图模式，输入'退出'结束程序）：")
        if user_input.lower() == '切换模式':
            return 'switch'
        if user_input.lower() == '退出':
            print("程序结束。")
            return 'exit'
        
        try:
            # 清空输入框并发送消息
            input_box.clear()
            input_box.send_keys(user_input)
            input_box.send_keys(Keys.RETURN)

            # 等待 ChatGPT 响应
            response_text = ""
            while True:
                time.sleep(1)  # 每秒检查一次
                new_response = driver.find_elements(By.CSS_SELECTOR, "div[class*='group/conversation-turn']")((((((((((((()))))))))))))
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
            print(f"ChatGPT 回复：{response_text}")
        except StaleElementReferenceException:
            print("输入框变得无效，重新获取...")
            input_box = get_input_box(driver)

def image_mode(driver, input_box):
    image_counter = 1  # 初始化图像计数器
    while True:
        user_input = input("请输入你想让ChatGPT生成的图像描述（输入'切换模式'切换到聊天模式，输入'退出'结束程序）：")
        if user_input.lower() == '切换模式':
            return 'switch'
        if user_input.lower() == '退出':
            print("程序结束。")
            return 'exit'
        
        try:
            # 清空输入框并发送消息
            input_box.clear()
            input_box.send_keys(user_input)
            input_box.send_keys(Keys.RETURN)

            # 等待图像生成并保存
            image_url = get_image_from_response(driver)
            if image_url:
                save_path = f"generated_image{image_counter}.png"
                save_image(image_url, save_path)
                print(f"图像已生成并保存为 {save_path}")
                image_counter += 1  # 更新图像计数器
        except StaleElementReferenceException:
            print("输入框变得无效，重新获取...")
            input_box = get_input_box(driver)

def get_input_box(driver):
    wait = WebDriverWait(driver, 120)
    return wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))

def get_image_from_response(driver):
    try:
        image_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
            "#__next > div > div.relative.flex.h-full.max-w-full.flex-1.flex-col.overflow-hidden > main > div.flex.h-full.flex-col.focus-visible\\:outline-0 > div.flex-1.overflow-hidden > div > div > div > div > div:nth-child(3) > div > div > div.group\\/conversation-turn.relative.flex.w-full.min-w-0.flex-col.agent-turn > div > div.flex.max-w-full.flex-col.flex-grow > div.grid.gap-2.grid-cols-1.my-1.transition-opacity.duration-300 > div > div > div > div.relative.h-full > img"))
        )
        image_url = image_element.get_attribute('src')
        return image_url
    except Exception as e:
        print(f"无法获取图像: {e}")
        return None

def main():
    chatgpt_url = "https://chat.openai.com/"
    cookies_path = "D:\Code\PythonProject\Webdrive\cookies.json"

    options = uc.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\\Users\\liangkaishui\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = uc.Chrome(options=options)

    # 打开 ChatGPT 网页并加载 Cookies
    driver.get(chatgpt_url)
    load_cookies(driver, cookies_path)
    driver.refresh()

    time.sleep(2)

    input_box = get_input_box(driver)

    current_mode = '聊天模式'
    while True:
        if current_mode == '聊天模式':
            result = chat_mode(driver, input_box)
        elif current_mode == '画图模式':
            result = image_mode(driver, input_box)

        if result == 'switch':
            current_mode = '画图模式' if current_mode == '聊天模式' else '聊天模式'
            print(f"已切换到 {current_mode}")
        elif result == 'exit':
            break

    driver.quit()

if __name__ == "__main__":
    main()
