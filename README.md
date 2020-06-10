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

`yarn build`は静的ファイルを作成するためのコマンドです．このビルドにより各種HTML/JS/CSSが生成されるのでこれをどこかにデプロイすれば，アクセスできるようになります．

本環境では，`frontend/dist`をproxyにマウントしているので本番環境を動かす際には

```shell
> docker-comppose -f docker-compose.prod.yml up frontend
> docker-comppose -f docker-compose.prod.yml up -d proxy
```

の順番に起動する必要があります．

#### API

#### Proxy

#### Mongo

### CI/CD

CI/CDツールとしてGitHub Actionsを利用しています．

現状4つのWorkflowが実装されています．

|名前|トリガー|行う内容|
|:-|:-|:-|
|Create a release pull request|`develop`ブランチに`[release]`を含むコミットメッセージで`push`したとき|`develop`->`master`へのPRを作成する|
|PR Labeler|特定のブランチ名でPRを作成したとき|自動的にlabelにブランチ名を追加する|
|Test on Merge| `develop`もしくは`master`へのプルリクが作成されたときやコミットしたとき(`No CI`ラベルを付与したPRは除く)|テスト環境を作成しテストスクリプトを走らせる．カバレッジ情報をcodecovに送る．成功した場合のみmergeできる．|
|Deploy to Server|`master`に`push`したとき|開発環境用スクリプトを走らせ自動的に本番環境を更新する|