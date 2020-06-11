# WebBash

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![codecov](https://codecov.io/gh/Shirataki2/WebBash/branch/feature%2F%2324-add-tests/graph/badge.svg)](https://codecov.io/gh/Shirataki2/WebBash) ![](https://img.shields.io/badge/API-v1.1.0-blue)

![](https://github.com/Shirataki2/WebBash/workflows/Test%20on%20Merge/badge.svg) ![](https://github.com/Shirataki2/WebBash/workflows/Deploy%20To%20Server/badge.svg)

![](https://blog.chomama.jp/wp-content/uploads/2020/06/webbashicon-2.png)

Web上でシェル芸の練習ができたら嬉しいね．というモチベーションで開発した二番煎じなウェブアプリ．

ロゴはキングウンコをリスペクトしています．

```shell
＿人人人人人人人＿
＞　わしじゃよ　＜
￣Y^Y^Y^Y^Y^Y^Y^￣
　　　　　　👑
　　　　（💩💩💩）
　　　（💩👁💩👁💩）
　　（💩💩💩👃💩💩💩）
　（💩💩💩💩👄💩💩💩💩）
```

## 使用方法

### 1. 基本

1. [https://bash.chomama.jp](https://bash.chomama.jp)にアクセス
2. PCならば画面左側，スマホなら画面上側のテキストボックスにシェルスクリプトを書き込む
3. 「送信」ボタンを押す
4. 実行が完了すれば結果が表示されます．

### 2. シェル芸で作った画像を表示する (575)

1. `/images`ディレクトリの下に`jp(e)g`,`png`,`gif`の拡張子のファイルが作成された場合それらを最大4枚まで，ブラウザに表示することができます．
2. 作成した画像はサーバに保存されます．
2. 作成した画像をクリックすると拡大表示されます．

### 3. ローカルの画像をサーバに投げつける (575)

1. Media Filesには画像を最大4枚まで添付することができます．
    - 5枚以上選択はできますが，投稿時にエラーを吐きます．
2. 投稿した画像は辞書順に`0`,`1`,`2`,`3`と改名されます．
3. 画像を使って煮るなり焼くなりしてください．
4. 投稿した画像はサーバに保存されません．

### 4. 履歴と共有

- 最大100件，コードがローカルに保存されます．右上の時計マークをクリックすることでダイアログが表示されます．
- 右上の鳥をクリックすると，書いたコードを`#シェル芸`タグ付きでTwitterに投稿できます．[**シェル芸Bot**](https://twitter.com/minyoruminyon)と**相互フォロー**であった場合，呟けばシェル芸Botが反応してくれます．

1.から4.の内容はウェブアプリページの右上の❔ボタンを押しても見ることができます．

### 5. APIを直に叩く

このサイトの本体は裏で動いているAPIサーバです．なので`https://bash.chomama.jp/api/run`に`POST`をするだけでも，レスポンスが帰ってきます．

詳しくは[APIドキュメンテーションのページ](https://bash.chomama.jp/api/docs)をご覧ください．英語が苦手なので意味は汲み取ってください...申し訳ありません．

単純な例

```shell
> curl -X POST https://bash.chomama.jp/api/run -d 'source=echo $(matsuya) $(matsuya)|ke2daira'

{"stdout":"ウレミアムシャンピニオンソースハンバーグセット プシメシ\n","stderr":"","exit_code":"0","exec_sec":"0.601 sec","images":[]}
```

## 特徴

- 割と早い
    - `ps`などの軽微なスクリプトならば1秒足らずでレスポンスがきます．
- 見た目がなんかGCPとか最近よく見るやつみたい
    - すべてvuetifyのおかげです．
- APIを叩いてるだけ
    - cURLでもなんでも使ってください．

## 制約

当然，シェルスクリプトを好き勝手いじれすぎたら困るので以下の制約があります．

**シェルスクリプト自体の制限**

- 実行時間は20秒まで
- メモリ/スワップメモリ/共有メモリは256MBまで
- 実行可能なプロセス数は128まで
- 生成可能なファイルのサイズは5MBまで
- ネットワークは使用不可

**`/api/run`の制限**

- 同時に10個以上シェル芸Botコンテナが立っている場合は503を返します
- 同一IDから短時間に集中してアクセスがあった場合には一定時間アクセスを拒否します．(429を返します)
    - 10分間に120以上のリクエストがあった場合，30分アクセスを拒否します．
    - 1分間に15以上のリクエストがあった場合，90分アクセスを拒否します．
    - 10秒間に10以上のリクエストがあった場合，24時間アクセスを拒否します．
    - 1秒間に3以上のリクエストがあった場合，無期限でアクセスを拒否します．


## 開発環境

### Docker

アプリケーションはすべてDocker上で管理しています．アプリケーションの都合上，Dockerを走らせてシェル芸コンテナを動かしているので，Dockerコンテナ内でDockerコンテナを作成する荒技をとらないといけません．

本アプリではホストのDockerデーモンソケットファイルをdocker-compose.yml内でマウント(Volume接続)して，ホストのDockerとやりとりしてシェル芸コンテナを作成しています．(いわゆるDocker outside of Docker(DooD))

本アプリでは以下のコンテナが稼働しています．

各セルはentrypointです．

|コンテナ名|開発環境|テスト環境|本番環境|
|:-|:-|:-|:-|
|frontend|`yarn serve`|`yarn install --production=false && yarn build`|`yarn install --production=false && yarn build`|
|api|`sh entrypoint.dev.sh`|`pytest -v --cov=app --cov-report xml`|`sh entrypoint.sh`|
|proxy|(default)|(default)|(default)|
|mongo|(default)|(default)|(default)|

#### Frontend

Vue.jsを用いて，フロントエンド側を作成しています．UI等はVuetifyに依存している部分が多くあり，各種ボタンやダイアログなどの表示はすべてこのVuetifyに任せっきりで，さほど自力でjsやcssを書いてはいません．

`yarn serve`をすると，Vueのコンパイルが開始します．デバッグ時にはこのコマンドを使うことで，Vue CLIが開発モードで起動し，ホットリロードなど各種開発時に便利な機能が利用できます．ホストのポート`4040`番とリンクしており，`<Host IP>:4040`にアクセスすることでページが表示されます．

`yarn build`は静的ファイルを作成するためのコマンドです．このビルドにより各種HTML/JS/CSSが生成されます．

本環境では，静的ファイルの生成先`frontend/dist`をproxyにマウントしているので本番環境を動かす際には

```shell
> docker-comppose -f docker-compose.prod.yml up frontend
> docker-comppose -f docker-compose.prod.yml up -d proxy
```

の順番に起動する必要があります．

#### API

このアプリの本体です．Pythonで書かれています．フレームワークはFastAPIを使用しています．リクエストをスキーマベースで処理するのでPydanticによりリクエストのバリデーションを自動的に行ってくれます．不正なリクエストには`422`エラーが返されます．

現状，画像を提供するAPIとシェル芸コンテナを走らせるAPIしかありませんが拡張する予定です．

開発環境では以下のスクリプトが実行されます

```shell
service nginx start
uvicorn app.main_fastapi:api --log-level debug --port 6000 --reload
```

ASGI(WSGIの後継)の一つであるuvicornでFastAPIアプリとWebサーバをつないでいます．このコンテナの80番ポートにアクセスされた際，6000番ポートにリバースプロキシされるようにしています．ですので，ネットワーク上ではDocker内の`http://api`とアクセスすることでこのAPIにアクセスすることができます．

本番環境も同じようなスクリプトですが，セーブ時に勝手にリロードされないように，`--reload`オプションは省いています．

#### Proxy

`/`にアクセスされた際には，Frontendでビルドした静的ファイルを返し，`/api/`にアクセスされた際にはAPIサーバにリバースプロキシしています．ホストのポートは，開発環境では`5919`番ポート，本番環境では`9999`番ポートとそれぞれのサーバの80番ポートとリンクしています．本番環境では，ホストのnginxからproxyサーバの`9999`番ポートにリバースプロキシされるようになっています．

#### Mongo

アクセスログを記録するデータベースです．X-Forwarded-ForからクライアントIPを取得しています．

### CI/CD

CI/CDツールとしてGitHub Actionsを利用しています．

現状4つのWorkflowが実装されています．

|名前|トリガー|行う内容|
|:-|:-|:-|
|Create a release pull request|`develop`ブランチに`[release]`を含むコミットメッセージで`push`したとき|`develop`->`master`へのPRを作成する|
|PR Labeler|特定のブランチ名でPRを作成したとき|自動的にlabelにブランチ名を追加する|
|Test on Merge| `develop`もしくは`master`へのプルリクが作成されたときやコミットしたとき(`No CI`ラベルを付与したPRは除く)|テスト環境を作成しテストスクリプトを走らせる．カバレッジ情報をcodecovに送る．成功した場合のみmergeできる．|
|Deploy to Server|`master`に`push`したとき|開発環境用スクリプトを走らせ自動的に本番環境を更新する|

### 開発ポリシー

1. master,developには直接コミットはしない
2. 機能追加やバグ修正などがあったらissueを立てる
    - Feature: 機能追加
    - Chore: 軽微な修正
    - Bug: 不具合の訂正
3. developからブランチを作成する，上の3つのissueの種類に合わせてブランチ名を命名する．
    - `feature/#13-bug-fix`のように`[種類]/[#issueのID]-[slug]`という名前にする
        - `feature/#xx-slug`: 機能追加
        - `chore/#xx-slug`: 軽微な修正
        - `fix/#xx-slug`: 不具合の訂正
4. 修正や追加が終わったらdevelopブランチにPRを出す．
    - No CIというラベルがついていなければ，テストスクリプトを走らせる．
    - テストが通って問題がなさそうであればMergeする．
5. developへMergeされた際
    - テストスクリプトは常に走ります．
    - `[deploy]`がコミットメッセージに含まれている場合はmasterブランチにPRが出されます．
6. masterへMergeされた際
    - ホストへデプロイされます．