<template>
  <v-app dark>
    <AppHeader
      :code="code"
      :history="history"
      @selected="(newcode) => {code = newcode}"
      @deleted="() => {history = []}"
    />
    <v-content>
      <v-container grid-list-sm>
        <v-row>
          <v-col
            cols="12"
            md="6"
          >
            <v-row>
              <v-col
                cols="12"
                class="order-xs-1 order-md-1"
              >
                <Editor v-model="code" />
                <span class="overline">{{ getLenLimit }}</span>
              </v-col>
              <v-col
                cols="12"
                class="order-xs-3 order-md-6"
              >
                <v-btn
                  block
                  color="primary"
                  dark
                  :loading="isload"
                  :disabled="disabled"
                  @click="submit"
                  @keydown.enter.ctrl.exact="submit"
                  @keydown.enter.meta.exact="submit"
                >送信</v-btn>
              </v-col>
              <v-col
                cols="12"
                class="order-xs-2 order-md-2"
              >
                <v-form
                  v-model="fileValid"
                  ref="fileForm"
                  lazy-validation
                >

                  <v-file-input
                    multiple
                    accept="image/*"
                    label="Media Input (4ファイルまで/各2MBまで)"
                    @change="onFileSelected"
                    :rules="[
                    files => !files || !files.some(file => file.size > 2097152) || 'Image size should be less than 2 MB!'
                  ]"
                  />
                </v-form>
              </v-col>
            </v-row>
          </v-col>
          <v-col
            cols="12"
            md="6"
            class="order-xs-3 order-md-2"
          >
            <v-row>
              <v-col cols="12">
                <v-card>
                  <v-card-subtitle style="font-family: monospace">[STDOUT]</v-card-subtitle>
                  <v-card-text style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:0.8em">
                    {{ stdout }}
                  </v-card-text>
                  <ImageViewer :images="images" />
                  <v-card-subtitle style="font-family: monospace">[STDERR]</v-card-subtitle>
                  <v-card-text style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:0.8em">
                    {{ stderr }}
                  </v-card-text>
                  <v-card-subtitle style="font-family: monospace">[EXITCODE]</v-card-subtitle>
                  <v-card-text style="font-family: monospace">{{ exitCode }}</v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
      <v-snackbar
        v-model="snackbar"
        :color="snackbarType"
        top
      >
        <strong>{{ message }}</strong>
        <v-btn
          dark
          text
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </v-snackbar>
    </v-content>
    <AppFooter />
  </v-app>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Editor from "@/components/Editor.vue";
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import ImageViewer from "@/components/ImageViewer.vue";
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "app",
  components: {
    Editor,
    AppHeader,
    AppFooter,
    ImageViewer
  }
})
class App extends Vue {
  code = "";
  stdout = "";
  stderr = "";
  exitCode = "";

  history: string[] = [];
  images: string[] = [];
  media: File[] = [];

  isload = false;
  fileValid = false;

  snackbar = false;
  snackbarType = "error";
  message = "";

  get disabled() {
    return this.code === "";
  }

  get getLenLimit() {
    const len = this.getLen(this.code);
    return `${len} 文字 (Twitter(270文字): ${Math.round((len / 270) * 10000) /
      100}% / 上限(4000文字): ${Math.round((len / 4000) * 10000) / 100}%)`;
  }

  onFileSelected(e: Array<File>) {
    this.media = e;
  }

  mounted() {
    const history = localStorage.getItem("code/history");
    if (history) {
      this.history = JSON.parse(history);
    }
    document.onkeydown = (e: KeyboardEvent) => {
      if (
        (e.ctrlKey && e.key === "Enter") ||
        (e.metaKey && e.key === "Enter")
      ) {
        if (!this.isload) this.submit();
      }
    };
  }

  resetResult() {
    this.stdout = "";
    this.stderr = "";
    this.exitCode = "";
    this.images = [];
  }

  async submit() {
    this.isload = true;
    this.resetResult();
    const formdata = new FormData();
    const form: any = this.$refs.fileForm;
    if (!form.validate()) {
      return this.onError("画像の最大サイズは2MBまでです");
    }
    if (this.getLen(this.code) > 4000) {
      return this.onError("最大文字数を超過しています");
    }
    try {
      if (this.media.length > 0) {
        if (this.media.length > 4) {
          return this.onError("画像は最大4枚まで送信可能です");
        }
        for (let i = 0; i < this.media.length; i++) {
          const file = this.media[i];
          formdata.append(`f${i}`, file);
        }
      }
    } catch (e) {
      return this.onError("入力画像の処理中にエラーが発生しました");
    }
    formdata.append("source", this.code);
    this.history.push(this.code);
    if (this.history.length > 100) {
      this.history = this.history.slice(1);
    }
    localStorage.setItem("code/history", JSON.stringify(this.history));
    try {
      const { data } = await this.$axios.post("/api/run", formdata, {
        headers: {
          "content-type": "multipart/form-data"
        }
      });
      this.stdout = data.stdout;
      this.stderr = data.stderr;
      this.exitCode = `${data.exit_code} (time: ${data.exec_sec}${
        data.exit_code === 124 ? " (timeout)" : ""
      })`;
      this.images = data.images;
    } catch (e) {
      const status: number = e.response.status;
      if (status === 503) {
        return this.onError(
          "503: アクセスが集中しています．後ほどお試しください．"
        );
      } else if (status === 500) {
        return this.onError(
          "500: サーバー内部でエラーが発生しています．開発者に連絡してください！"
        );
      } else {
        return this.onError("通信エラーです．");
      }
    }
    this.isload = false;
  }

  onError(message: string) {
    this.snackbar = true;
    this.snackbarType = "error";
    this.message = message;
    this.isload = false;
  }

  onSuccess(message: string) {
    this.snackbar = true;
    this.snackbarType = "success";
    this.message = message;
    this.isload = false;
  }

  getLen(str: string) {
    let result = 0;
    for (let i = 0; i < str.length; i++) {
      const chr = str.charCodeAt(i);
      if (
        (chr >= 0x00 && chr < 0x81) ||
        chr === 0xf8f0 ||
        (chr >= 0xff61 && chr < 0xffa0) ||
        (chr >= 0xf8f1 && chr < 0xf8f4)
      ) {
        result += 1;
      } else {
        result += 2;
      }
    }
    return result;
  }
}
export default App;
</script>
