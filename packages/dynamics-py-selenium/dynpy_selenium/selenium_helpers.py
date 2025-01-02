from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumHelper(ABC):
    """
    Abstract class to help with generic selenium actions

    Usage:
        - create a subclass and define a _generate_driver method
        - initialize the subclass and call instance.set_driver()
        - access the driver through `instance.driver` or call any of
            the provided helper methods
    """

    def __init__(self) -> None:
        self.driver = None

    def set_driver(self) -> None:
        self.driver = self._generate_driver()

    @abstractmethod
    def _generate_driver(self) -> WebDriver:
        """Abstract method for creating the selenium webdriver"""

    def check_exists_by_selector(self, selector: str) -> bool:
        try:
            self.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return False
        return True

    def click_by_selector(self, selector: str) -> None:
        self.driver.find_element(By.CSS_SELECTOR, selector).click()

    def send_keys_by_selector(
        self, selector: str, keys: str, overwrite: bool = False
    ) -> None:
        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        if overwrite:
            elem.clear()
        elem.send_keys(keys)

    def wait_for_element_by_selector(self, selector: str, timeout: int = 100) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException as e:
            raise TimeoutException(
                f"Loading element `{selector}` took too much time!"
            ) from e


class ChromeSeleniumHelper(SeleniumHelper):
    """SeleniumHelper using a Chrome driver"""

    def _generate_driver(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
