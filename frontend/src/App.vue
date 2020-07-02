<template>
  <v-app dark>
    <AppHeader />
    <router-view />
    <v-snackbar
      v-model="$store.state.snackbar"
      :color="$store.state.snackbarType"
      top
    >
      <strong>{{ $store.state.message }}</strong>
      <template v-slot:action="{ attrs }">
        <v-btn
          dark
          text
          v-bind="attrs"
          @click="$store.commit('SET_SNACKBAR', false)"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
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
