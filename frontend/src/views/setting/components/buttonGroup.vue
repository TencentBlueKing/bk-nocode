<template>
  <div class="btn-container">
    <template v-for="(item,index) in buttonGroup">
      <div :class="curIndex===index&&'btn-active'" class="btn-group" :key="item.key">
        <span class="circle" @click.stop="handleDelete(index)" v-if="curIndex===index">
          <i class="bk-icon icon-close"></i>
        </span>
        <span
          :class="index===0?'bk-primary':'bk-default'"
          class="bk-button bk-button-small btn-content"
          :title="item.name"
          @click.stop="handleClick(item,index)">
          {{ item.name }}
        </span>
      </div>
    </template>
    <div class="btn-group" style="padding: 2px">
      <bk-button
        theme="default"
        title="功能按钮"
        size="small"
        icon="plus"
        @click.stop="handleAddFunction">
        添加功能
      </bk-button>
    </div>
    <bk-button
      :theme="'default'"
      size="small"
      v-if="!edit"
      @click="handleExport">
      导出
    </bk-button>
    <bk-dropdown-menu
      @show="dropdownShow"
      @hide="dropdownHide"
      ref="dropdown"
      style="margin-left: 8px"
      v-if="!edit&&buttonGroup.length>1">
      <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
        更多
        <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
      </div>
      <!--      <ul class="bk-dropdown-list" slot="dropdown-content" v-for="item in buttonGroup">-->
      <ul class="bk-dropdown-list" slot="dropdown-content">
        <li><a href="javascript:;" @click="triggerHandler('import')">导入</a></li>
      </ul>
    </bk-dropdown-menu>
  </div>
</template>

<script>
import Bus from '@/utils/bus.js';

export default {
  name: 'ButtonGroup',
  props: {
    buttonGroup: {
      type: Array,
      default: () => [],
    },
    edit: {
      type: Boolean,
      default: true,
    },
    currentIndex: Number,
  },
  data() {
    return {
      isDropdownShow: false,
      isLargeDropdownShow: false,
      curIndex: -1,
    };
  },
  watch: {
    currentIndex: {
      handler(val) {
        if (val === -1) {
          this.curIndex = val;
        }
      },
      immediate: true,
    },
  },
  methods: {
    handleClick(item, index) {
      this.curIndex = index;
      Bus.$emit('selectFunction', { ...item, curIndex: this.curIndex, workSheetId: this.workSheetId || '' });
    },
    handleExport() {
      this.$emit('export');
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(item) {
      if (!this.edit) {
        this.$emit('headerBtnClick', item);
        this.$refs.dropdown.hide();
      }
    },
    handleDelete(index) {
      this.$emit('deleteItem', index);
    },
    handleAddFunction() {
      this.curIndex = this.buttonGroup.length  ;
      this.$emit('handleAddFunction');
      Bus.$emit('selectFunction', { ...this.buttonGroup[this.curIndex], curIndex: this.curIndex, workSheetId: this.workSheetId || '' });
    },
  },
};
</script>

<style scoped lang="postcss">
.btn-container {
  display: flex;
  flex-wrap: wrap;
}

.btn-group {
  margin-right: 8px;
  padding: 2px;
  border: 1px solid transparent;
  position: relative;

  .btn-content{
    max-width: 80px;
    min-width: 48px;
    text-overflow:ellipsis;
    white-space:nowrap;
    overflow:hidden;
    //border: 1px solid #C4C6CC;
    border-radius: 2px;
    height: 26px;
  }
}

.btn-active {
  border: 1px dashed #3a84ff;
  padding: 2px;
  background: #E1ECFF;
}

.dropdown-trigger-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #c4c6cc;
  height: 26px;
  border-radius: 2px;
  padding: 0 15px;
  color: #63656E;
}

.dropdown-trigger-btn.bk-icon {
  font-size: 18px;
}

.dropdown-trigger-btn .bk-icon {
  font-size: 22px;
}

.dropdown-trigger-btn:hover {
  cursor: pointer;
  border-color: #979ba5;
}

.circle {
  position: absolute;
  top: -5px;
  right: -8px;
  width: 14px;
  height: 14px;
  background: #979BA5;
  border-radius: 50%;
  display: block;
  z-index: 5;

  i {
    color: #fcfcfc;
    font-size: 12px;
    height: 14px;
    display: block;
    line-height: 14px;
  }
}
</style>
