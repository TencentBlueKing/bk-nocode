<template>
  <div class="multi-select">
    <bk-select
      v-model="val"
      :multiple="true"
      :disabled="disabled"
      :searchable="true"
      :loading="sourceDataLoading"
      @change="change">
      <bk-option v-for="option in sourceData" :key="option.key" :id="option.key" :name="option.name"> </bk-option>
    </bk-select>
  </div>
</template>
<script>
import dataSourceMixins from '../dataSourceMixins.js';

export default {
  name: 'MultiSelect',
  mixins: [dataSourceMixins],
  props: {
    field: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: Array,
      default: () => [],
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      val: [...this.value],
    };
  },
  watch: {
    value(val) {
      this.val = [...val];
    },
  },
  methods: {
    change(val) {
      this.$emit('change', val);
    },
  },
};
</script>
