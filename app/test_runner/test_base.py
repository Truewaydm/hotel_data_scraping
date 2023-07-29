from appium import webdriver

desired_caps = {
    'platformName': 'Android',
    'deviceName': 'emulator-5554',
    'appPackage': 'com.tripadvisor.tripadvisor',
    'appActivity': 'com.tripadvisor.tripadvisor.TripAdvisorTripAdvisorActivity',
    'noReset': True,
    'automationName': "UiAutomator2"
}


def init_driver():
    return webdriver.Remote("http://localhost:4723", desired_caps)


def close_driver(driver):
    driver.quit()
