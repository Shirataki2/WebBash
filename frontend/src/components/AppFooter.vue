<template>
  <v-footer>
    <v-col
      class="text-center ma-n2"
      style="font-size: 0.8em"
      padless
      cols="12"
    >
      Version 2.0.0 |
      &copy; {{ new Date().getFullYear() }} — <strong>FF</strong> (Twitter: <a
        target="_blank"
        href="https://twitter.com/fujifog"
      >@fujifog</a>) | <a
        target="_blank"
        href="/api/docs"
      >API Documentation</a>
    </v-col>
  </v-footer>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component
class ThemeSwitch extends Vue {}
export default ThemeSwitch;
</script>
