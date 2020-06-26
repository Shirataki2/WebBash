<template>
  <v-card-text v-if="visible">
    <v-dialog
      v-model="saveDialog"
      persistent
      max-width="600px"
    >
      <template v-slot:activator="{ on }">
        <v-btn
          color="success"
          block
          v-on="on"
        >Save</v-btn>
      </template>
      <v-card>
        <v-card-title>
          <span class="headline">Save</span>
        </v-card-title>
        <v-card-text>
          <v-form
            v-model="valid"
            ref="form"
          >
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    label="Title *"
                    v-model="title"
                    outlined
                    :counter="32"
                    :rules="[
                      v => !!v || 'User Name is required',
                      v => v.length <= 32 || 'User Name must be less than 32 characters',
                    ]"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    label="Description *"
                    v-model="description"
                    outlined
                    :counter="280"
                    :rules="[
                      v => !!v || 'Description is required',
                      v => v.length <= 280 || 'Description must be less than 280 characters',
                    ]"
                    required
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            text
            @click="onCodeSubmit"
          >Save</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            color="error"
            text
            @click="onCodeCencel"
          >Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card-text>
</template>


<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";

@Component({
  name: "SaveForm"
})
class SaveForm extends Vue {
  @Prop({ type: Boolean, default: false })
  visible!: boolean;
  saveDialog = false;
  valid = false;
  title = "";
  description = "";

  onCodeSubmit() {
    this.title = "";
    this.description = "";
    this.saveDialog = false;
  }

  onCodeCencel() {
    this.title = "";
    this.description = "";
    this.saveDialog = false;
  }
}
export default SaveForm;
</script>
