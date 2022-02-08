<template>
  <div>
    <bk-big-tree
      ref="tree"
      ext-cls="menu-permission"
      :options="{ nameKey: 'name',idKey: 'id' }"
      :show-checkbox="true"
      :data="tree"
      @check-change="handleCheck">
    </bk-big-tree>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'MenuPermission',
  props: {
    treeInfo: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Array,
      default: () => ([]),
    },
  },
  data() {
    return {
      checkList: [],
      tree: cloneDeep(this.treeInfo),
      treeValue: cloneDeep(this.value),
    };
  },
  watch: {
    treeInfo: {
      handler(val) {
        this.tree = val;
        if (this.treeValue.length > 0) {
          this.$nextTick(() => {
            this.setChecked(this.treeValue);
          });
        }
      },
      deep: true,
      immediate: true,
    },
    value: {
      handler(val) {
        this.treeValue = val;
      },
      immediate: true,
    },
  },
  methods: {
    setChecked(val) {
      const idList = val.map(el => el.id);
      // 将传入的节点信息发出去
      // const tempNodeData = [];
      this.tree.forEach((item) => {
        if (idList.includes(item.id)) {
          this.$refs.tree.setChecked(item.id);
          // tempNodeData.push(item);
          // this.$emit('checkNode', item);
        } else if (item.children) {
          item.children.forEach((child) => {
            if (idList.includes(child.id)) {
              // tempNodeData.push(child);
              // this.$emit('checkNode', child);
              this.$refs.tree.setChecked(child.id);
            }
          });
        }
      });
    },
    handleCheck(id, { data }) {
      this.$emit('checkNode', data);
    },
  },
};
</script>

<style scoped lang="postcss">
.menu-permission {
  /deep/ .bk-big-tree-node {
    height: 36px;
  }
}
</style>
