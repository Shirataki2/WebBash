<template>
  <v-app dark>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <v-toolbar-title>
        <strong>Web Bash</strong>
      </v-toolbar-title>
      <v-spacer />
      <v-dialog
        v-model="searchDialog"
        scrollable
        permanent
        max-width="800px"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            icon
            v-on="on"
            @click="search"
          >
            <v-icon>
              mdi-magnify
            </v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-title>
            <span class="headline">Search (Beta)</span>
            <v-spacer />
            <v-btn
              icon
              @click="searchDialog = false"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-form
              v-model="searchValid"
              ref="searchForm"
            >
              <v-container>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      label="User Name"
                      v-model="usernameQuery"
                      class="mt-n2 mb-n2"
                      dense
                      outlined
                      @input="search"
                      :counter="256"
                      :rules="[
                        v => v.length <= 256 || 'User Name must be less than 256 characters',
                      ]"
                    ></v-text-field>
                    <v-text-field
                      label="Description"
                      v-model="descriptionQuery"
                      class="mt-n2 mb-n2"
                      dense
                      outlined
                      @input="search"
                      :counter="280"
                      :rules="[
                        v => v.length <= 280 || 'Description must be less than 280 characters',
                      ]"
                    ></v-text-field>
                    <v-text-field
                      label="Source Code"
                      v-model="codeQuery"
                      class="mt-n2 mb-n2"
                      dense
                      outlined
                      @input="search"
                      :counter="4000"
                      :rules="[
                        v => v.length <= 4000 || 'Source Code must be less than 4000 characters',
                      ]"
                    ></v-text-field>
                    <v-select
                      v-model="selectedSort"
                      dense
                      outlined
                      item-text="label"
                      item-value="value"
                      :items="sorts"
                      @change="search"
                      label="Sort By"
                      return-object
                    />
                  </v-col>
                </v-row>
              </v-container>
            </v-form>
            <v-divider />
            <v-row class="mt-4">
              <v-col
                cols="12"
                v-if="searchResult.length > 0"
              >
                <v-card
                  v-for="item in searchResult"
                  :key="item.id"
                  @click="onPostClick(item)"
                  outlined
                >
                  <v-card-text
                    style="font-size:1.1em;cursor: pointer;white-space: pre-wrap;word-wrap:break-word;"
                    class="pb-10"
                  >{{ item.description }}</v-card-text>
                  <v-divider />
                  <v-card-actions style="color: #999">
                    by {{ item.author }}
                    <v-spacer />
                    <v-icon style="color: #999">mdi-eye</v-icon>
                    <span class="ml-2 mr-4">{{ item.views }}</span>
                    <v-icon style="color: #999">mdi-thumb-up</v-icon>
                    <span class="ml-2 mr-2">{{ item.votes }}</span>
                  </v-card-actions>
                </v-card>
              </v-col>
              <v-col
                cols="12"
                v-else
                class="text-center"
              >
                <strong>No Result!</strong>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-dialog>
      <v-dialog
        v-model="searchDetailDialog"
        scrollable
        permanent
        max-width="800px"
        height="99%"
      >
        <v-card>
          <v-card-text>
            <p
              class="ma-4"
              style="font-size: 1.3em;white-space: pre-wrap;word-wrap:break-word;"
            >{{ selectedPost ? selectedPost.description : '' }}</p>
            <p
              class="ma-4"
              style="text-align: right"
            >by {{ selectedPost ? selectedPost.author : '' }}</p>
            <Preview
              v-model="selectedPost.main"
              :lineNumbers="false"
            />
          </v-card-text>
          <v-card-actions>
            <v-icon style="color: #999">mdi-eye</v-icon>
            <span class="ml-2 mr-4">{{ selectedPost.views }}</span>

            <v-icon style="color: #999">mdi-thumb-up</v-icon>
            <span class="ml-2 mr-2">{{ selectedPost.votes + offset}}</span>
            <v-spacer />
            <v-btn
              text
              color="warning"
              @click="() => searchDetailDialog = false"
            >Close</v-btn>
            <v-btn
              text
              color="success"
              @click="onUpvoteClick(selectedPost)"
            >Upvote!</v-btn>
            <v-btn
              text
              color="primary"
              @click="onCopyClick(selectedPost)"
            >Copy</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-dialog
        v-model="historyDialog"
        scrollable
        max-width="700px"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            icon
            v-on="on"
          >
            <v-icon>
              mdi-history
            </v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-title>History (最新100件)</v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pt-4">
            <div v-if="history.length > 0">
              <v-textarea
                readonly
                outlined
                filled
                :rows="2"
                dense
                class="pt-n3 mb-n6 pl-9 mr-9"
                v-for="(pastCode, i) in reversedHistory"
                :key="i"
                :value="pastCode"
                @click="onHistoryClick(pastCode)"
              />
            </div>
            <div v-else>
              <h4 style="text-align: center">No history</h4>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn
              color="primary"
              text
              @click="historyDialog = false"
            >Close</v-btn>
            <v-spacer />
            <v-btn
              color="error"
              text
              @click="deleteHistory"
            >Clear</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-btn
        icon
        target="_blank"
        :href="`https://twitter.com/intent/tweet?text=${encodeURI(code)}&hashtags=${encodeURI('シェル芸')}`"
      >
        <v-icon>mdi-twitter</v-icon>
      </v-btn>
      <v-dialog
        v-model="helpDialog"
        scrollable
        max-width="1000px"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            icon
            v-on="on"
          >
            <v-icon>
              mdi-help-circle
            </v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-title>About</v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pt-4">
            <About />
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn
              color="primary"
              text
              @click="helpDialog = false"
            >Close</v-btn>
            <v-spacer />
          </v-card-actions>
        </v-card>
      </v-dialog>
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
                                max-height="100%"
                                style="cursor: pointer"
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
                                    />
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
                  <v-card-text v-if="exitCode !== ''">
                    <v-dialog
                      v-model="saveDialog"
                      persistent
                      max-width="600px"
                    >
                      <template v-slot:activator="{ on }">
                        <v-btn
                          color="success"
                          block
                          v-on="on"
                        >Save</v-btn>
                      </template>
                      <v-card>
                        <v-card-title>
                          <span class="headline">Save</span>
                        </v-card-title>
                        <v-card-text>
                          <v-form
                            v-model="valid"
                            ref="form"
                          >
                            <v-container>
                              <v-row>
                                <v-col cols="12">
                                  <v-text-field
                                    label="User Name *"
                                    v-model="username"
                                    outlined
                                    :counter="16"
                                    :rules="[
                                      v => !!v || 'User Name is required',
                                      v => v.length <= 16 || 'User Name must be less than 16 characters',
                                    ]"
                                    required
                                  ></v-text-field>
                                </v-col>
                                <v-col cols="12">
                                  <v-textarea
                                    label="Description *"
                                    v-model="description"
                                    outlined
                                    :counter="280"
                                    :rules="[
                                      v => !!v || 'Description is required',
                                      v => v.length <= 280 || 'Description must be less than 280 characters',
                                    ]"
                                    required
                                  ></v-textarea>
                                </v-col>
                              </v-row>
                            </v-container>
                          </v-form>
                        </v-card-text>
                        <v-card-actions>
                          <v-btn
                            color="primary"
                            text
                            @click="onCodeSubmit"
                          >Save</v-btn>
                          <v-spacer></v-spacer>
                          <v-btn
                            color="error"
                            text
                            @click="onCodeCencel"
                          >Cancel</v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-dialog>
                  </v-card-text>
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
    <v-footer>
      <v-col
        class="text-center ma-n2"
        style="font-size: 0.8em"
        padless
        cols="12"
      >
        Version 1.0.0 |
        &copy; {{ new Date().getFullYear() }} — <strong>FF</strong> (Twitter: <a
          target="_blank"
          href="https://twitter.com/fujifog"
        >@FF</a>) | <a
          target="_blank"
          href="/api/docs"
        >API Documentation</a>
      </v-col>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import Editor from "./components/Editor.vue";
import Preview from "./components/Preview.vue";
import About from "./components/About.vue";
import ThemeSwitch from "./components/ThemeSwitch.vue";
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "app",
  components: {
    Editor,
    Preview,
    ThemeSwitch,
    About
  }
})
class App extends Vue {
  code = "";
  src = "";
  stdout = "";
  stderr = "";
  exitCode = "";
  message = "";
  username = "";
  description = "";
  usernameQuery = "";
  descriptionQuery = "";
  codeQuery = "";
  offset = 0;
  num = 0;
  images: string[] = [];
  media: File[] = [];
  isload = false;
  dialog = false;
  valid = false;
  searchValid = false;
  fileValid = false;
  historyDialog = false;
  saveDialog = false;
  searchDialog = false;
  searchDetailDialog = false;
  helpDialog = false;
  snackbar = false;
  snackbarType = "error";
  history: string[] = [];
  searchResult: any[] = [];
  selectedPost: any = { main: "" };
  sorts = [
    { label: "関連度順", value: { key: "_score", order: "desc" } },
    { label: "最新順", value: { key: "post_at", order: "desc" } },
    { label: "古い順", value: { key: "post_at", order: "asc" } },
    { label: "閲覧数順", value: { key: "views", order: "desc" } },
    { label: "Upvote数順", value: { key: "votes", order: "desc" } }
  ];
  selectedSort = { label: "最新順", value: { key: "post_at", order: "desc" } };

  get disabled() {
    return this.code === "";
  }

  get getLenLimit() {
    const len = this.getLen(this.code);
    return `${len} 文字 (Twitter(270文字): ${Math.round((len / 270) * 10000) /
      100}% / 上限(4000文字): ${Math.round((len / 4000) * 10000) / 100}%)`;
  }

  get reversedHistory() {
    return this.history.slice().reverse();
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

  async submit() {
    this.isload = true;
    this.stdout = "";
    this.stderr = "";
    this.exitCode = "";
    this.images = [];
    const formdata = new FormData();
    const form: any = this.$refs.fileForm;
    if (!form.validate()) {
      return this.onError("画像の最大サイズは2MBまでです");
    }
    if (this.getLen(this.code) > 4000) {
      return this.onError("最大文字数を超過しています");
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

  onHistoryClick(code: string) {
    this.code = code;
    this.historyDialog = false;
  }

  deleteHistory() {
    this.historyDialog = false;
    localStorage.removeItem("code/history");
    this.history = [];
  }

  async onCodeSubmit() {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const form: any = this.$refs.form;
    if (form.validate()) {
      try {
        await this.$axios.post("/api/posts", {
          author: this.username,
          description: this.description,
          main: this.code
        });
        this.saveDialog = false;
        form.resetValidation();
        this.username = "";
        this.description = "";
        this.onSuccess("正常に保存しました");
      } catch (e) {
        return this.onError("通信エラーです．");
      }
    }
  }

  async onCodeCencel() {
    this.saveDialog = false;
    const form: any = this.$refs.form;
    form.resetValidation();
    this.username = "";
    this.description = "";
  }

  async search() {
    try {
      const params: any = {};
      if (this.usernameQuery !== "") params["author"] = this.usernameQuery;
      if (this.descriptionQuery !== "")
        params["description"] = this.descriptionQuery;
      if (this.codeQuery !== "") params["main"] = this.codeQuery;
      params["key"] = this.selectedSort.value.key;
      params["order"] = this.selectedSort.value.order;
      const resp = await this.$axios.get("/api/search", {
        params
      });
      const data: Array<any> = resp.data.content;
      this.num = resp.data.num;
      if (!data) {
        this.searchResult = [];
        return;
      }
      this.searchResult = [];
      data.forEach((item: any) => {
        const data = item;
        this.searchResult.push({
          ...data
        });
      });
    } catch (e) {
      console.error(e);
      return this.onError("通信エラーです．");
    }
  }

  async onPostClick(post: any) {
    this.selectedPost = post;
    this.searchDetailDialog = true;
    await this.$axios.put("/api/posts", {
      pid: post._id,
      views: post.views + 1
    });
    this.selectedPost.views += 1;
  }

  async onUpvoteClick(post: any) {
    await this.$axios.put("/api/posts", {
      pid: post._id,
      votes: post.votes + 1
    });
    this.selectedPost.votes += 1;
  }

  onCopyClick(post: any) {
    this.searchDialog = false;
    this.searchDetailDialog = false;
    this.code = post.main;
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
