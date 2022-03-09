<template>
  <bk-tag closable @close="$emit('delete',tag)">
    <span>{{tag.name}}：</span>
    <span>{{ tag.value }}</span>
  </bk-tag>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'SearchTag',
  props: {
    searchItem: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      tag: cloneDeep(this.searchItem),
    };
  },
};
</script>


