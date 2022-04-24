<template>
  <div class="bk-select-tag width-limit-tag">
    <span v-bk-overflow-tips style="overflow: hidden">{{ tag.display_name || tag.name }}</span>
    <i class="bk-icon icon-close" @click="$emit('delete', tag)"></i>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'MemberTag',
  props: {
    member: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      tag: cloneDeep(this.member),
    };
  },
  watch: {
    member(val) {
      this.tag = val;
    },
  },
};
</script>

<style scoped lang="postcss">
.bk-select-tag {
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
.width-limit-tag {
  display: inline-flex;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  i {
    font-size: 14px;
    cursor: pointer;
  }
}
</style>
