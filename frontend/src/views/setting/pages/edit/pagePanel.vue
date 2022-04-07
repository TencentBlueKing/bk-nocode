<template>
  <div :class="['page-panel',pageList.length===0&&'edit-panel']">
    <draggable
      filter=".actions-area"
      :class="['page-container', activeCls]"
      :value="pageList"
      :group="{ name: 'form', pull: true, put: ['menu', 'half-row-field'] }"
      @add="add"
      @end="end">
      <page-element
        v-for="(page,index) in pageList"
        :page="page"
        :class="{ actived: selectedIndex === index }"
        :key="`${page.type}_${index}`"
        @action="handleFormAction($event, index)">
      </page-element>
      <span class="tip" v-if="pageList.length===0">拖拽组件到这里</span>
    </draggable>
  </div>
</template>

<script>
import {  PAGE_TYPE_MAP }  from '@/constants/comps.js';
import pageElement from './pageElement.vue';
import cloneDeep from 'lodash.clonedeep';
import draggable from 'vuedraggable';
export default {
  name: 'PagePanel',
  components: {
    pageElement,
    draggable,
  },
  props: {
    pageList: {
      type: Array,
      default: () => ([]),
    },
    pageId: [String, Number],
    hover: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      selectedIndex: -1,
    };
  },
  computed: {
    activeCls() {
      if (this.hover) {
        return `hover ${this.pageList.length === 0 ? 'add-first-comp' : ''}`;
      }
      return '';
    },
  },
  methods: {
    add(e) {
      const { type } = e.item.dataset;
      const  config = this.getConfigSetting(type);
      const pageConfig = {
        type: PAGE_TYPE_MAP[type],
        ...config,
      };
      const index = this.pageList.length === 0 ? 0 : e.newIndex;
      this.$emit('add', pageConfig, index);
      this.selectedIndex = index;
    },
    // 排序
    end(e) {
      console.log(e);
    },
    handleFormAction(type, index) {
      const page = cloneDeep(this.pageList[index]);
      if (type === 'edit') {
        this.$emit('select', page, index);
        this.selectedIndex = index;
      } else if (type === 'copy') {
        delete page.id;
        this.$emit('copy', page, index);
        this.selectedIndex = index + 1;
      } else if (type === 'delete') {
        this.$emit('delete', index);
        if (this.selectedIndex === index) {
          this.selectedIndex = -1;
        }
      }
    },
    getConfigSetting(type) {
      let config;
      switch (type) {
        case 'LINKGROUP':
          config = {
            config: { name: '分组名称' },
            layout: { display: 'row', lineLayout: 'COL_12' },
            children: [{
              value: '',
              config: {
                name: '新建项目',
              },
            }],
          };
          break;
        case 'QUICKENTRANCE':
          config = {
            config: {
              name: '默认标题',
              desc: '',
              bgColor: '',
              component_order: [],
              path: '',
            },
            children: [],
            layout: { lineLayout: '' },
            value: '',
          };
          break;
      }
      return config;
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../../css/scroller.css";
.page-panel {
  margin: 24px 24px 0 24px;
  height: calc(100% - 56px);
  width: 100%;
  flex: 1;
  @mixin scroller;
}
.edit-panel{
  height: 69px;
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;
  border: 1px dashed #C4C6CC;
}
.tip{
  font-size: 14px;
  color: #313238;
  text-align: center;
  display: block;
  line-height: 67px;
}

.page-container {
  height: 100%;
  overflow: auto;
  &.hover {
    outline: 2px dashed #1768ef;
    border-radius: 4px;
  }
  &.add-first-comp {
    background: rgba(23, 104, 239, 0.1);
  }
}
.page-element {
  &.actived {
    border: 1px dashed #3a84ff;
  }
}
</style>
