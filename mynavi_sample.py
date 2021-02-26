import os
import time

import pandas as pd
# from selenium import webdriver
import datetime
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg is True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 \
            (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(ChromeDriverManager().install(), options=options)


def timestamp():
    return str(datetime.datetime.now().strftime('%Y/%m/%d/ %H:%M:%S'))

# main処理


def main():
    log_path = ('log.csv')
    with open(log_path, 'a', encoding="utf_8_sig") as f:
        print(timestamp()+'  処理開始', file=f)
        # 検索するキーワードの入力 2-4
        search_keyword = str(input('検索するキーワードを指定してください。'))
        print(timestamp()+'  キーワード設定：'+search_keyword, file=f)
        # 検索するページ数を指定 2-3オプション
        search_range = int(input('抽出するページ数を指定してください。'))
        print(timestamp()+'  抽出ページ数：'+str(search_range), file=f)
        # アウトプット先のファイルを指定 2-5
        path = ('output.csv')
        print(timestamp()+'  アウトプット先ファイル：'+path, file=f)

        # driverを起動
        print(timestamp()+'  ドライバー起動', file=f)
        if os.name == 'nt':
            # Windows
            driver = set_driver("chromedriver.exe", False)
        elif os.name == 'posix':
            # Mac
            driver = set_driver("chromedriver", False)
        # Webサイトを開く
        print(timestamp()+'  WEBサイトを開く', file=f)
        driver.get("https://tenshoku.mynavi.jp/")
        time.sleep(5)

        try:
            # ポップアップを閉じる
            print(timestamp()+'  ポップアップを閉じる', file=f)
            driver.execute_script(
                'document.querySelector(".karte-close").click()')
            time.sleep(5)
            # ポップアップを閉じる
            driver.execute_script(
                'document.querySelector(".karte-close").click()')
        except Exception:
            pass

        # 検索窓に入力
        print(timestamp()+'  検索キーワード入力', file=f)
        driver.find_element_by_class_name(
            "topSearch__text").send_keys(search_keyword)
        # 検索ボタンクリック
        print(timestamp()+'  検索実行', file=f)
        driver.find_element_by_class_name("topSearch__button").click()

        # ページ終了まで繰り返し取得
        exp_name_list = []
        exp_copy_list = []
        exp_job_list = []

        df = pd.DataFrame()
        # print(df)

        def scraping():

            time.sleep(5)
            # 検索結果の現在のページに表示されているすべての会社名・案件名・仕事内容を取得
            name_list = driver.find_elements_by_class_name(
                "cassetteRecruit__name")
            print(timestamp()+'  会社名{0}件'.format(name_list), file=f)

            copy_list = driver.find_elements_by_class_name(
                "cassetteRecruit__copy")
            print(timestamp()+'  案件名{0}件'.format(copy_list), file=f)

            job_list = driver.find_elements_by_xpath(
                "//table[@class='tableCondition']/tbody/tr[1]/td[1]")
            print(timestamp()+'  仕事内容{0}件'.format(job_list), file=f)

            # 会社名を取得して出力用リストに格納 1ページ分繰り返し
            for i, name in enumerate(name_list):
                exp_name_list.append(name.text)
                print(timestamp()+'  会社名：{0}件目抽出'.format(i), file=f)
                # print(name.text)

            # 案件名取得して出力用リストに格納 1ページ分繰り返し 2-1
            for i, copy in enumerate(copy_list):
                exp_copy_list.append(copy.text)
                print(timestamp()+'  案件名：{0}件目抽出'.format(i), file=f)
                # print(copy.text)

            # 仕事名取得して出力用リストに格納 1ページ分繰り返し 2-2
            for i, job in enumerate(job_list):
                exp_job_list.append(job.text)
                print(timestamp()+'  仕事内容：{0}件目抽出'.format(i), file=f)
                # print(job.text)

        # 2ページ目以降の処理。inputされたページ数分だけ取得する 2-3
        i = 1
        # エラー時の処理をスキップ 2-6
        try:
            print(timestamp()+'  抽出処理開始', file=f)
            while search_range >= i:
                print(timestamp()+'  {0}ページ目検索開始'.format(i), file=f)
                scraping()
                time.sleep(5)
                print('{0}ページ目完了'.format(i), file=f)
                time.sleep(5)
                i += 1
                nextPageElement = driver.find_element_by_xpath(
                    "//li[@class='pager__next']/ \
                        a[@class='iconFont--arrowLeft']")
                nextPageElement.click()

            print(timestamp()+'  抽出処理終了', file=f)
            df['name'] = exp_name_list
            df['copy'] = exp_copy_list
            df['job'] = exp_job_list
            df.to_csv(path)
            print(timestamp()+'  ファイル出力完了', file=f)
        except Exception:
            pass


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
