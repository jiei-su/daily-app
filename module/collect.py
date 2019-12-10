"""
スクレイピング用モジュール.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import chromedriver_binary
import dbaccess
import log

# Headlessモード定義
OPTS = Options()
OPTS.add_argument('--headless')
OPTS.add_argument('--no-sandbox')
OPTS.add_argument('--disable-dev-shm-usage')
DRIVER = webdriver.Chrome('./lib/chromedriver', options=OPTS)


class Scraping:
    """
    スクレイピング用クラス.
    """

    def get_target_from_db(self, target: str) -> dict:
        """
        リアルタイムで収集する情報（天気予報、運行情報）のURLをDBから取得する.

        param:
            target 収集情報のキーワード

        return:
            target_info {目的地(路線):url}
        """

        if target == 'weather':
            try:
                db = dbaccess.Weather()
            except RuntimeError:
                log.error('get_target_from_db: RuntimeError')
                return False
        elif target == 'train':
            try:
                db = dbaccess.Train()
            except RuntimeError:
                log.error('get_target_from_db: RuntimeError')
                return False

        target_info = db.select_all()
        if len(target_info) == 0:
            log.error('get_target_from_db: target_info is None')
            return None
        if target_info is False:
            log.error('get_target_from_db: target_info is False')
            return False
            
        return target_info

    def collect_weather(self) -> dict:
        """
        天気予報をスクレイピングする.

        return:
            weather_info {場所:{時間:[コメント,気温]}
        """

        results = self.get_target_from_db('weather')
        if results is None:
            return None
        elif results is False:
            return False

        weather_info = {}
        for row in results:
            place = row['place']
            
            try:
                DRIVER.get(row['url'])
            except Exception:
                log.error('collect_weather: target url is None')
                return None

            try:
                selenium_obj = DRIVER.find_element_by_class_name("hour")
                times = selenium_obj.text
                not_current_time = [
                    val.text
                    for val in selenium_obj.find_elements_by_class_name("past")
                ]
                comments = DRIVER.find_element_by_class_name("weather").text
                temps = DRIVER.find_element_by_class_name("temperature").text
            except NoSuchElementException:
                log.error('collect_weather: target row is None')
                return None
            
            info = self.parse_weather(times, not_current_time, comments, temps)

            weather_info[place] = info

        return weather_info

    def parse_weather(self, times: list, not_current_time: list,
                      comments: list, temps: list) -> dict:
        """
        天気予報収集データを解析する.

        param:
            times 時間
            not_current_time 現在時刻以外
            comments コメント
            temps 気温

        return:
            info {時間:[コメント,気温]}
        """

        info = {}
        flag = False
        for time, com, temp in zip(times.split(), comments.split()[1:], temps.split()):
            disp_time = time.strip('0') + '時'

            if time not in not_current_time and flag is False:
                info[disp_time] = [com, temp, 'current']
                flag = True
            else:
                info[disp_time] = [com, temp]

        return info
 
    def collect_train(self) -> dict:
        """
        運行情報をスクレイピングする.

        return:
            train_info {路線:{heading:見出し,comment:コメント}}
        """

        results = self.get_target_from_db('train')
        if results is None:
            return None
        elif results is False:
            return False

        train_info = {}
        for row in results:
            try:
                DRIVER.get(row['url'])
            except Exception:
                log.error('collect_train: target url is None')
                return None

            try:
                service_status = DRIVER.find_element_by_id("mdServiceStatus").text
            except NoSuchElementException:
                log.error('collect_train: target info is None')
                return None

            service_info = self.parse_train(service_status)

            train_info[row['route']] = service_info

        return train_info

    def parse_train(self, service_status: str) -> dict:
        """
        運行情報収集データを解析する.

        param:
            service_status 運行情報

        return:
            info {heading:見出し,comment:コメント}
        """

        info = {}
        heading = service_status[3:].split('\n')[0]
        info['heading'] = heading

        comment = service_status[3:].split('\n')[1]
        info['comment'] = comment

        return info

    def close_driver(self):
        """
        driver閉じる.
        サイト毎にdriverをクローズし、再度、別サイト用に起動するとMaxRetryError
        そのため、全サイトのスクレイピング完了時に当関数をコールしdriverクローズ
        """

        DRIVER.close()
        DRIVER.quit()


class Insert:
    """
    新規追加情報をDBに登録.
    収集サイトを変更する場合、ロジックの変更が必要
    """

    def __init__(self):
        self.weather_traget = {
            """
            場所: 収集URL(tenki.jp)
            """
        }
        self.train_traget = {
            """
            路線: 収集URL(transit.yahoo.co.jp)
            """
        }
        self.english_traget = [
            """
            収集URL(eigo-duke.com)
            """
        ]

    def insert_weather(self) -> bool:
        """
        天気予報(収集URL)をDBに登録する.

        return:
            True
        """

        try:
            db = dbaccess.Weather()
        except RuntimeError:
            log.error('insert_weather: RuntimeError')
            return False

        for place in self.weather_traget:
            if db.insert(place, self.weather_traget[place]) is False:
                log.error('insert_weather: insert error')
                return False

        if db.commit() is False:
            log.error('insert_weather: commit error')
            return False

        log.info('insert_weather: commit Complete!')
        return True

    def insert_train(self) -> bool:
        """
        運行情報(収集URL)をDBに登録する.

        return:
            True
        """

        try:
            db = dbaccess.Train()
        except RuntimeError:
            log.error('insert_train: RuntimeError')
            return False

        for route in self.train_traget:
            if db.insert(route, self.train_traget[route]) is False:
                log.error('insert_train: insert error')
                return False

        if db.commit() is False:
            log.error('insert_train: commit error')
            return False

        log.info('insert_train: commit Complete!')
        return True

    def collect_english(self) -> list:
        """
        サイトから英単語、日本語を収集する.

        return:
            english_info 英単語
            japanese_info 日本語
        """

        english_info = []
        japanese_info = []
        for url in self.english_traget:
            try:
                DRIVER.get(url)
            except Exception:
                log.error('collect_english: target url is None')
                continue

            try:
                english_text = [
                    eng.text
                    for eng in DRIVER.find_elements_by_class_name("eng")
                ]
                japanese_text = [
                    jap.text
                    for jap in DRIVER.find_elements_by_class_name("jap")
                ]
            except NoSuchElementException:
                log.error('collect_english: target text is None')
                return None

            english_info.extend(english_text)
            japanese_info.extend(japanese_text)

        DRIVER.close()
        DRIVER.quit()

        return english_info, japanese_info

    def insert_english(self) -> bool:
        """
        英単語をDBに登録する.

        return:
            True
        """

        try:
            db = dbaccess.EnglishStudy()
        except RuntimeError:
            log.error('insert_english: RuntimeError')
            return False

        english_info, japanese_info = self.collect_english()
        for eng, jap in zip(english_info, japanese_info):
            if db.insert(eng, jap) is False:
                log.error('insert_english: insert error')
                return False

        if db.commit() is False:
            log.error('insert_english: commit error')
            return False

        log.info('insert_english: commit Complete!')
        return True