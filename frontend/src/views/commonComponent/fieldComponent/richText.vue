<template>
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :desc="item.tips" desc-type="icon">
    <rich-text-editor :value="val" @change="change"></rich-text-editor>
    </bk-form-item>
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
    item: {
      type: Object,
      required: true,
      default: () => {
      },
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      val: '',
    };
  },
  watch: {
    val(val) {
      this.item.val = val;
    },
  },
  created() {
    this.item.val = '';
  },
  methods: {
    change(val) {
      this.val = val;
      this.$emit('change', val);
    },
  },
};
</script>
