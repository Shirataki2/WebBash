<template>
  <v-footer fixed>
    <v-col class="text-center ma-n2" style="font-size: 0.8em" padless cols="12">
      Version 2.2.1 | &copy; {{ new Date().getFullYear() }} —
      <strong>FF </strong
      ><a target="_blank" href="https://twitter.com/fujifog">@fujifog</a>
      <br />
      <a target="_blank" href="/api/docs">API Documentation</a>
    </v-col>
  </v-footer>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component({
  name: "AppFooter"
})
class AppFooter extends Vue {}
export default AppFooter;
</script>
