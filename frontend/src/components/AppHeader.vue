<template>
  <v-app-bar
    app
    color="primary"
    dark
  >
    <v-toolbar-title @click="go('/')">
      <strong>Web Bash</strong>
    </v-toolbar-title>
    <v-spacer />
    <v-btn
      text
      large
      class="mr-n1 ml-n1"
      style="font-weight: 900"
      v-if="$store.state.isLogin"
      href="/timeline"
    >
      <v-icon>
        mdi-forum
      </v-icon>
      <span class="hidden-xs-only">
        TimeLine
      </span>
    </v-btn>
    <v-menu offset-y>
      <template
        v-slot:activator="{on, attrs}"
        class="pr-2"
      >
        <div v-if="$store.state.isLogin">
          <v-avatar
            size="38"
            v-bind="attrs"
            v-on="on"
          >
            <img :src="$store.state.avatarUrl">
          </v-avatar>
          <span><b
              class="ml-2 mr-2 hidden-xs-only"
              style="position: relative; top: 2px"
            >{{$store.state.username}}</b></span>
        </div>
        <div v-else>
          <v-btn
            icon
            v-bind="attrs"
            v-on="on"
          >
            <v-icon>
              mdi-account
            </v-icon>
          </v-btn>
        </div>
      </template>
      <v-list class="body-1">
        <template v-if="$store.state.isLogin">
          <v-list-item @click="logout">
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </template>
        <template v-else>
          <v-list-item @click="logInWithTwitter">
            <v-list-item-title>Log In with Twitter</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-menu>
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
          <div v-if="reversedHistory.length > 0">
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
      :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(code)}&hashtags=${encodeURIComponent('シェル芸')}`"
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
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import Cookies from "js-cookie";
import About from "@/components/About.vue";
import ThemeSwitch from "@/components/ThemeSwitch.vue";

@Component({
  components: {
    About,
    ThemeSwitch
  }
})
class AppHeader extends Vue {
  historyDialog = false;
  helpDialog = false;

  async mounted() {
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    const accessTokenExpire = Cookies.get("access_token_expire");
    // ログイン情報を問い合わせる
    if (accessToken && refreshToken && accessTokenExpire) {
      console.log("Valid Access Token");
      // 基本情報の取得
      try {
        const { data } = await this.$axios.get("/api/users/me", {
          headers: {
            "access-token": accessToken
          }
        });
        this.login(data);
      } catch {
        console.log("Expired Access Token");
        // Refresh Tokenでトークンの更新を図る
        const params = new FormData();
        params.append("access_token", accessToken);
        params.append("refresh_token", refreshToken);
        try {
          const accessToken = Cookies.get("access_token");
          const [{ data }, ignore] = await Promise.all([
            this.$axios.get("/api/users/me", {
              headers: {
                "access-token": accessToken
              }
            }),
            this.$axios.post("/api/token/refresh", params, {
              headers: {
                "content-type": "multipart/form-data"
              }
            })
          ]);

          console.log("Update Access Token");
          console.log(Date.now());
          this.login(data);
        } catch (e) {
          console.log("Invalid Access Token");
          await this.logout();
          console.error(e);
        }
      }
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  login(data: any) {
    console.log("Login");
    this.$store.dispatch("setLogin", true);
    this.$store.dispatch("setUsername", data.username);
    this.$store.dispatch("setAvatarUrl", data.avater_url);
  }

  async logout() {
    console.log("Logout");
    this.$axios.get("/api/oauth/logout");
    this.$store.dispatch("setLogin", false);
    this.$store.dispatch("setUsername", "");
    this.$store.dispatch("setAvatarUrl", "");
  }

  get reversedHistory() {
    const history = this.$store.state.history;
    return history.slice().reverse();
  }

  get isLogin() {
    return this.$store.state.isLogin;
  }

  get code() {
    return this.$store.state.code;
  }

  onHistoryClick(code: string) {
    this.$store.dispatch("setCode", code);
    this.historyDialog = false;
  }

  deleteHistory() {
    this.historyDialog = false;
    localStorage.removeItem("code/history");
    this.$store.dispatch("deleteAllHistory");
  }

  async logInWithTwitter() {
    const redirectUri =
      process.env.NODE_ENV === "development"
        ? "http://192.168.10.19:5919/api/oauth/login"
        : "/api/oauth/login";
    location.href = redirectUri;
  }

  go(loc: string) {
    window.location.href = loc;
  }
}
export default AppHeader;
</script>
