<template>
  <v-card-text v-if="visible">
    <v-dialog v-model="saveDialog" persistent max-width="600px">
      <template v-slot:activator="{ on }">
        <v-btn color="success" block v-on="on">Post</v-btn>
      </template>
      <v-card>
        <v-card-title>
          <span class="headline">New Post</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="valid" ref="form">
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    label="タイトル(必須)"
                    v-model="title"
                    outlined
                    :counter="32"
                    :rules="[
                      v => !!v || 'User Name is required',
                      v =>
                        v.length <= 32 ||
                        'User Name must be less than 32 characters'
                    ]"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    label="説明(任意)"
                    v-model="description"
                    outlined
                    :counter="280"
                    :rules="[
                      v =>
                        v.length <= 280 ||
                        'Description must be less than 280 characters'
                    ]"
                    required
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" text @click="onCodeCencel">Cancel</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="onCodeSubmit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card-text>
</template>


<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";
import checkToken from "@/utils/check_token";
import Cookies from "js-cookie";
/* eslint-disable @typescript-eslint/camelcase */

@Component({
  name: "SaveForm"
})
class SaveForm extends Vue {
  @Prop({ type: Boolean, default: false })
  visible!: boolean;
  @Prop({ type: Array, default: () => [] })
  images!: string[];
  @Prop({ type: Array, default: () => [] })
  media!: string[];
  @Prop({ type: String, default: "" })
  stdout!: string;
  @Prop({ type: String, default: "" })
  stderr!: string;
  @Prop({ type: String, default: "" })
  exitcode!: string;
  saveDialog = false;
  valid = false;
  title = "";
  description = "";

  async onCodeSubmit() {
    try {
      // eslint-disable-next-line
      const data = await checkToken(this);
      const accessToken = Cookies.get("access_token");
      await this.$axios.post(
        "/api/posts/",
        {
          title: this.title,
          description: this.description,
          main: this.$store.state.code,
          posted_images: this.media,
          generated_images: this.images,
          stdout: this.stdout,
          stderr: this.stderr,
          exitcode: this.exitcode
        },
        {
          headers: {
            "access-token": accessToken
          }
        }
      );
    } finally {
      this.title = "";
      this.description = "";
      this.saveDialog = false;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const form: any = this.$refs.form;
      form.resetValidation();
    }
  }

  onCodeCencel() {
    this.title = "";
    this.description = "";
    this.saveDialog = false;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const form: any = this.$refs.form;
    form.resetValidation();
  }
}
export default SaveForm;
</script>
