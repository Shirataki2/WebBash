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
            style="height: 100%"
            v-if="userdata"
          >
            <v-row>
              <v-col cols="4" sm="3">
                <v-avatar size="100%">
                  <v-img :src="userdata.avater_url.replace('_normal', '')" />
                </v-avatar>
              </v-col>
              <v-col cols="8" sm="9">
                <div class="hidden-xs-only">
                  <div class="mt-6" />
                </div>
                <h1>{{ userdata.username }}</h1>
                <Copy :message="userdata.id">
                  <span style="font-size: 0.6em; color: #777"
                    >ID: {{ userdata.id }}</span
                  >
                </Copy>
              </v-col>
            </v-row>
            <v-col cols="12" grid-list-xs>
              <v-tabs
                v-model="tab"
                grow
                centered
                background-color="transparent"
              >
                <v-tabs-slider></v-tabs-slider>

                <v-tab href="#tab-1">
                  最近の投稿
                </v-tab>

                <v-tab href="#tab-0" v-if="$store.state.userId === userdata.id">
                  ユーザ情報編集
                </v-tab>
              </v-tabs>

              <v-tabs-items v-model="tab" style="background-color: transparent">
                <v-tab-item value="tab-1">
                  <transition-group name="slide" tag="p">
                    <v-card
                      flat
                      color="transparent"
                      v-for="post in posts"
                      :key="post.id"
                    >
                      <Post :post="post" :onDelete="deletePost" />
                    </v-card>
                  </transition-group>
                </v-tab-item>
                <v-tab-item value="tab-0">
                  <UpdateUserInfo :username="userdata.username" />
                </v-tab-item>
              </v-tabs-items>
            </v-col>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { Vue, Component } from "vue-property-decorator";
import Cookies from "js-cookie";
import SideBar from "@/components/SideBar.vue";
import checkToken from "@/utils/check_token";
import Copy from "@/components/Copy.vue";
import Post from "@/components/Post.vue";
import UpdateUserInfo from "@/components/UpdateUserInfo.vue";

Component.registerHooks(["beforeRouteEnter", "beforeRouteUpdate"]);

@Component({
  name: "User",
  components: {
    SideBar,
    Copy,
    Post,
    UpdateUserInfo
  }
})
class User extends Vue {
  user = "me";
  found = true;
  userdata: any = null;
  posts: any = null;
  tab = 0;

  async mounted() {
    this.user = this.$route.params.user_id;
    await checkToken(this);
    const accessToken = Cookies.get("access_token");
    const { data } = await this.$axios.get(`/api/users/${this.user}`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.userdata = data;
    const posts = await this.$axios.get(`/api/users/${this.user}/posts`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.posts = posts.data;
  }

  async beforeRouteEnter(_route: any, _from: any, next: any) {
    await checkToken(this);
    const accessToken = Cookies.get("access_token");
    next(async (vm: this) => {
      vm.user = vm.$route.params.user_id;
      const { data } = await vm.$axios.get(`/api/users/${vm.user}`, {
        headers: {
          "access-token": accessToken
        }
      });
      vm.userdata = data;
      const posts = await vm.$axios.get(`/api/users/${vm.user}/posts`, {
        headers: {
          "access-token": accessToken
        }
      });
      vm.posts = posts.data;
    });
  }

  async beforeRouteUpdate(_route: any, _from: any, next: any) {
    await checkToken(this);
    const accessToken = Cookies.get("access_token");
    const user = _route.params.user_id;
    const { data } = await this.$axios.get(`/api/users/${user}`, {
      headers: {
        "access-token": accessToken
      }
    });
    const posts = await this.$axios.get(`/api/users/${user}/posts`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.posts = posts.data;
    this.userdata = data;
    next();
  }

  async deletePost(post: any) {
    await checkToken(this);
    const accessToken = Cookies.get("access_token");
    await this.$axios.delete(`/api/users/me/posts/${post.id}`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.posts = this.posts.filter((p: any) => p.id !== post.id);
    this.$store.dispatch("setMessage", {
      snackbarType: "success",
      message: "正常に削除しました"
    });
  }
}
export default User;
</script>

<style scoped>
.v-tabs > .v-tabs-bar {
  background-color: transparent;
}
</style>
