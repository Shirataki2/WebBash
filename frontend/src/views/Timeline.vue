<template>
  <div>
    <v-main class="mt-n3 pb-7">
      <v-container>
        <v-row>
          <v-col
            style="height: 100%"
            cols="2"
            sm="1"
            md="4"
            lg="3"
          >
            <v-list
              flat
              nav
              style="background-color: transparent;position: fixed"
            >
              <v-list-item-group style="background-color: transparent">
                <v-list-item>
                  <v-list-item-icon>
                    <v-badge content="β版">
                      <v-icon class="sidebar">mdi-home</v-icon>
                    </v-badge>
                  </v-list-item-icon>
                  <v-list-item-content class="hidden-sm-and-down">
                    <v-list-item-title class="sidebar">すべての投稿</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-badge content="開発中">
                      <v-icon class="sidebar">mdi-bell</v-icon>
                    </v-badge>
                  </v-list-item-icon>
                  <v-list-item-content class="hidden-sm-and-down">
                    <v-list-item-title class="sidebar">通知</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-badge content="開発中">
                      <v-icon class="sidebar">mdi-account-heart</v-icon>
                    </v-badge>
                  </v-list-item-icon>
                  <v-list-item-content class="hidden-sm-and-down">
                    <v-list-item-title class="sidebar">フォロー中の投稿</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-badge content="開発中">
                      <v-icon class="sidebar">mdi-account</v-icon>
                    </v-badge>
                  </v-list-item-icon>
                  <v-list-item-content class="hidden-sm-and-down">
                    <v-list-item-title class="sidebar">ユーザー</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-col>
          <v-col
            cols="10"
            sm="11"
            md="8"
            lg="9"
            style="height: 100%; border-left: 1px solid #777; border-right: 1px solid #777"
          >
            <v-card
              style="background-color: transparent; margin; border-bottom: 1px solid #777;"
              class="grid-list-xs"
              elevation="0"
              v-for="post in posts"
              :key="post.id"
            >
              <v-card-title>
                <v-avatar size="42">
                  <img :src="post.owner.avater_url" />
                </v-avatar>
                <span class="subtitle-1 font-weight-bold ml-2">{{ post.owner.username }}
                  <span class="ml-2 mr-4 subtitle-2">&#x2027;</span>
                  <span class="subtitle-2 font-weight-light grey--text">{{ parseDate(post.post_at) }}</span>
                </span>
              </v-card-title>
              <v-card-text>
                <p class="subtitle-1 font-weight-bold mt-n2 mb-n1">{{ post.title }}</p>
                <p class="mt-2 mb-1 ml-3 mr-3">{{ post.description }}</p>
                <v-divider />
                <p
                  class="mt-2 mb-n3"
                  style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:1em"
                >
                  {{ previewResult(post.stdout) }}
                </p>
                <ImageViewer
                  class="mt-n3 mb-n3"
                  :images="post.generated_images.map((image) => image.url)"
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
import Cookie from "js-cookie";
import checkToken from "@/utils/check_token";
import ImageViewer from "@/components/ImageViewer.vue";

@Component({
  name: "timeline",
  components: {
    ImageViewer
  }
})
class TimeLine extends Vue {
  posts: any[] = [];

  async mounted() {
    try {
      await checkToken(this);
      const accessToken = Cookie.get("access_token");
      const { data } = await this.$axios.get("/api/posts/", {
        headers: {
          "access-token": accessToken
        }
      });
      this.posts = data;
    } finally {
      1;
    }
  }

  parseDate(date: string) {
    const postAt = new Date(date);
    const offset = new Date().getTimezoneOffset();
    const elapsed =
      new Date(Date.now()).getTime() - postAt.getTime() + offset * 60000;
    if (elapsed < 60 * 1000) {
      return `${Math.floor(elapsed / 1000)} 秒前`;
    }
    if (elapsed < 60 * 60 * 1000) {
      return `${Math.floor(elapsed / (60 * 1000))} 分前`;
    }
    if (elapsed < 24 * 60 * 60 * 1000) {
      return `${Math.floor(elapsed / (60 * 60 * 1000))} 時間前`;
    }
    const localdate = new Date(postAt.getTime() + offset * 60000);
    let d = "";
    if (localdate.getFullYear() !== new Date(Date.now()).getFullYear())
      d += `${localdate.getFullYear()}年 `;
    d += `${localdate.getMonth() + 1}月${localdate.getDate()}日`;
    return d;
  }

  previewResult(s: string) {
    const numNewline = s.match(/\n/)?.length || 0;
    const numChar = s.length;
    let t = s;
    if (numNewline > 20) {
      t =
        t
          .split(/\n/)
          .slice(0, 20)
          .join("\n") + "...";
    }
    if (numChar > 300) {
      t = t.slice(0, 300) + "...";
    }
    return t;
  }
}
export default TimeLine;
</script>

<style scoped>
.sidebar {
  font-weight: 900;
  font-size: 1.3em;
}
</style>