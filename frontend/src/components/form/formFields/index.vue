<template>
  <div class="form-fields">
    <field-form-item
      v-for="field in fields"
      :key="field.key"
      :field="field"
      :use-fixed-data-source="useFixedDataSource"
      :value="localValue[field.key]"
      @change="handleChange(field.key, $event)"></field-form-item>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import FieldFormItem from './fieldItem.vue';

export default {
  name: 'FormFields',
  components: {
    FieldFormItem,
  },
  props: {
    fields: {
      type: Array,
      default: () => [],
    },
    useFixedDataSource: {
      type: Boolean,
      default: false,
    },
    value: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      localValue: this.getFieldsValue(this.fields),
    };
  },
  watch: {
    fields() {
      this.localValue = this.getFieldsValue();
    },
    value() {
      this.localValue = this.getFieldsValue();
    },
  },
  methods: {
    // 获取变量value，优先去props传入的value值，若没有则取默认值
    getFieldsValue() {
      const fieldsValue = {};
      this.fields.map((item) => {
        if (item.key in this.value) {
          fieldsValue[item.key] = cloneDeep(this.value[item.key]);
        } else if ('default' in item) {
          if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS', 'TABLE', 'IMAGE', 'FILE'].includes(item.type)) {
            fieldsValue[item.key] = item.default ? item.default.split(',') : [];
          } else {
            fieldsValue[item.key] = item.default;
          }
        }
      });
      return fieldsValue;
    },
    handleChange(key, value) {
      this.localValue[key] = value;
      this.$emit('change', cloneDeep(this.localValue));
    },
  },
};
</script>
<style lang="postcss" scoped>
.form-fields{
  display: flex;
  flex-wrap: wrap;
}
</style>
