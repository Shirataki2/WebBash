<template>
  <codemirror
    :value="code"
    @input="(newCode) => $emit('updateCode', newCode)"
    :options="{...cmOptions, ...{theme: $vuetify.theme.dark ? 'material' : 'mdn-like'}}"
  />
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";

@Component({
  model: {
    prop: "code",
    event: "updateCode"
  }
})
class Editor extends Vue {
  @Prop({ type: String, default: "" })
  code = "";

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
