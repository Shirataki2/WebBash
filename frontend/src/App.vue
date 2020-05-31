<template>
  <v-app dark>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <v-toolbar-title>
        Web Bash
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        icon
        target="_blank"
        :href="`http://twitter.com/share?text=${encodeURI(code)}&hashtags=${encodeURI('シェル芸')}`"
      >
        <v-icon>mdi-twitter</v-icon>
      </v-btn>
      <ThemeSwitch />
    </v-app-bar>
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
                >送信</v-btn>
              </v-col>
              <v-col
                cols="12"
                class="order-xs-2 order-md-2"
              >
                <v-file-input
                  multiple
                  accept="image/*"
                  label="Media input (4ファイルまで)"
                  v-on:change="onFileSelected"
                />
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
                  <v-container fluid>
                    <v-row>
                      <v-col
                        v-for="(image, i) in images"
                        :key="i"
                        class="d-flex child-flex"
                        cols="6"
                        sm="3"
                        md="6"
                        xl="3"
                      >
                        <v-card
                          flat
                          tile
                          class="d-flex"
                        >
                          <v-dialog
                            v-model="dialog"
                            max-width="1000"
                          >
                            <template v-slot:activator="{ on }">
                              <v-img
                                :src="image"
                                v-on="on"
                                @click="() => src = image"
                                aspect-ratio="1.6"
                                class="grey lighten-2"
                              >
                                <template v-slot:placeholder>
                                  <v-row
                                    class="fill-height ma-0"
                                    align="center"
                                    justify="center"
                                  >
                                    <v-progress-circular
                                      indeterminate
                                      color="grey lighten-5"
                                    ></v-progress-circular>
                                  </v-row>
                                </template>
                              </v-img>
                            </template>
                            <v-img :src="src">
                            </v-img>
                            <v-btn
                              block
                              :href="image"
                              target="_blank"
                              large
                            >
                              <v-icon>mdi-download</v-icon>
                              Download
                            </v-btn>
                          </v-dialog>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-container>
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
        color="error"
        top
      >
        {{ message }}
        <v-btn
          dark
          text
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </v-snackbar>
    </v-content>
  </v-app>
</template>

<script lang="ts">
import Editor from "./components/Editor.vue";
import ThemeSwitch from "./components/ThemeSwitch.vue";
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "app",
  components: {
    Editor,
    ThemeSwitch
  }
})
class App extends Vue {
  code = "";
  src = "";
  stdout = "";
  stderr = "";
  exitCode = "";
  message = "";
  images: string[] = [];
  media: File[] = [];
  isload = false;
  dialog = false;
  snackbar = false;

  get disabled() {
    return this.code === "";
  }

  get getLenLimit() {
    const len = this.getLen(this.code);
    return `${len} 文字 (Twitter(280文字): ${Math.round((len / 280) * 10000) /
      100}% / 上限(4000文字): ${Math.round((len / 4000) * 10000) / 100}%)`;
  }

  onFileSelected(e: Array<File>) {
    this.media = e;
  }

  async submit() {
    this.isload = true;
    this.stdout = "";
    this.stderr = "";
    this.exitCode = "";
    this.images = [];
    const formdata = new FormData();
    if (this.code.length > 4000) {
      this.snackbar = true;
      this.message = "最大文字数を超過しています";
      this.isload = false;
    }
    try {
      if (this.media) {
        for (let i = 0; i < Math.min(4, this.media.length); i++) {
          // eslint-disable-next-line
          const file: Blob = this.media[i];
          formdata.append(`file_${i}`, file);
        }
      }
    } catch (e) {
      this.snackbar = true;
      this.message = "入力画像の処理中にエラーが発生しました";
      this.isload = false;
    }
    formdata.append("source", this.code);
    try {
      const { data } = await this.$axios.post("/run", formdata, {
        headers: {
          "content-type": "multipart/form-data"
        }
      });
      this.stdout = data.stdout;
      this.stderr = data.stderr;
      this.exitCode = `${data.exit_code} (time: ${data.sec}${
        data.exit_code === 124 ? " (timeout)" : ""
      })`;
      this.images = data.images;
    } catch (e) {
      this.snackbar = true;
      this.message = "通信エラーです";
      this.isload = false;
    }

    // for debug
    // this.stdout =
    //   "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    // this.stderr =
    //   "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    // this.exitCode = "0";
    // this.images = [
    //   "https://picsum.photos/500/300?image=13",
    //   "https://picsum.photos/500/300?image=42"
    // ];

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
