<template>
  <v-app dark>
    <AppHeader />
    <router-view />
    <AppFooter />
  </v-app>
</template>

<script lang="ts">
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "app",
  components: {
    AppFooter,
    AppHeader
  }
})
class App extends Vue {}
export default App;
</script>