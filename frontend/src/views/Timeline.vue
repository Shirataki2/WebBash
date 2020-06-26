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
            style="height: 100%; border-left: 1px solid #777"
          >
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
            <h1>Main</h1>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "timeline"
})
class TimeLine extends Vue {}
export default TimeLine;
</script>

<style scoped>
.sidebar {
  font-weight: 900;
  font-size: 1.3em;
}
</style>