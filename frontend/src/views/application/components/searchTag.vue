<template>
  <div class="bk-select-tag width-limit-tag">
    <span>{{tag.name}}：</span>
    <span>{{ tag.value }}</span>
    <i class="bk-icon icon-close" @click="$emit('delete',tag)"></i>
  </div>
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

<style scoped lang="postcss">
.bk-select-tag{
  margin: 8px;
  height: 22px;
  line-height: 22px;
  padding: 0 2px 0 5px;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  background: #f0f1f5;
  border-radius: 2px;
  font-size: 12px;
}
.width-limit-tag{
  display: inline-flex;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #63656E;
  i{
    font-size: 14px;
    cursor: pointer;
  }
}
</style>

