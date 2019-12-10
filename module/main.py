"""
実行モジュール.
"""
import daily_html


if __name__ == "__main__":
    """
    天気予報、運行情報、英単語HTML生成.
    デバッグHTML作成
    """

    ins = daily_html.CreateHtml(['weather','train','english'])
    del ins

    debug = daily_html.Debug()
    debug.create_html_about_debug()
