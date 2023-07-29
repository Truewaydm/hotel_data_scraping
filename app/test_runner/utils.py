import re

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def wait_for_element(driver: 'WebDriver', locator: str, value: str, timeout_sec: float = 10) -> 'WebElement':
    """Wait until the element located

    Args:
        driver: WebDriver instance
        locator: Locator like WebDriver, Mobile JSON Wire Protocol
            (e.g. `appium.webdriver.common.appiumby.AppiumBy.ACCESSIBILITY_ID`)
        value: Query value to locator
        timeout_sec: Maximum time to wait the element. If time is over, `TimeoutException` is thrown

    Raises:
        `selenium.common.exceptions.TimeoutException`

    Returns:
        The found WebElement
    """
    return WebDriverWait(driver, timeout_sec).until(expected_conditions.presence_of_element_located((locator, value)))


def replace_date_format(input_text):
    def add_leading_zero(number):
        return f'{int(number):02d}'

    months_dict = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    pattern = r'(\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\b)'
    result = re.sub(pattern, lambda match: f'{add_leading_zero(match.group(3))}.{months_dict[match.group(2)]}.2023',
                    input_text)
    result = result.replace(' → ', '-')
    return result
