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

                <v-tab href="#tab-2">
                  自己紹介
                </v-tab>

                <v-tab href="#tab-3">
                  高評価した投稿
                </v-tab>
              </v-tabs>

              <v-tabs-items v-model="tab" style="background-color: transparent">
                <v-tab-item v-for="i in 3" :key="i" :value="'tab-' + i">
                  <v-card flat color="transparent">
                    <v-card-text>あ</v-card-text>
                  </v-card>
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

@Component({
  name: "User",
  components: {
    SideBar,
    Copy
  }
})
class User extends Vue {
  user = "me";
  found = true;
  userdata: any = null;
  tab = 0;

  async mounted() {
    this.user = (this.$route.params && this.$route.params.user_id) || "me";
    await checkToken(this);
    const accessToken = Cookies.get("access_token");
    const { data } = await this.$axios.get(`/api/users/${this.user}`, {
      headers: {
        "access-token": accessToken
      }
    });
    this.userdata = data;
  }
}
export default User;
</script>

<style scoped>
.v-tabs > .v-tabs-bar {
  background-color: transparent;
}
</style>
