import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# 配置
chatgpt_url = "https://chat.openai.com/"
cookies_path = "cookies.json"

# 启动 Chrome 浏览器
options = uc.ChromeOptions()
# 如果需要加载现有的用户数据，取消下行注释并配置路径
options.add_argument(r"user-data-dir=C:\\Users\\liangkaishui\\AppData\\Local\\Google\\Chrome\\User Data")
driver = uc.Chrome(options=options)

try:
    # 打开 ChatGPT 网站
    driver.get(chatgpt_url)
    time.sleep(5)  # 等待页面加载

    # 手动登录过程：如果你未登录，你需要手动进行登录
    print("请手动登录 ChatGPT")
    time.sleep(90)  # 等待用户手动登录并完成验证（时间可根据情况调整）

    # 登录后获取 Cookies
    cookies = driver.get_cookies()
    with open(cookies_path, "w") as file:
        file.write(str(cookies))

    print(f"Cookies 已保存到 {cookies_path}")

finally:
    driver.quit()
