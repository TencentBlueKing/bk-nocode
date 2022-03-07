<template>
  <div
    v-bkloading="{ isLoading: loading }"
    v-bk-clickoutside="closeTree"
    class="bk-search-tree"
    :class="extCls">
    <div
      class="bk-search-tree-wrapper"
      @click.stop="showTree('view')">
            <span :class="{ 'bk-color-tree': displayName }">
                {{ displayName || "请选择"}}
            </span>
      <i class="bk-select-angle bk-icon icon-framework"></i>
    </div>
    <transition name="common-fade">
      <div class="bk-search-tree-content" v-show="isShowTree">
        <tree
          :tree-data-list="displayList"
          @toggle="toggleInfo"
          @toggleChildren="toggleChildren(...arguments,'view')">
        </tree>
      </div>
    </transition>
  </div>
</template>

<script>
import Tree from './Tree.vue';
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'SelectTree',
  components: {
    Tree,
  },
  model: {
    prop: 'value',
    event: 'selected',
  },
  props: {
    list: {
      type: Array,
      default: () => ([]),
    },
    value: {
      type: [Number, String, Array],
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    loading: {
      type: Boolean,
      default: false,
    },
    extCls: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isShowTree: false,
      displayName: '',
      displayList: [],
      checked: null,
    };
  },
  watch: {
    list() {
      this.initData();
    },
    value(val) {
      this.initData();
    },
    loading() {
      this.initData();
    },
  },
  created() {
    this.initData();
  },
  methods: {
    initData() {
      this.displayList = cloneDeep(this.list);
      if (this.displayList.length) {
        this.displayList.forEach((tree) => {
          this.setCheckedValue(tree);
        });
      }
      if (this.value && this.checked) {
        this.displayList.forEach((tree) => {
          this.openChildren(tree);
        });
      }
      if (this.checked) {
        this.$emit('change', cloneDeep(this.checked));
      }
    },
    setCheckedValue(tree) {
      this.$set(tree, 'checkInfo', false);
      this.$set(tree, 'has_children', !!(tree.children && tree.children.length));
      if (this.value && String(this.value) === String(tree.id)) {
        tree.checkInfo = true;
        this.checked = tree;
        this.setDispalyName();
        return;
      }
      if (tree.has_children) {
        this.$set(tree, 'showChildren', false);
        tree.children.forEach((item) => {
          this.setCheckedValue(item);
        });
      }
    },
    openChildren(tree) {
      this.$set(tree, 'showChildren', false);
      this.$set(tree, 'showChildren', this.checked.route.some(item => String(item.id) === String(tree.id)));
      if (!(tree.children && tree.children.length)) {
        return;
      }
      tree.children.forEach((item) => {
        this.openChildren(item);
      });
    },
    setDispalyName() {
      let nameList = [];
      if (this.checked.route.length) {
        nameList = this.checked.route.map(item => item.name);
      }
      nameList.push(this.checked.name);
      this.displayName = nameList.join('/');
    },
    showTree() {
      if (this.loading) {
        return;
      }
      this.isShowTree = true;
    },
    closeTree() {
      this.isShowTree = false;
    },
    toggleInfo(tree) {
      this.checked = tree;
      this.setDispalyName();
      this.cancelAllSectedStatus();
      this.$set(tree, 'checkInfo', true);
      this.$emit('selected', tree.id);
      this.$emit('change', cloneDeep(tree));
      this.closeTree();
    },
    cancelAllSectedStatus(list = this.displayList) {
      list.forEach((tree) => {
        this.$set(tree, 'checkInfo', false);
        if (tree.children && tree.children.length) {
          this.cancelAllSectedStatus(tree.children);
        }
      });
    },
    toggleChildren(item) {
      this.$set(item, 'showChildren', !item.showChildren);
    },
  },
};
</script>

<style lang='postcss' scoped>
.bk-search-tree {
  background: #ffffff;
  .bk-color-tree {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
.bk-search-tree-content {
  height: 170px;
}
</style>
