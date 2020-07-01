<template>
  <div>
    <v-main class="mt-n7 pb-7">
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
            <v-card
              style="background-color: transparent; margin; border-bottom: 1px solid #777;"
              class="grid-list-xs"
              elevation="0"
              v-for="(post, index) in posts"
              :key="post.id"
            >
              <div
                v-if="index == posts.length - 3"
                v-observe-visibility="visibilityChanged"
              />
              <v-card-title>
                <v-avatar size="42">
                  <img :src="post.owner.avater_url || ''" />
                </v-avatar>
                <span class="subtitle-1 font-weight-bold ml-2">{{ post.owner.username || '' }}
                  <span class="ml-2 mr-4 subtitle-2">&#x2027;</span>
                  <span class="subtitle-2 font-weight-light grey--text">{{ post.post_at ? parseDate(post.post_at) : '' }}</span>
                </span>
              </v-card-title>
              <v-card-text>
                <div
                  @click="$router.push(`/user/${post.owner.id || ''}/post/${post.id || ''}`).catch(()=>{});"
                  style="cursor: pointer"
                >
                  <p class="subtitle-1 font-weight-bold mt-n2 mb-n1">{{ post.title || '' }}</p>
                  <p class="mt-2 mb-1 ml-3 mr-3">{{ post.description || '' }}</p>
                  <v-divider />
                  <p
                    class="mt-2 mb-n3"
                    style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:1em"
                  >
                    {{ post.stdout ? previewResult(post.stdout) : ''}}
                  </p>
                </div>
                <ImageViewer
                  class="mt-n3 mb-n3"
                  v-if="post.generated_images"
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
import SideBar from "@/components/SideBar.vue";
import Cookie from "js-cookie";
import checkToken from "@/utils/check_token";
import parseDate from "@/utils/parseDate";
import axios from "axios";
import ImageViewer from "@/components/ImageViewer.vue";

Component.registerHooks(["beforeRouteEnter", "beforeRouteLeave"]);

@Component({
  name: "timeline",
  components: {
    ImageViewer,
    SideBar
  }
})
class TimeLine extends Vue {
  posts: any[] = [];
  interval: number | null = null;
  lastPostAt = "";
  // eslint-disable-next-line
  beforeRouteLeave(_to: any, _from: any, next: any) {
    if (this.interval) {
      clearInterval(this.interval);
    }
    next();
  }

  async beforeRouteEnter(_route: any, _from: any, next: any) {
    try {
      await checkToken(this);
      const accessToken = Cookie.get("access_token");
      const { data } = await axios.get("/api/posts/", {
        headers: {
          "access-token": accessToken
        }
      });
      next((vm: this) => {
        vm.posts = data;
        vm.lastPostAt = data[0].post_at;
        if (vm.interval) {
          clearInterval(vm.interval);
        }
        vm.interval = setInterval(async () => {
          if (vm.posts === []) return;
          await checkToken(vm);
          const accessToken = Cookie.get("access_token");
          const { data } = await axios.get("/api/posts/fetch", {
            headers: {
              "post-at": vm.lastPostAt,
              "access-token": accessToken
            }
          });
          if (data.length > 0) {
            vm.posts.unshift(...data);
            vm.lastPostAt = data[0].post_at;
          }
        }, 10000);
        setInterval(() => {
          const posts = vm.posts.slice();
          vm.posts = posts;
        }, 1000);
      });
    } finally {
      1;
    }
  }

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
      this.lastPostAt = data[0].post_at;
      if (this.interval) {
        clearInterval(this.interval);
      }
      this.interval = setInterval(async () => {
        if (this.posts === []) return;
        await checkToken(this);
        const accessToken = Cookie.get("access_token");
        const { data } = await axios.get("/api/posts/fetch", {
          headers: {
            "post-at": this.lastPostAt,
            "access-token": accessToken
          }
        });
        if (data.length > 0) {
          this.posts.unshift(...data);
          this.lastPostAt = data[0].post_at;
        }
      }, 10000);
      setInterval(() => {
        const posts = this.posts.slice();
        this.posts = posts;
      }, 1000);
    } finally {
      1;
    }
  }

  // eslint-disable-next-line
  async visibilityChanged(isVisible: boolean, _e: any) {
    if (isVisible) {
      await checkToken(this);
      const accessToken = Cookie.get("access_token");
      const { data } = await axios.get("/api/posts/history", {
        headers: {
          "post-at": this.posts[this.posts.length - 1].post_at,
          "access-token": accessToken
        }
      });
      this.posts.push(...data);
    }
  }

  parseDate(date: string) {
    return parseDate(date);
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
