<template>
  <v-container fluid>
    <v-row>
      <v-col
        v-for="image in images"
        :key="image"
        class="d-flex child-flex"
        cols="6"
        sm="3"
        md="6"
        xl="3"
      >
        <v-card flat tile class="d-flex">
          <v-dialog v-model="dialog" max-width="1800">
            <template v-slot:activator="{ on }">
              <v-img
                :src="image"
                v-on="on"
                @click="() => (src = image)"
                aspect-ratio="1.6"
                class="grey lighten-2"
                max-height="100%"
                style="cursor: pointer"
              >
                <template v-slot:placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular indeterminate color="grey lighten-5" />
                  </v-row>
                </template>
              </v-img>
            </template>
            <v-img :src="src"> </v-img>
            <v-btn
              block
              :href="src"
              v-if="!disableDownload"
              target="_blank"
              large
            >
              <v-icon>mdi-download</v-icon>
              Download
            </v-btn>
          </v-dialog>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Vue, Component, Prop } from "vue-property-decorator";

@Component
class ImageViewer extends Vue {
  src = "";
  dialog = false;
  @Prop({ type: Boolean, default: false })
  disableDownload!: boolean;

  @Prop({ type: Array, default: [] })
  images!: string[];
}
export default ImageViewer;
</script>
