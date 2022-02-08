<template>
  <section :class="['page-tree-container', { folded }]">
    <div class="btns-area">
      <bk-button theme="primary" title="新增分组" :text="true" @click="createGroup = true">
        <i class="custom-icon-font icon-add-circle"></i>
        新增分组
      </bk-button>
      <bk-button theme="primary" title="新增页面" :text="true" @click="$emit('createPage')">
        <i class="custom-icon-font icon-add-circle"></i>
        新增页面
      </bk-button>
    </div>
    <div class="page-tree-content">
      <page-nav-item
        v-if="createGroup"
        type="group"
        :edit="true"
        :app-id="appId"
        @create="handleCreateGroup"
        @cancel="createGroup = false">
      </page-nav-item>
      <draggable handle=".drag-icon" :group="{ name: 'root', put: 'page' }" :list="pageList" @end="handleDragChange">
        <page-nav-item
          v-for="page in pageList"
          :key="page.id"
          :type="page.type === 'GROUP' ? 'group' : 'page'"
          :app-id="appId"
          :page="page"
          :crt-page="crtPage"
          @dragEnd="handleDragChange"
          @update="handleUpdatePage"
          @delete="handleDeletePage"
          @createPage="$emit('createPage', $event)"
          @select="$emit('select', $event)">
        </page-nav-item>
      </draggable>
    </div>
    <div class="fold-btn" @click="folded = !folded">
      <i :class="['bk-icon icon-angle-left-line', { flip: folded }]"></i>
    </div>
  </section>
</template>

<script>
import draggable from 'vuedraggable';
import cloneDeep from 'lodash.clonedeep';
import pageNavItem from './pageNavItem.vue';

export default {
  name: 'PageTree',
  components: {
    draggable,
    pageNavItem,
  },
  props: {
    appId: String,
    rootPageId: Number,
    pageList: {
      type: Array,
      default: () => [],
    },
    crtPage: {
      validator(val) {
        return typeof val === 'number' || val === '';
      },
    },
  },
  data() {
    return {
      createGroup: false,
      folded: false,
    };
  },
  methods: {
    async handleDragChange(e) {
      console.log(e.item.dataset.id);
      const pageId = Number(e.item.dataset.id);
      const newOrder = e.newIndex;
      let parentId;
      this.pageList.some(group => {
        if (group.id === pageId) {
          parentId = this.rootPageId;
          return true;
        }
        if (group.children && group.children.length > 0) {
          return group.children.some(item => {
            if (item.id === pageId) {
              parentId = group.id;
              return true;
            }
          });
        }
      });
      try {
        const params = {
          id: pageId,
          data: {
            new_order: newOrder,
            parent_id: parentId,
            project_key: this.appId,
          },
        };
        await this.$store.dispatch('setting/pageDragSort', params);
      } catch (e) {
        console.error(e);
      }
      console.log(pageId, newOrder, parentId);
    },
    handleCreateGroup(data) {
      const list = this.pageList.slice(0);
      list.push(cloneDeep(data));
      this.$emit('update', list);
      this.createGroup = false;
    },
    handleUpdatePage(data) {
      const list = cloneDeep(this.pageList);
      const { groupIndex, pageIndex } = this.findPage(data.id);
      if (pageIndex > -1) {
        list[groupIndex].children[pageIndex] = cloneDeep(data);
      } else {
        list[groupIndex] = cloneDeep(data);
      }
      this.$emit('update', list);
    },
    handleDeletePage(id) {
      const list = cloneDeep(this.pageList);
      const { groupIndex, pageIndex } = this.findPage(id);
      if (pageIndex > -1) {
        list[groupIndex].children.splice(pageIndex, 1);
      } else {
        list.splice(groupIndex, 1);
      }
      this.$emit('update', list);
    },
    findPage(id) {
      let groupIndex = -1;
      let pageIndex = -1;
      this.pageList.some((group, index) => {
        groupIndex = index;
        if (group.id === id) {
          return true;
        }
        if (group.children) {
          return group.children.some((page, i) => {
            if (page.id === id) {
              pageIndex = i;
              return true;
            }
          });
        }
      });
      return { groupIndex, pageIndex };
    },
  },
};
</script>

<style scoped lang="postcss">
.page-tree-container {
  position: relative;
  width: 216px;
  height: 100%;
  background: #fcfcfc;
  border-right: 1px solid #dcdee5;
  transition: width 0.2s ease-in-out;
  &.folded {
    width: 0;
    border: none;
    .btns-area {
      display: none;
    }
  }
}
.btns-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  background: #ffffff;
  box-shadow: 0 1px 0 0 #dcdee5;
  .bk-button-text {
    width: 50%;
    text-align: center;
  }
  i {
    font-size: 14px;
  }
}
.page-tree-content {
  height: calc(100% - 40px);
  overflow: auto;
}
.fold-btn {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 12px;
  height: 32px;
  background: #dcdee5;
  border-radius: 0 6px 6px 0;
  z-index: 1;
  cursor: pointer;
  &:hover {
    i {
      color: #3a84ff;
    }
  }
  i {
    font-size: 12px;
    color: #ffffff;
    transition: transform 0.2s ease-in-out;
    &.flip {
      transform: rotate(-180deg);
    }
  }
}
</style>
