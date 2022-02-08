<template>
  <div class="checkbox">
    <bk-checkbox-group v-model="val" @change="change">
      <bk-checkbox v-for="option in sourceData" :value="option.key" :disabled="disabled" :key="option.key">
        {{ option.name }}
      </bk-checkbox>
    </bk-checkbox-group>
  </div>
</template>
<script>
import dataSourceMixins from '../dataSourceMixins.js';

export default {
  name: 'Checkbox',
  mixins: [dataSourceMixins],
  props: {
    field: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: [Array, String],
      // default: () => [],
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      val: Array.isArray(this.value) ? [...this.value] : [this.value],
    };
  },
  watch: {
    value(val) {
      this.val = Array.isArray(val) ? [...val] : [val];
    },
  },
  methods: {
    change(val) {
      this.$emit('change', val);
    },
  },
};
</script>
<style lang="postcss" scoped>
.bk-form-checkbox {
  margin-right: 24px;
}
</style>
