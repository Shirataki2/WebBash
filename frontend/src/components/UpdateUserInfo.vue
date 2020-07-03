<template>
  <v-card style="background-color: transparent" class="mb-5 mt-9" elevation="0">
    <v-form v-model="valid" ref="form" lazy-validation @submit.prevent>
      <v-text-field
        label="ユーザネーム (必須)"
        v-model="newName"
        outlined
        :counter="50"
        :rules="[
          v => !!v || 'この項目は必須です',
          v => v.length <= 50 || '50文字以下で指定してください'
        ]"
        required
      />
      <v-file-input
        accept="image/*"
        label="アバター画像"
        @change="onFileSelected"
        :rules="[
          file => !file || file.size < 2097152 || '画像サイズの上限は2MBです'
        ]"
      />
      <v-btn
        block
        color="success"
        @click="submit"
        class="mb-5 mt-9"
        :loading="isLoad"
      >
        更新
      </v-btn>
    </v-form>
  </v-card>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import checkToken from "@/utils/check_token";
import Cookies from "js-cookie";

@Component({
  name: "UpdateUserInfo"
})
class UpdateUserInfo extends Vue {
  @Prop({ type: String, required: true })
  username!: string;
  newName = "";
  valid = false;

  isLoad = false;

  media: Blob | null = null;
  onFileSelected(e: File) {
    this.media = e;
  }

  mounted() {
    this.newName = this.username;
  }

  async submit() {
    this.isLoad = true;
    try {
      const formdata = new FormData();
      await checkToken(this);
      const accessToken = Cookies.get("access_token");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const form: any = this.$refs.form;
      if (form.validate()) {
        if (this.media) formdata.append("avater", this.media);
        formdata.append("username", this.newName);
        await this.$axios.put("/api/users/me", formdata, {
          headers: {
            "access-token": accessToken
          }
        });
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const r: any = this.$router;
        r.go({ path: this.$router.currentRoute.path, force: true });
      }
    } catch {
      this.$store.dispatch("setMessage", {
        snackbarType: "error",
        message: "エラーが発生しました"
      });
      this.isLoad = false;
    }
  }
}
export default UpdateUserInfo;
</script>

<style>
</style>
