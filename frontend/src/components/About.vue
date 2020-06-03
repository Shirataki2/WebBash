<template>
  <div>
    <h2 class="mb-4">これはなに</h2>
    <p>Webブラウザ上でシェルスクリプトを実行できるサイトです．</p>
    <p>#シェル芸 で使われているDockerリポジトリを使用しています．(<a href="https://hub.docker.com/r/theoldmoon0602/shellgeibot">theoldmoon0602/shellgeibot</a>)</p>
    <h2 class="mt-9 mb-4">実行時の制限</h2>
    <ol>
      <li>実行時間は20秒まで</li>
      <li>メモリ/スワップメモリ/共有メモリは256MBまで</li>
      <li>実行可能なプロセス数は128まで</li>
      <li>生成可能なファイルのサイズは5MBまで</li>
      <li>ネットワークは使用不可</li>
      <li>同時に10個以上シェル芸Botコンテナが立っている場合は503を返します</li>
    </ol>
    <h2 class="mt-9 mb-4">使い方</h2>
    <div class="mt-6 mb-5">
      <h3 class="mt-1 mb-2">基本</h3>
      <ol>
        <li>左側にコードを入力します．</li>
        <li>送信を押します(Ctrl+EnterでもOK)</li>
        <li>裏でスクリプトが実行されます</li>
        <li>実行結果が表示されます</li>
        <li>SheBangは使用可能です</li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">画像受信</h3>
      <ol>
        <li><code>/images</code>配下にpng/jpeg/jpg/gif拡張子の画像を置きます</li>
        <li>画像が最大4枚まで表示されます</li>
        <li>作成した画像はクリックで拡大できます</li>
        <li>作成した画像はサーバーに保存されます</li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">画像送信</h3>
      <ol>
        <li>Media Inputに画像ファイルを添付します(4枚まで,各々2MBまで)．</li>
        <li>画像は<code>/media</code>配下に置かれます．</li>
        <li>画像の名前は順に0,1,2,3と改名されます．拡張子も省かれます．</li>
        <li>シェル芸Botと同じ仕様で煮るなり焼くなり好きにしてください．</li>
        <li>送信した画像はサーバーに保存されません</li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">コードの共有</h3>
      <ol>
        <li>実行後に表示される SAVE をクリックして実行コードをこのサイトにアクセスした人全員とできます．</li>
        <li>名前，及び説明を入れてください(検索の際に使用されます．)．</li>
        <li><strong>※添付画像は保存されません</strong></li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">検索</h3>
      <ol>
        <li>
          <v-icon>mdi-magnify</v-icon>をクリックすると検索が行えます．
        </li>
        <li>ユーザ名は完全一致検索，コードと説明は全文検索です．</li>
        <li>Elasticsearchのプラグインであるkuromojiでコードの説明を形態素解析しています．</li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">履歴</h3>
      <ol>
        <li>
          <v-icon>mdi-history</v-icon>をクリックすると履歴が表示されます．
        </li>
        <li>localStorageに保存しているのでそれを消すことで消去されます</li>
      </ol>
    </div>
    <div class="mt-6 mb-5">
      <h3 class="mb-2">Twitterに共有</h3>
      <ol>
        <li>
          <v-icon>mdi-twitter</v-icon>をクリックするとTwitterのツイート投稿画面に移動します．
        </li>
        <li>シェル芸Botにフォローバックされている場合そのままツイートすることでシェル芸Botが実行してくれます．</li>
      </ol>
    </div>
    <h2 class="mt-9 mb-4">リポジトリ</h2>
    <p><a href="https://github.com/Shirataki2/WebBash">https://github.com/Shirataki2/WebBash</a></p>
    <p>ビルド方法などは後ほど追記します．</p>
    <p>環境が整ってれば<code>docker-compose -f docker-compose.prod.yml up -d</code>で起動できま<s>す</s> るはずです</p>
    <h2 class="mt-9 mb-4">使用フレームワーク等</h2>
    <ul>
      <li>Docker</li>
      <li>Docker Compose</li>
      <li>Vue.js</li>
      <li>Responder</li>
      <li>Uvicorn</li>
      <li>Nginx</li>
      <li>Elastic Stack</li>
    </ul>
    <h2 class="mt-9 mb-4">参考にさせていただいたもの</h2>
    <ul>
      <li><a
          target="_blank"
          href="https://twitter.com/minyoruminyon"
        >シェル芸Bot</a></li>
      <li><a
          target="_blank"
          href="https://github.com/kekeho/SGWeb"
        >SGWeb</a></li>
      <li><a
          target="_blank"
          href="https://github.com/jiro4989/websh"
        >websh</a></li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component
class Editor extends Vue {}
export default Editor;
</script>
