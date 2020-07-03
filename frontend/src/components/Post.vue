<template>
  <v-card
    style="background-color: transparent; margin; border-bottom: 1px solid #777;"
    class="grid-list-xs"
    elevation="0"
  >
    <v-card-title>
      <v-avatar size="42">
        <img :src="post.owner.avater_url || ''" />
      </v-avatar>
      <span class="subtitle-1 font-weight-bold ml-2">
        {{ post.owner.username || "" }}
        <span class="ml-2 mr-4 subtitle-2">&#x2027;</span>
        <span class="subtitle-2 font-weight-light grey--text">
          {{ post.post_at ? parseDate(post.post_at) : "" }}
        </span>
      </span>
      <v-spacer />
      <span v-if="post.owner.id === $store.state.userId">
        <v-btn small icon @click="deletePost">
          <v-icon color="red darken-4">mdi-trash-can</v-icon>
        </v-btn>
      </span>
      <confirm :ref="post.id" />
    </v-card-title>
    <v-card-text>
      <div
        @click="
          $router
            .push(`/user/${post.owner.id || ''}/post/${post.id || ''}`)
            .catch(() => {})
        "
        style="cursor: pointer"
      >
        <p class="subtitle-1 font-weight-bold mt-n2 mb-n1">
          {{ post.title || "" }}
        </p>
        <p class="mt-2 mb-1 ml-3 mr-3">
          {{ post.description || "" }}
        </p>
        <v-divider />
        <p
          class="mt-2 mb-n3"
          style="font-family: monospace;white-space: pre-line; word-wrap:break-word;font-size:1em"
        >
          {{ post.stdout ? previewResult(post.stdout) : "" }}
        </p>
      </div>
      <ImageViewer
        class="mt-n3 mb-n3"
        v-if="post.generated_images"
        :images="post.generated_images.map(image => image.url)"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { Vue, Component, Prop } from "vue-property-decorator";
import parseDate from "@/utils/parseDate";
import ImageViewer from "@/components/ImageViewer.vue";
import Confirm from "@/components/Confirm.vue";

@Component({
  name: "Post",
  components: {
    ImageViewer,
    Confirm
  }
})
class Post extends Vue {
  @Prop({ type: Object, required: true })
  post!: any;

  @Prop({ type: Function, required: true })
  onDelete!: (post: object) => void;

  parseDate(date: string) {
    return parseDate(date);
  }

  previewResult(s: string) {
    const numNewline = s.match(/\n/)?.length || 0;
    const numChar = s.length;
    let t = s;
    if (numNewline > 20) {
      t =
        t
          .split(/\n/)
          .slice(0, 20)
          .join("\n") + "...";
    }
    if (numChar > 300) {
      t = t.slice(0, 300) + "...";
    }
    return t;
  }

  async deletePost() {
    const confirm: any = this.$refs[`${this.post.id}`];
    if (
      await confirm.open("投稿の削除", "本当に削除しますか", {
        color: "error"
      })
    ) {
      await this.onDelete(this.post);
    }
  }
}
export default Post;
</script>
