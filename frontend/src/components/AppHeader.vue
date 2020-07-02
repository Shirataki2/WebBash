<template>
  <div>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="hidden-sm-and-up mr-n3"
      ></v-app-bar-nav-icon>
      <v-toolbar-title
        @click="$router.push('/').catch(() => {})"
        style="cursor: pointer"
      >
        <strong>Web Bash</strong>
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        class="hidden-xs-only mr-n1 ml-n1"
        text
        style="font-weight: 900"
        v-if="$store.state.isLogin"
        @click="$router.push('/timeline').catch(() => {})"
      >
        <v-icon>
          mdi-forum
        </v-icon>
        <span class="hidden-xs-only">
          TimeLine
        </span>
      </v-btn>
      <v-dialog v-model="tosDialog" scrollable max-width="1000px">
        <template v-slot:activator="{ on }">
          <v-btn text class="hidden-xs-only" v-on="on">
            <strong>利用規約</strong>
          </v-btn>
        </template>
        <v-card>
          <v-card-title>利用規約</v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pt-4">
            <TOS />
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn color="primary" text @click="tosDialog = false">Close</v-btn>
            <v-spacer />
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }" class="pr-2">
          <div v-if="$store.state.isLogin">
            <v-avatar size="38" v-bind="attrs" v-on="on">
              <img :src="$store.state.avatarUrl" />
            </v-avatar>
            <span
              ><b
                class="ml-2 mr-2 hidden-xs-only"
                style="position: relative; top: 2px"
                >{{ $store.state.username }}</b
              ></span
            >
          </div>
          <div v-else>
            <v-btn icon large class="hidden-xs-only" v-bind="attrs" v-on="on">
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
      <v-dialog v-model="historyDialog" max-width="700px" scrollable>
        <template v-slot:activator="{ on }">
          <v-btn icon v-if="$route.path === '/'" large v-on="on">
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
            <v-btn color="primary" text @click="historyDialog = false"
              >Close</v-btn
            >
            <v-spacer />
            <v-btn color="error" text @click="deleteHistory">Clear</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-btn
        v-if="$route.path === '/'"
        icon
        large
        target="_blank"
        :href="
          `https://twitter.com/intent/tweet?text=${encodeURIComponent(
            code
          )}&hashtags=${encodeURIComponent('シェル芸')}`
        "
      >
        <v-icon>mdi-twitter</v-icon>
      </v-btn>
      <v-dialog v-model="helpDialog" scrollable max-width="1000px">
        <template v-slot:activator="{ on }">
          <v-btn icon large class="hidden-xs-only" v-on="on">
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
            <v-btn color="primary" text @click="helpDialog = false"
              >Close</v-btn
            >
            <v-spacer />
          </v-card-actions>
        </v-card>
      </v-dialog>
      <ThemeSwitch class="hidden-xs-only" />
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" absolute app temporary>
      <v-list nav>
        <v-list-item-group style="background-color: transparent">
          <div v-if="$store.state.isLogin">
            <v-list-item
              @click="
                () => {
                  $router.push('/timeline').catch(() => {
                    $vuetify.goTo(0, {
                      duration: 1000,
                      easing: 'easeInOutCubic'
                    });
                  });
                }
              "
            >
              <v-list-item-icon>
                <v-icon class="sidebar">mdi-home</v-icon>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar"
                  >すべての投稿</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-badge content="開発中">
                  <v-icon class="sidebar">mdi-bell</v-icon>
                </v-badge>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar">通知</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-badge content="開発中">
                  <v-icon class="sidebar">mdi-account-heart</v-icon>
                </v-badge>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar"
                  >フォロー中の投稿</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-badge content="開発中">
                  <v-icon class="sidebar">mdi-account</v-icon>
                </v-badge>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar">ユーザー</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item @click="logout">
              <v-list-item-icon>
                <v-icon class="sidebar">mdi-logout-variant</v-icon>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar">Logout</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </div>
          <div v-else>
            <v-list-item @click="logInWithTwitter">
              <v-list-item-icon>
                <v-icon class="sidebar">mdi-login-variant</v-icon>
              </v-list-item-icon>
              <v-list-item-content class="hidden-sm-and-up">
                <v-list-item-title class="sidebar"
                  >Login with Twitter</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>
          </div>
          <v-list-item
            @click="
              () => {
                helpDialog = true;
                drawer = false;
              }
            "
          >
            <v-list-item-icon>
              <v-icon class="sidebar">mdi-help-circle</v-icon>
            </v-list-item-icon>
            <v-list-item-content class="hidden-sm-and-up">
              <v-list-item-title class="sidebar">Help</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="
              () => {
                tosDialog = true;
                drawer = false;
              }
            "
          >
            <v-list-item-icon>
              <v-icon class="sidebar">mdi-file-document-outline</v-icon>
            </v-list-item-icon>
            <v-list-item-content class="hidden-sm-and-up">
              <v-list-item-title class="sidebar">利用規約</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            class="mt-5"
            @click="
              () => {
                $router.push('/').catch(() => {});
              }
            "
          >
            <v-list-item-icon>
              <v-icon class="sidebar">mdi-console-line</v-icon>
            </v-list-item-icon>
            <v-list-item-content class="hidden-sm-and-up">
              <v-list-item-title class="sidebar"
                >シェル芸を作成!</v-list-item-title
              >
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <template v-slot:append>
        <div class="pa-2">
          <ThemeSwitch />
        </div>
      </template>
    </v-navigation-drawer>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import checkToken from "@/utils/check_token";
import About from "@/components/About.vue";
import TOS from "@/components/TOS.vue";
import ThemeSwitch from "@/components/ThemeSwitch.vue";
import Cookies from "js-cookie";

@Component({
  components: {
    About,
    ThemeSwitch,
    TOS
  }
})
class AppHeader extends Vue {
  drawer = false;
  historyDialog = false;
  helpDialog = false;
  tosDialog = false;

  async mounted() {
    const data = await checkToken(this);
    if (data) {
      this.login(data);
    } else {
      await this.logout();
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  login(data: any) {
    console.log("Login");
    this.$store.dispatch("setLogin", true);
    this.$store.dispatch("setUserId", data.id);
    this.$store.dispatch("setUsername", data.username);
    this.$store.dispatch("setAvatarUrl", data.avater_url);
  }

  async logout() {
    console.log("Logout");
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    Cookies.remove("access_token_expire");
    this.$axios.get("/api/oauth/logout");
    this.$store.dispatch("setLogin", false);
    this.$store.dispatch("setUserId", "");
    this.$store.dispatch("setUsername", "");
    this.$store.dispatch("setAvatarUrl", "");
    this.$store.dispatch("setMessage", {
      snackbarType: "error",
      message: "ログアウトしました"
    });
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
    this.$store.dispatch("setMessage", {
      snackbarType: "error",
      message: "履歴を削除しました"
    });
  }

  async logInWithTwitter() {
    const redirectUri =
      process.env.NODE_ENV === "development"
        ? "http://192.168.10.19:5919/api/oauth/login"
        : "/api/oauth/login";
    location.href = redirectUri;
  }
}
export default AppHeader;
</script>

<style scoped>
.sidebar {
  font-weight: 900;
  font-size: 1.1em !important;
}
</style>
