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
            <transition-group name="slide" tag="p">
              <div v-for="(post, index) in posts" :key="post.id">
                <div
                  v-if="index == posts.length - 3"
                  v-observe-visibility="visibilityChanged"
                />
                <Post :post="post" :onDelete="deletePost" />
              </div>
            </transition-group>
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
import Confirm from "@/components/Confirm.vue";
import Post from "@/components/Post.vue";
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
    SideBar,
    Confirm,
    Post
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

  async deletePost(post: any) {
    await checkToken(this);
    const accessToken = Cookie.get("access_token");
    await this.$axios.delete(`/api/users/me/posts/${post.id}`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.posts = this.posts.filter(p => p.id !== post.id);
    this.$store.dispatch("setMessage", {
      snackbarType: "success",
      message: "正常に削除しました"
    });
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
.slide-enter-active {
  animation: slide-in 0.7s;
}
.slide-leave-active {
  animation: slide-in 0.7s reverse;
}
@keyframes slide-in {
  0% {
    transform: translateY(-100px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
