import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains   # for auto scroll
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserAuto:
    SPEED_DEFAULT = 1  # wait sec
    MAX_WAIT_CNT = 500

    def __init__(self, addr_park):
        self.addr_park= addr_park
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver = webdriver.Chrome()
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(self.addr_park)
        self.driver.implicitly_wait(10)

        self.speed_init()

    def speed_init(self):
        self.WAIT_SEC = self.SPEED_DEFAULT
        self.WAIT_SEC_CALENDAR = self.SPEED_DEFAULT

    def speed_up(self):
        self.WAIT_SEC = 0.05

    def scroll_to_element(self, element):
        # self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

        str_script_center = 'var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);' \
                            + 'var elementTop = arguments[0].getBoundingClientRect().top;' \
                            + 'window.scrollBy(0, elementTop-(viewPortHeight/2));'

        self.driver.execute_script(str_script_center, element)

    def do_action(self, strCommand, dict_arg):
        bRun = True
        cnt = 0
        ok = 0; msg = 'false'
        while bRun:
            try:
                if cnt > self.MAX_WAIT_CNT:
                    print('Error: cnt > self.MAX_WAIT_CNT')
                    bRun = False
                time.sleep(self.WAIT_SEC)
                ok, msg = self._switch(strCommand, dict_arg)
                bRun = False
            except (selenium.common.exceptions.StaleElementReferenceException, selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.ElementNotInteractableException) as err:
                print('Exception: ', err)
                print('Wait and try again')
                cnt = cnt + 1

        return ok, msg

    def _switch(self, strCommand, dict_arg):
        fun_switch = {
            'click': self._click,
            'click_id': self._click_id,
            'fill_text': self._fill_text,
            'select_inx': self._select_inx,
            'set_yyyymmdd': self._set_yyyymmdd,
            'fill_text_verify':self._fill_text_verify,
        }

        return fun_switch[strCommand](dict_arg)

    def click(self, strTitle):
        dict_arg = {}
        dict_arg['strTitle'] = strTitle
        return self.do_action('click', dict_arg)

    def _click(self, dict_arg):
        strTitle = dict_arg['strTitle']
        str_comm = '//*[@title="' + strTitle + '"]'
        element = self.driver.find_element_by_xpath(str_comm)
        self.scroll_to_element(element)
        element.click()

        #FIXME: always return pass
        return 1, 'ok'

    def get_attribute(self, str_type, strID):
        element = self._get_elm_id(strID)
        str_value = element.get_attribute(str_type)
        print('strID = ', strID, ' str_value = ', str_value)
        return str_value



    def click_id(self, strID):
        dict_arg = {}
        dict_arg['strID'] = strID
        return self.do_action('click_id', dict_arg)

    def _click_id(self, dict_arg):
        strID = dict_arg['strID']
        element = self._get_elm_id(strID)
        element.click()

        #FIXME: always return pass
        return 1, 'ok'

    def fill_text(self, strID, strText, b_refilled):
        return self.fill_text_core('fill_text', strID, strText, b_refilled)

    def fill_text_verify(self, strID, strText):
        try:
            ok, msg = self.fill_text_core('fill_text_verify', strID, strText, 0)
            return 1, msg
        except Exception as e:
            import traceback
            traceback.print_exc()
            return 0, 'self.fill_text_core Exception'

    def fill_text_core(self, str_funName, strID, strText, b_refilled):
        dict_arg = {}
        dict_arg['strID'] = strID
        dict_arg['strText'] = strText
        dict_arg['b_refilled'] = b_refilled

        return self.do_action(str_funName, dict_arg)

    def _fill_text(self, dict_arg):
        strID = dict_arg['strID']
        strText = dict_arg['strText']
        b_refilled = dict_arg['b_refilled']
        element = self._get_elm_id(strID)
        self.scroll_to_element(element)

        if b_refilled:
            from selenium.webdriver.common.keys import Keys
            element.send_keys(Keys.CONTROL, 'a')
        element.send_keys(strText)

        #FIXME: always return pass
        return 1, 'ok'

    def _fill_text_verify(self, dict_arg):
        strID = dict_arg['strID']
        strText = dict_arg['strText']
        element = self._get_elm_id(strID)
        self.scroll_to_element(element)

        if element.get_attribute('value') == strText:
            return 1, 'ok'
        else:
            return 0, 'Not Matched: element.text = {}, strText = {}\n'.format(element.text, strText)


    def select_inx(self, strID, inx):
        dict_arg = {}
        dict_arg['strID'] = strID
        dict_arg['inx'] = inx
        return self.do_action('select_inx', dict_arg)

    def _select_inx(self, dict_arg):
        strID = dict_arg['strID']
        inx = dict_arg['inx']
        element = self._get_elm_id(strID)
        self.scroll_to_element(element)
        sele = Select(element)
        sele.select_by_index(inx)

        #FIXME: always return pass
        return 1, 'ok'

    def set_yyyymmdd(self, strID, yyyy, mm, date):
        dict_arg = {}
        dict_arg['strID'] = strID
        dict_arg['yyyy'] = yyyy; dict_arg['mm'] = mm; dict_arg['date'] = date
        return self.do_action('set_yyyymmdd', dict_arg)

    def _set_yyyymmdd(self, dict_arg):
        strID = dict_arg['strID']
        yyyy = dict_arg['yyyy']
        mm = dict_arg['mm']
        date = dict_arg['date']

        self.click_id(strID)
        time.sleep(self.WAIT_SEC_CALENDAR)
        element = self.driver.find_element_by_class_name('ui-datepicker-year')
        sele = Select(element)
        sele.select_by_index(int(yyyy)-1929)  # 0: 1929

        time.sleep(self.WAIT_SEC_CALENDAR)
        element = self.driver.find_element_by_class_name('ui-datepicker-month')
        sele = Select(element)
        sele.select_by_index(int(mm)-1)  # 0: 一月

        elements = self.driver.find_elements_by_xpath(".//*[@id='ui-datepicker-div']/table/tbody/tr/td/a")
        for dates in elements:
            if(dates.is_enabled() and dates.is_displayed() and str(dates.get_attribute("innerText")) == str(date)):
                dates.click()

        #FIXME: always return pass
        return 1, 'ok'

    def handle_alert_popup(self):
        # wait for alert window
        # prevent:
        #  Message: unexpected alert open: {Alert text :

        element = WebDriverWait(self.driver, 10).until(
            EC.alert_is_present()
        )

        # accept
        alert = self.driver.switch_to_alert()
        alert.accept()

    def _get_elm_id(self, strID):
        # https://selenium-python.readthedocs.io/waits.html
        # from selenium.webdriver.common.by import By
        # from selenium.webdriver.support.ui import WebDriverWait
        # from selenium.webdriver.support import expected_conditions as EC

        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, strID)) and
            EC.element_to_be_clickable((By.ID, strID))
        )

        return element
