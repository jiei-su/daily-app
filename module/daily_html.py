"""
HTML生成モジュール.
"""
import collect
import dbaccess
import log

# 静的ファイルのパス定義
CSS_PATH = 'static/css/'
JS_PATH = 'static/js/'
IMG_PATH = 'static/img/'


class CreateHtml:
    """
    天気予報、運行情報、英単語HTML生成クラス.
    """
    
    def __init__(self, target_list: list):
        """
        ヘッダ、フッタを生成する.

        param:
            target_list HTML作成対象リスト
        """

        self.ins = collect.Scraping()

        for target in target_list:
            self.target = target
            if self.target == 'weather':
                self.title = '天気予報'
            elif self.target == 'train':
                self.title = '運行情報'
            elif self.target == 'english':
                self.title = '今日の英単語'

            self.header = f'''
            <!DOCTYPE html>
            <html lang="ja">
            <head>
            <title>{ self.title }</title>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.css"/>
            <link rel="stylesheet" href="https://cdn.datatables.net/responsive/2.2.3/css/responsive.dataTables.min.css"/>
            <link rel="stylesheet" type="text/css" href="{ CSS_PATH }common.css">
            <link rel="stylesheet" type="text/css" href="{ CSS_PATH }{ self.target }.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
            <script src="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.js"></script>
            <script src="https://cdn.datatables.net/responsive/2.2.3/js/dataTables.responsive.min.js"></script>
            <script src="{ JS_PATH }common.js"></script>
            </head>
            <body>
            <header>
            <div id="headWrap">
            <h1>{ self.title }</h1>
            </div>
            </header>
            <main>'''

            self.footer = f'''
            </main>
            <footer>
            <div id="footerWrap">
            <div class="footerList"><a href="weather.html">天気予報</a></div>
            <div class="footerList"><a href="train.html">運行情報</a></div>
            <div class="footerList"><a href="english.html">今日の英単語</a></div>
            </div>
            </footer>
            </body>
            </html>'''

            self.create_html()

    def create_html(self):
        """
        ヘッダ、body、フッタを結合し、HTML生成.
        """

        html = self.header

        if self.target == 'weather':
            body = self.create_body_about_weather()
        elif self.target == 'train':
            body = self.create_body_about_train()
        elif self.target == 'english':
            body = self.create_body_about_english()
        
        if body is None:

            html += f'''
            <p class="leadText">収集に失敗しました<p>'''
        elif body is False:

            html += f'''
            <p class="leadText">データベースのアクセスに失敗しました<p>'''
        else:
            html += body

        html += self.footer

        create_html = f'../{ self.target }.html'
        with open(create_html, 'wb') as file:
            file.write(html.encode('utf-8'))
            log.info('create_html: Complete!')

    def create_body_about_weather(self) -> str:
        """
        天気予報のHTMLBody生成.
        """

        weather_info = self.ins.collect_weather()
        if weather_info is None:
            return None
        elif weather_info is False:
            return False

        body = ''
        for place, info in weather_info.items():

            body += f'''
            <section>
            <h2>{ place }</h2>
            <div class="content">'''

            for val in info.values():
                if 'current' in val:

                    body += f'''
                    <div class="current">
                    <p class="current-temp">{ val[1] }&deg;</p>
                    <p class="current-comment">{ val[0] }</p>
                    </div>'''

            body += '<div class="list">'
            for time, val in info.items():
                comment = val[0]
                
                if '晴' in comment:
                    icon = f'{ IMG_PATH }sun.png'
                elif '曇' in comment:
                    icon = f'{ IMG_PATH }cloud.png'
                elif '雨' in comment:
                    icon = f'{ IMG_PATH }rain.png'
                elif any(map(comment.__contains__, ('雪', 'みぞれ'))):
                    icon = f'{ IMG_PATH }snow.png'
                else:
                    icon = f'{ IMG_PATH }unknown.png'

                body += f'''
                <div class="time-unit">
                <p class="time">{ time }<p>
                <p class="icon"><img src="{ icon }" alt="{ comment }"><p>
                <p class="temp">{ val[1] }&deg;</p>
                </div>'''

            body += '</div></div></section>'

        return body

    def create_body_about_train(self) -> str:
        """
        運行情報のHTMLBody生成.
        """

        train_info = self.ins.collect_train()
        if train_info is None:
            return None
        elif train_info is False:
            return False

        body = ''
        for route, info in train_info.items():
            heading = info['heading']
            if heading == '平常運転':
                icon = f'{ IMG_PATH }circle.png'
            else heading == '列車遅延':
                icon = f'{ IMG_PATH }alert.png'

            body += f'''
            <section>
            <h2>{ route }</h2>
            <h3>
            <span><img src="{ icon }" alt="{ heading }"></span>
            { heading }
            <span><img src="{ icon }" alt="{ heading }"></span>
            </h3>
            <p class="comment">{ info['comment'] }</p>
            </section>'''

        return body

    def create_body_about_english(self) -> str:
        """
        英単語のHTMLBody生成.
        """

        try:
            db = dbaccess.EnglishStudy()
        except RuntimeError:
            return False

        english_info = db.select_random_english()
        if english_info is None:
            return None
        elif english_info is False:
            return False

        body = ''
        for row in english_info:

            body += f'''
            <div class="content">
            <p class="english">{ row['english'] }</p>
            <p class="japanese">{ row['japanese'] }</p>
            <button class="btn">答えを見る<button>
            </div>
            <script src="{ JS_PATH }{ self.target }.js"></script>'''

        return body

    def __del__(self):
        """
        driver閉じる.
        """

        log.info('__del__: driver close')
        self.ins.close_driver()


class Debug:
    """
    デバッグHTML生成クラス.
    """

    def __init__(self):
        """
        ヘッダ、フッタを生成する.
        """

        self.header = f'''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
        <title>デバッグ</title>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.css"/>
        <link rel="stylesheet" type="text/css" href="{ CSS_PATH }common.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <script src="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.js"></script>
        </head>
        <body>
        <header>
        <div id="headWrap">
        <h1>デバッグ</h1>
        </div>
        </header>
        <main>'''

        self.footer = f'''
        </main>
        <footer>
        </footer>
        </body>
        </html>'''

    def create_html_about_debug(self):
        """
        デバッグ用HTMLを生成する.
        """

        html = self.header

        debug_list = {
            'weather': dbaccess.Weather().select_all(),
            'train': dbaccess.Train().select_all(),
            'english': dbaccess.EnglishStudy().select_all()
        }
        for table, rows in debug_list.items():

            html += f'''
            <script>
            jQuery(function($){{
            $("#debug-table-{ table }").DataTable();
            }});
            </script>
            <section>
            <h2>{ table }</h2>
            <table id="debug-table-{ table }" class="table table-bordered">
            <thead>
            <tr>
            '''

            # テーブルカラム作成
            for column in rows[0].keys():

                html += f'''
                <th>{ column }</th>
                '''
            else:
                html += '</tr></thead>'

            # テーブルbody作成
            html += '''<tbody>'''
            for row in rows:

                html += '<tr>'
                for val in row.values():

                    html += f'''
                    <td>{ val }</td>
                    '''
                else:
                    html += '</tr>'
            else:
                html += '</tbody></table>'

        self.footer += html

        # HTMLファイル生成
        with open('../debug.html', 'wb') as file:
            file.write(html.encode('utf-8'))
            log.info('create_html_about_debug: Complete!')