<template>
  <bk-form :label-width="100" ext-cls="custom-form">
    <form-fields :fields="currentFields" :value="value" @change="handleSetValue" />
  </bk-form>
</template>
<script>
import FormFields from '@/components/form/formFields/index.vue';
export default {
  name: 'EditorForm',
  components: { FormFields },
  props: {
    fields: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    currentFields() {
      return this.fields.filter(item => !['id', 'title'].includes(item.key));
    },
  },
  methods: {
    handleSetValue($event, index) {
      this.$emit('change', $event, index);
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-form {
  padding: 24px 40px 0;
  /deep/ .bk-label-text {
    font-size: 14px;
    color: #979ba5;
  }
  /deep/ .bk-form-content {
    font-size: 14px;
    color: #63656e;
  }
}
</style>
