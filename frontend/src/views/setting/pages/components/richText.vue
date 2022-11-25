<template>
  <div :class="['rich-text',{ 'show-rich-text': $route.name!=='customPage' }]">
    <rich-text-editor :value="val" :disabled="disabled" @change="change" :preview="preview"></rich-text-editor>
  </div>
</template>
<script>
import RichTextEditor from '@/components/richTextEditor.vue';
export default {
  name: 'RichText',
  components: {
    RichTextEditor,
  },
  props: {
    preview: {
      type: Boolean,
      default: false,
    },
    page: {
      type: Object,
      default: () => ({}),
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      val: this.page.config.content,
    };
  },
  watch: {
    value(val) {
      this.val = val;
    },
  },
  methods: {
    change(val) {
      this.$emit('change', val);
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../../css/scroller.css";
.rich-text{
  /*height: 50%;*/
  overflow-y: scroll;
  /*@mixin scroller;*/
  /*/deep/ .toastui-editor-contents{*/
  /*  p{*/
  /*    margin: 0;*/
  /*  }*/

  /*  img{*/
  /*    margin: 0;*/
  /*  }*/
  /*}*/
}
.show-rich-text{
  background: #fff;
  margin-top: 24px;
}
</style>
