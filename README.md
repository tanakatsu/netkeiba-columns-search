## netkeiba-columns-search

This is a simple tool to fetch columns in [netkeiba](https://news.netkeiba.com/?pid=column_top&rf=navi).

### Get started

1. Clone this repository
    ```
    $ git clone https://github.com/tanakatsu/netkeiba-columns-search.git
    ```
1. Create virtual environment and activate it
    ```
    $ python -m venv venv
    $ . venv/bin/activate
    ```
1. Install packages
    ```
    $ pip install -r requirements.txt
    ```
1. Install browsers
    ```
    $ sudo /path/to/playwright install-deps
    $ playwright install
    ```
1. Run script
    ```
    $ python main.py --output_dir OUTPUT_DIR --keyword KEYWORD
    ```
    You can choose any keyword that you want to search.

### Example of result

When you use default keyword "Aiエスケープ", you'll get the following output.
```
$ tree output
output/
├── 49160.txt
├── 49207.txt
├── 49255.txt
...

├── 55946.txt
├── 55994.txt
└── 56029.txt

1 directory, 185 files
```

```
$ cat output/49160.txt

道中の位置取りからして完璧だったクロノジェネシス(C)netkeiba.com



netkeibaにある膨大な競走成績を人工知能によって機械学習するAiエスケープを開発したAIマスター・Mと、レースデータの分析を
専門とする競馬評論家・伊吹雅也による今週末のメインレース展望。コンピュータの“脳”が導き出した注目馬の期待度を、人間の“
脳”がさまざまな角度からチェックする。
(文・構成＝伊吹雅也)


荒れる要素しかない一戦でAIが選んだのは!?

...


M なるほど。ジュンブルースカイは前走から中12週での参戦となります。

伊吹 とはいえ、この馬自身が休養明けを苦にするタイプかどうかはまだわかりませんからね。もともと私もそれなりに重いシルシ
を打つつもりでしたし、Aiエスケープの評価を加味するならば、連軸を任せる価値がある一頭と言えるでしょう。



AIとデータの究極予想の結論は？
```
