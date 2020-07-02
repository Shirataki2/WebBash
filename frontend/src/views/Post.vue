<template>
  <div>
    <v-main class="mt-n3 pb-7">
      <v-container>
        <v-row>
          <SideBar />
          <v-col
            cols="12"
            sm="10"
            md="8"
            lg="8"
            xl="9"
            style="height: 100%; border-left: 1px solid #777; border-right: 1px solid #777"
          >
            <span class="title" style="cursor: pointer" @click="$router.back()">
              <v-icon class="mr-5 mb-1">
                mdi-arrow-left
              </v-icon>
              <span class="font-weight-bold">戻る</span>
            </span>
            <v-divider class="mt-3" />
            <v-card
              style="background-color: transparent; margin; border-bottom: 1px solid #777;"
              class="grid-list-xs"
              elevation="0"
              v-if="post"
            >
              <v-card-title>
                <v-avatar size="42">
                  <img :src="post.owner.avater_url" />
                </v-avatar>
                <span class="title font-weight-bold ml-2"
                  >{{ post.owner.username }}
                  <span class="ml-2 mr-4 subtitle-1">&#x2027;</span>
                  <span class="subtitle-1 font-weight-light grey--text">{{
                    parseDate(post.post_at)
                  }}</span>
                </span>
              </v-card-title>
              <v-card-text>
                <p class="title font-weight-bold">{{ post.title }}</p>
                <p class="ml-3 mr-3">{{ post.description }}</p>
                <CodeViewer :code="post.main" class="mb-3" />
                <v-row class="mb-2">
                  <v-col cols="6">
                    <v-btn
                      block
                      color="success"
                      class="font-weight-bold"
                      large
                      :outlined="!upvoted"
                      @click="upvote"
                    >
                      <v-badge content="開発中">
                        <v-icon>
                          mdi-thumb-up
                        </v-icon>
                      </v-badge>
                    </v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn
                      block
                      color="error"
                      class="font-weight-bold"
                      large
                      :outlined="!downvoted"
                      @click="downvote"
                    >
                      <v-badge content="開発中">
                        <v-icon>
                          mdi-thumb-down
                        </v-icon>
                      </v-badge>
                    </v-btn>
                  </v-col>
                  <v-col cols="12">
                    <v-btn
                      block
                      color="primary"
                      class="font-weight-bold mt-n2"
                      large
                      outlined
                      @click="copyCode"
                    >
                      <v-icon>
                        mdi-download
                      </v-icon>
                      COPY
                    </v-btn>
                  </v-col>
                </v-row>
                <v-divider />
                <p
                  class="subtitle-1 font-weight-bold"
                  style="text-align: center"
                >
                  [標準出力]
                </p>
                <p
                  class="mt-2"
                  style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:1em"
                >
                  {{ post.stdout }}
                </p>
                <v-divider />
                <p
                  class="subtitle-1 font-weight-bold"
                  style="text-align: center"
                >
                  [標準エラー出力]
                </p>
                <p
                  class="mt-2"
                  style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:1em"
                >
                  {{ post.stderr }}
                </p>
                <v-divider />
                <p
                  class="subtitle-1 font-weight-bold"
                  style="text-align: center"
                >
                  [画像入力]
                </p>
                <ImageViewer
                  class="mt-n3 mb-n3"
                  :images="post.posted_images.map(image => image.url)"
                />
                <v-divider />
                <p
                  class="subtitle-1 font-weight-bold"
                  style="text-align: center"
                >
                  [画像出力]
                </p>
                <ImageViewer
                  class="mt-n3 mb-n3"
                  :images="post.generated_images.map(image => image.url)"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { Vue, Component } from "vue-property-decorator";
import { Route } from "vue-router";
import SideBar from "@/components/SideBar.vue";
import CodeViewer from "@/components/CodeViewer.vue";
import ImageViewer from "@/components/ImageViewer.vue";
import Cookie from "js-cookie";
import checkToken from "@/utils/check_token";
import parseDate from "@/utils/parseDate";
import axios from "axios";

Component.registerHooks(["beforeRouteEnter"]);

@Component({
  name: "Post",
  components: {
    SideBar,
    ImageViewer,
    CodeViewer
  }
})
class Post extends Vue {
  post: any = null;
  upvoted = false;
  downvoted = false;
  async beforeRouteEnter(route: Route, redirect: Route, next: any) {
    try {
      await checkToken(this);
      const accessToken = Cookie.get("access_token");
      const userId = route.params.user_id;
      const postId = route.params.post_id;
      const { data } = await axios.get(`/api/users/${userId}/posts/${postId}`, {
        headers: {
          "access-token": accessToken
        }
      });
      next((vm: this) => {
        vm.post = data;
      });
    } catch (e) {
      console.error(e);
    }
  }

  async mounted() {
    try {
      await checkToken(this);
      const accessToken = Cookie.get("access_token");
      const userId = this.$route.params.user_id;
      const postId = this.$route.params.post_id;
      const { data } = await axios.get(`/api/users/${userId}/posts/${postId}`, {
        headers: {
          "access-token": accessToken
        }
      });
      this.post = data;
    } catch (e) {
      console.error(e);
    }
  }

  parseDate(date: string) {
    return parseDate(date);
  }

  copyCode() {
    this.$store.dispatch("setCode", this.post.main);
    this.$router.push("/");
  }

  async upvote() {
    1;
  }

  async downvote() {
    1;
  }

  async ubOn2Off() {
    2;
  }
  async ubOff2On() {
    2;
  }
}
export default Post;
</script>
