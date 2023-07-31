import os
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
    """
    Replace date format
    :param input_text:
    :return: date format - 03.10.2023-04.10.2023
    """

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


def get_file_path(path: str, name_of_file: str):
    """
    Get the path to the JSON file
    :param path: Subdirectory within the 'app' directory where the file is located
    :param name_of_file: Name of the JSON file
    :return: Full path to the JSON file
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    app_directory = os.path.dirname(current_directory)
    return os.path.join(app_directory, path, name_of_file)
