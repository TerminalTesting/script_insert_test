# -*- coding: utf-8 -*-
import unittest
import sys
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class VSChangesTest(unittest.TestCase):

    #delete old screenshot artifacts. Not in setUp method because it`s run for every test
    os.system('find -iname \*.png -delete')

    def setUp(self):
        
        self.base_url = 'http://nsk.%s/' % os.getenv('SITE')
        self.ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
        self.INSERT_LIST_DESC = 'terminal/admin/site/terminal/tjsinsert/list?filter[_sort_order]=DESC&filter[_sort_by]=id&filter[_page]=1'
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.SCRIPTS_ADD = {'title': 'AutotestScriptAdd',
                            'head_insert': '<script type="text/javascript" id="headInsertID">\n    //javascript\n</script>',
                            'body_insert': '<script type="text/javascript" id="bodyInsertID">\n    //javascript\n</script>'
                            }


    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""

        self.driver.get('%slogout' % self.base_url)
        self.driver.close()
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    
    def remove_tags(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def is_element_present(self, how, what, timeout = 10, screen = True):
        """ Поиск элемента по локатору

            По умолчанию таймаут 10 секунд, не влияет на скорость выполнения теста
            если элемент найден, если нет - ждет его появления 10 сек
            
            Параметры:
               how - метод поиска
               what - локатор
            Методы - атрибуты класса By:
             |  CLASS_NAME = 'class name'
             |  
             |  CSS_SELECTOR = 'css selector'
             |  
             |  ID = 'id'
             |  
             |  LINK_TEXT = 'link text'
             |  
             |  NAME = 'name'
             |  
             |  PARTIAL_LINK_TEXT = 'partial link text'
             |  
             |  TAG_NAME = 'tag name'
             |  
             |  XPATH = 'xpath'
                                             """
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((how, what)))
        except:
            print u'Элемент не найден'
            print 'URL: ', self.driver.current_url
            print u'Метод поиска: ', how
            print u'Локатор: ', what
            if screen:
                screen_name = '%d.png' % int(time.time())
                self.driver.get_screenshot_as_file(screen_name)
                print u'Скриншот страницы: ', self.ARTSOURCE + screen_name
            raise Exception('ElementNotPresent')

    def test_script_insert_add(self):

        driver = self.driver
        element = self.is_element_present
        result = True # True is the correct result

        #login
        driver.get('%slogin' % self.base_url)
        element(By.ID, 'username').send_keys(os.getenv('AUTH'))
        element(By.ID, 'password').send_keys(os.getenv('AUTHPASS'))
        element(By.CLASS_NAME, 'btn-primary').click()
        time.sleep(7)

        #add new script insert
        driver.get(self.base_url + self.INSERT_LIST_DESC)
        element(By.LINK_TEXT, u"Добавить новый").click()

        #add title
        element(By.CSS_SELECTOR, 'input[id*="_title"]').clear()
        element(By.CSS_SELECTOR, 'input[id*="_title"]').send_keys("AutotestScriptAdd")

        #select domain where scripts should be insert
        element(By.CSS_SELECTOR, 'input[id*="_domains_9"]').click()

        #select show rules(don`t show on terminal)
        Select(element(By.CSS_SELECTOR, 'select[id*="_showRules"]')).select_by_visible_text(u"исключая терминалы")

        #insert code to head
        element(By.CSS_SELECTOR, 'textarea[id*="_contentHead"]').clear()
        element(By.CSS_SELECTOR, 'textarea[id*="_contentHead"]').send_keys(self.SCRIPTS_ADD['head_insert'])

        #insert code to body
        element(By.CSS_SELECTOR, 'textarea[id*="_contentBody"]').clear()
        element(By.CSS_SELECTOR, 'textarea[id*="_contentBody"]').send_keys(self.SCRIPTS_ADD['body_insert'])
        
        #save insert settings
        element(By.NAME, 'btn_create_and_list').click()

        #open DESC insert list page
        driver.get(self.base_url + self.INSERT_LIST_DESC)

        #searching element
        element(By.LINK_TEXT, self.SCRIPTS_ADD['title'])
        """Do nothing and let test finish if element was found,
           else raise ElementNotPresent exception """

        assert result, ('Error')


    def test_script_insert_check(self):

        driver = self.driver
        element = self.is_element_present
        cnt = 0

        #main page should contains this insert with those settings
        driver.get(self.base_url)
        
        try:
            head_script = element(By.TAG_NAME, 'head').find_element_by_id('headInsertID')
            
        except:
            head_script = False
            cnt += 1
            print u'Элемент не найден'
            print 'URL: ', self.driver.current_url
            print u'Метод поиска: ', 'by id'
            print u'Локатор: ', 'headInsertID'
            print '*'*80

        try:
            body_script = element(By.TAG_NAME, 'body').find_element_by_id('bodyInsertID')
            
        except:
            body_script = False
            cnt += 1
            print u'Элемент не найден'
            print 'URL: ', self.driver.current_url
            print u'Метод поиска: ', 'by id'
            print u'Локатор: ', 'bodyInsertID'
            print '*'*80

        
        if head_script:
            if head_script.get_attribute('innerHTML') != self.remove_tags(self.SCRIPTS_ADD['head_insert']):
                cnt += 1
                print u'Вставка кода не соответствует'
                print u'Необходимо: \n', self.remove_tags(self.SCRIPTS_ADD['head_insert'])
                print u'На странице: \n', head_script.get_attribute('innerHTML')
                print 'URL: ', driver.current_url 
                print '*'*80

        if body_script:
            if body_script.get_attribute('innerHTML') != self.remove_tags(self.SCRIPTS_ADD['body_insert']):
                cnt += 1
                print u'Вставка кода не соответствует'
                print u'Необходимо: \n', self.remove_tags(self.SCRIPTS_ADD['body_insert'])
                print u'На странице: \n', body_script.get_attribute('innerHTML')
                print 'URL: ', driver.current_url 
                print '*'*80

        assert cnt == 0, (u'Errors: %d' % cnt)

    def test_script_insert_check_terminal(self):
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", os.getenv('USERAGENT'))  #set useragent
        self.driver = webdriver.Firefox(profile)  #associate with another object
        driver = self.driver
        element = self.is_element_present
        cnt = 0

        #main page shouldn`t contains in terminal this insert with those settings
        driver.get(self.base_url)

        try:
            head_script = element(By.TAG_NAME, 'head', screen = False).find_element_by_id('headInsertID')
            cnt += 1
            print u'Элемент найден, хотя настройками запрещена вставка в терминальную версию'
            print 'USERAGENT: ', os.getenv('USERAGENT')
            print u'Метод поиска: ', 'by id'
            print u'Локатор: ', 'headInsertID'
            print 'URL: ', driver.current_url
            print '*'*80

        except:
            pass

        try:
            body_script = element(By.TAG_NAME, 'body', screen = False).find_element_by_id('bodyInsertID')
            cnt += 1
            print u'Элемент найден, хотя настройками запрещена вставка в терминальную версию'
            print 'USERAGENT: ', os.getenv('USERAGENT')
            print u'Метод поиска: ', 'by id'
            print u'Локатор: ', 'bodyInsertID'
            print 'URL: ', driver.current_url
            print '*'*80
            
        except:
            pass
        

        assert cnt == 0, (u'Errors: %d' % cnt)

    def test_script_insert_delete(self):

        driver = self.driver
        element = self.is_element_present
        result = True  # True is the correct result

        #login
        driver.get('%slogin' % self.base_url)
        element(By.ID, 'username').send_keys(os.getenv('AUTH'))
        element(By.ID, 'password').send_keys(os.getenv('AUTHPASS'))
        element(By.CLASS_NAME, 'btn-primary').click()
        time.sleep(7)
        

        #open DESC insert list page
        driver.get(self.base_url + self.INSERT_LIST_DESC)

        #delete last add test
        element(By.LINK_TEXT, self.SCRIPTS_ADD['title']).click()
        element(By.LINK_TEXT, u'Удалить').click()
        element(By.CSS_SELECTOR, 'input.btn.btn-danger').click()

        #open DESC insert list page
        driver.get(self.base_url + self.INSERT_LIST_DESC)

        #searching element
        try:
            element(By.LINK_TEXT, self.SCRIPTS_ADD['title'])
            result = False  # change result to False - test failed
            print u'Элемент не удалился'
            print 'URL: ', driver.current_url
            driver.get_screenshot_as_file('script_delete_error.png')
            print u'Скриншот страницы: ', self.ARTSOURCE + 'script_delete_error.png'
	    
        except:
            pass

        assert result, (u'Error')
