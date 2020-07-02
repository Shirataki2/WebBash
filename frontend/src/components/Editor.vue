<template>
  <codemirror
    :value="$store.state.code"
    @input="
      newCode => {
        $store.dispatch('setCode', newCode);
      }
    "
    :options="{
      ...cmOptions,
      ...{ theme: $vuetify.theme.dark ? 'material' : 'mdn-like' }
    }"
  />
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component({})
class Editor extends Vue {
  //@Prop({ type: String, default: "" })
  //code = "";

  cmOptions = {
    tabSize: 4,
    styleActiveLine: true,
    lineNumbers: true,
    line: true,
    lineWrapping: true,
    theme: "material",
    mode: "shell",
    autoCloseBrackets: true,
    matchBrackets: true,
    showTrailingSpace: true
  };
}
export default Editor;
</script>
