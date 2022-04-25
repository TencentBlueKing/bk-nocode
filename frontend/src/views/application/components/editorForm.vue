<template>
  <bk-form :label-width="100" ext-cls="custom-edit-form">
    <form-fields :fields="fieldsList" :value="value" @change="handleSetValue" />
  </bk-form>
</template>
<script>
import FormFields from '@/components/form/formFields/index.vue';
import clonedeep from 'lodash.clonedeep';
import judgeFieldsConditionMixins from '@/components/form/formFields/judgeFieldsConditionMixins';
export default {
  name: 'EditorForm',
  components: { FormFields },
  mixins: [judgeFieldsConditionMixins],
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
  data() {
    return {
      fieldsList: clonedeep(this.fields).filter(item => !['id', 'title'].includes(item.key)),
    };
  },
  watch: {
    fields: {
      handler(val) {
        this.judgeCondition();
      },
      deep: true,
    },
  },
  created() {
    this.judgeCondition();
  },
  methods: {
    handleSetValue(key, $event) {
      this.$emit('change', key, $event);
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-edit-form {
  padding: 0 40px 24px;
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
