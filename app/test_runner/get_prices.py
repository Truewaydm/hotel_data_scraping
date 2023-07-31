from appium.webdriver.common.appiumby import AppiumBy
from app.test_runner.utils import wait_for_element, replace_date_format

# Locators
BUTTON_HOTELS = "com.tripadvisor.tripadvisor:id/chip"
SEARCH_FIELD = "com.tripadvisor.tripadvisor:id/edtSearchString"
HOTEL = "//android.widget.TextView[@text='Robin Hoods Bay, North Yorkshire, England']"
DATE_PICKER = "com.tripadvisor.tripadvisor:id/txtDate"
BUTTON_APPLY = "com.tripadvisor.tripadvisor:id/btnPrimary"
BUTTON_VIEW_ALL_DEALS = "com.tripadvisor.tripadvisor:id/btnAllDeals"
FIRST_TOP_DEAL = "Booking.com"
OTHER_DEALS = "com.tripadvisor.tripadvisor:id/txtProviderName"
PRICE_DEAL = "com.tripadvisor.tripadvisor:id/txtPriceTopDeal"


def find_hotel_prices(driver, hotel_name, dates):
    """
    Find hotel prices:
    :param driver: WebDriver
    :param hotel_name: The Grosvenor Hotel
    :param dates:
                {"date": "date number"}
                ...
    :return: prices
    {
  "The Grosvenor Hotel": {
    "03.10.2023-04.10.2023": [
      {
        "Booking.com": "$86",
        "screenshot": "03.10.2023-04.10.2023.png"
      },
      ...
    }
    """
    driver.find_element(by=AppiumBy.ID, value=BUTTON_HOTELS).click()
    wait_for_element(driver, AppiumBy.ID, value=SEARCH_FIELD, timeout_sec=10).send_keys(hotel_name)
    wait_for_element(driver, AppiumBy.XPATH, value=HOTEL, timeout_sec=10).click()

    prices = {}
    for date in dates:
        driver.implicitly_wait(10)
        driver.find_element(by=AppiumBy.ID, value=DATE_PICKER).click()
        driver.find_element(by=AppiumBy.XPATH, value="//android.widget.TextView[@text='" + date["date"] + "']").click()
        driver.find_element(by=AppiumBy.ID, value=BUTTON_APPLY).click()
        if date["date"] == "3":
            wait_for_element(driver, AppiumBy.ID, value=BUTTON_VIEW_ALL_DEALS, timeout_sec=10).click()

        driver.implicitly_wait(30)
        date_picker = driver.find_element(by=AppiumBy.ID, value=DATE_PICKER).text
        date_format = replace_date_format(date_picker)
        date['date'] = date_format

        provider_names = []
        driver.implicitly_wait(30)
        booking_provider = (driver.find_element
                            (by=AppiumBy.ACCESSIBILITY_ID, value=FIRST_TOP_DEAL).get_attribute("content-desc"))
        provider_names.append(booking_provider)
        providers = driver.find_elements(by=AppiumBy.ID, value=OTHER_DEALS)
        for provider in providers:
            provider_names.append(provider.text)

        prices_names = []
        price_deal = driver.find_elements(by=AppiumBy.ID, value=PRICE_DEAL)
        for price in price_deal:
            prices_names.append(price.text)

        driver.implicitly_wait(30)
        screenshot_name = f"{date_format}.png"
        driver.save_screenshot(f"tests_screenshots/{screenshot_name}")

        price_info = []
        for i in range(len(provider_names)):
            if i < len(prices_names):
                price_info.append({
                    provider_names[i]: prices_names[i],
                    'screenshot': screenshot_name
                })
        prices[date_format] = price_info
    return prices
