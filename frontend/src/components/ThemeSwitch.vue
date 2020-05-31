<template>
  <div>
    <v-btn
      icon
      v-if="$vuetify.theme.dark"
      @click="$vuetify.theme.dark=false"
    >
      <v-icon>mdi-weather-night</v-icon>
    </v-btn>
    <v-btn
      icon
      v-if="!$vuetify.theme.dark"
      @click="$vuetify.theme.dark=true"
    >
      <v-icon>mdi-weather-sunny</v-icon>
    </v-btn>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component
class ThemeSwitch extends Vue {}
export default ThemeSwitch;
</script>
