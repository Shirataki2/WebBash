<template>
  <div
    v-clipboard:copy="message"
    v-clipboard:success="onCopy"
    style="cursor: pointer;"
  >
    <v-tooltip v-model="tip" :bottom="isBottom" :top="!isBottom">
      <template v-slot:activator="{ on, attrs }">
        <slot v-bind="attrs" v-on="on" />
      </template>
      Copied!
    </v-tooltip>
  </div>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";

@Component({
  name: "Copy"
})
class Copy extends Vue {
  @Prop({ type: String, default: "" })
  message!: string;
  @Prop({ type: Boolean, default: false })
  bottom!: boolean;
  @Prop({ type: Boolean, default: false })
  top!: boolean;
  tip = false;

  get isBottom() {
    if (!this.bottom && !this.top) return true;
    if (this.bottom) return true;
    return false;
  }

  onCopy() {
    this.tip = true;
    setTimeout(() => {
      this.tip = false;
    }, 1000);
  }
}
export default Copy;
</script>
