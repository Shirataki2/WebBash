<template>
  <v-app-bar
    app
    color="primary"
    dark
  >
    <v-toolbar-title>
      <strong>Web Bash</strong>
    </v-toolbar-title>
    <v-spacer />
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
          <div v-if="history.length > 0">
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
import { Vue, Component, Prop } from "vue-property-decorator";
import About from "@/components/About.vue";
import ThemeSwitch from "@/components/ThemeSwitch.vue";

@Component({
  components: {
    About,
    ThemeSwitch
  }
})
class AppFooter extends Vue {
  historyDialog = false;
  helpDialog = false;
  @Prop({ type: Array, default: [] })
  history!: string[];
  @Prop({ type: String, default: "" })
  code!: string;

  get reversedHistory() {
    return this.history.slice().reverse();
  }

  onHistoryClick(code: string) {
    this.$emit("selected", code);
    this.historyDialog = false;
  }

  deleteHistory() {
    this.historyDialog = false;
    localStorage.removeItem("code/history");
    this.$emit("deleted");
  }
}
export default AppFooter;
</script>
