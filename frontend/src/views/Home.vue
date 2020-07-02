<template>
  <div class="mb-8">
    <v-main>
      <v-container grid-list-sm>
        <v-row>
          <v-col cols="12" md="6">
            <v-row>
              <v-col cols="12" class="order-xs-1 order-md-1">
                <Editor />
                <span class="overline">{{ getLenLimit }}</span>
              </v-col>
              <v-col cols="12" class="order-xs-3 order-md-6">
                <v-btn
                  block
                  color="primary"
                  dark
                  :loading="isload"
                  :disabled="disabled"
                  @click="submit"
                  @keydown.enter.ctrl.exact="submit"
                  @keydown.enter.meta.exact="submit"
                  >送信</v-btn
                >
              </v-col>
              <v-col cols="12" class="order-xs-2 order-md-2">
                <v-form v-model="fileValid" ref="fileForm" lazy-validation>
                  <v-file-input
                    multiple
                    accept="image/*"
                    label="Media Input (4ファイルまで/各2MBまで)"
                    @change="onFileSelected"
                    :rules="[
                      files =>
                        !files ||
                        !files.some(file => file.size > 2097152) ||
                        'Image size should be less than 2 MB!'
                    ]"
                  />
                </v-form>
                <ImageViewer
                  v-if="previewImages !== []"
                  :images="previewImages"
                  disable-download
                />
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="6" class="order-xs-3 order-md-2">
            <v-row>
              <v-col cols="12">
                <v-card>
                  <v-card-subtitle style="font-family: monospace"
                    >[STDOUT]</v-card-subtitle
                  >
                  <v-card-text
                    style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:0.8em"
                  >
                    {{ stdout }}
                  </v-card-text>
                  <ImageViewer :images="images" />
                  <v-card-subtitle style="font-family: monospace"
                    >[STDERR]</v-card-subtitle
                  >
                  <v-card-text
                    style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:0.8em"
                  >
                    {{ stderr }}
                  </v-card-text>
                  <v-card-subtitle style="font-family: monospace"
                    >[EXITCODE]</v-card-subtitle
                  >
                  <v-card-text style="font-family: monospace">{{
                    exitCode
                  }}</v-card-text>
                  <SaveForm
                    :visible="exitCode !== '' && $store.state.isLogin"
                    :images="images"
                    :media="mediaPath"
                    :stdout="stdout"
                    :stderr="stderr"
                    :exitcode="exitCode"
                  />
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
      <v-snackbar
        v-model="$store.state.snackbar"
        :color="$store.state.snackbarType"
        top
      >
        <strong>{{ $store.state.message }}</strong>
        <template v-slot:action="{ attrs }">
          <v-btn
            dark
            text
            v-bind="attrs"
            @click="$store.commit('SET_SNACKBAR', false)"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-main>
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Editor from "@/components/Editor.vue";
import SaveForm from "@/components/SaveForm.vue";
import ImageViewer from "@/components/ImageViewer.vue";
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "home",
  components: {
    Editor,
    ImageViewer,
    SaveForm
  }
})
class Home extends Vue {
  // code = "";
  stdout = "";
  stderr = "";
  exitCode = "";

  // history: string[] = [];
  images: string[] = [];
  media: File[] = [];
  previewImages: string[] = [];
  mediaPath: string[] = [];

  isload = false;
  fileValid = false;

  get disabled() {
    return this.$store.state.code === "";
  }

  get getLenLimit() {
    const len = this.getLen(this.$store.state.code);
    return `${len} 文字 (Twitter(270文字): ${Math.round((len / 270) * 10000) /
      100}% | 上限(4000文字): ${Math.round((len / 4000) * 10000) / 100}%)`;
  }

  onFileSelected(e: Array<File>) {
    this.previewImages = [];
    this.media = e;
    e.forEach(img => {
      this.previewImages.push(URL.createObjectURL(img));
    });
  }

  mounted() {
    const history = localStorage.getItem("code/history");
    if (history) {
      this.$store.dispatch("setHistory", JSON.parse(history));
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

  beforeRouteEnter(_route: any, _redirect: any, next: any) {
    document.onkeydown = (e: KeyboardEvent) => {
      if (
        (e.ctrlKey && e.key === "Enter") ||
        (e.metaKey && e.key === "Enter")
      ) {
        if (!this.isload) this.submit();
      }
    };
    next((vm: this) => {
      const history = localStorage.getItem("code/history");
      if (history) vm.$store.dispatch("setHistory", JSON.parse(history));
    });
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
    if (this.getLen(this.$store.state.code) > 4000) {
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
    formdata.append("source", this.$store.state.code);
    this.$store.dispatch("appendHistory", this.$store.state.code);
    if (this.$store.state.history.length > 100) {
      this.$store.dispatch("deleteFirstHistory");
    }
    localStorage.setItem(
      "code/history",
      JSON.stringify(this.$store.state.history)
    );
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
      this.mediaPath = data.media;
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
    this.$store.dispatch("setMessage", { message, snackbarType: "error" });
    this.isload = false;
  }

  onSuccess(message: string) {
    this.$store.dispatch("setMessage", { message, snackbarType: "success" });
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
export default Home;
</script>
