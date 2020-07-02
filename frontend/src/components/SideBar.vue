<template>
  <v-col
    style="height: 100%"
    class="hidden-xs-only"
    cols="1"
    sm="1"
    md="4"
    lg="4"
    xl="3"
  >
    <v-list flat nav style="background-color: transparent;position: fixed">
      <v-list-item-group style="background-color: transparent">
        <v-list-item
          @click="
            () => {
              $router.push('/timeline').catch(() => {
                $vuetify.goTo(0, { duration: 1000, easing: 'easeInOutCubic' });
              });
            }
          "
        >
          <v-list-item-icon>
            <v-icon class="sidebar">mdi-home</v-icon>
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
          <v-list-item-content class="hidden-sm-and-down">
            <v-list-item-title class="sidebar">ユーザー</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <div class="mt-4 mb-3" />
        <v-list-item
          @click="
            () => {
              $router.push('/').catch(() => {});
            }
          "
        >
          <v-list-item-icon>
            <v-icon class="sidebar">mdi-console-line</v-icon>
          </v-list-item-icon>
          <v-list-item-content class="hidden-sm-and-down">
            <v-list-item-title class="sidebar"
              >シェル芸を作成!</v-list-item-title
            >
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-col>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
/* eslint-disable @typescript-eslint/camelcase */

@Component({
  name: "SideBar"
})
class SideBar extends Vue {}
export default SideBar;
</script>

<style scoped>
.sidebar {
  font-weight: 900;
  font-size: 1.3em !important;
}
</style>
