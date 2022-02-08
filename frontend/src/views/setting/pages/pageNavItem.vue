<template>
  <div :class="['page-nav-item', { 'has-group': page.children && page.children.length > 0 }]" :data-id="page.id">
    <div
      :class="['page-item-container', { 'popover-open': popoverOpen, actived: crtPage === page.id }]"
      @click="handlePageClick">
      <div class="drag-area">
        <i v-if="!isEdit" class="bk-icon icon-grag-fill drag-icon"></i>
      </div>
      <div class="name-wrapper">
        <i v-if="type === 'group'" :class="['bk-icon', 'icon-right-shape', 'arrow-icon', { expanded }]"></i>
        <bk-input
          v-if="isEdit"
          ref="nameInput"
          size="small"
          :placeholder="placeholder"
          :class="['name-input', { error: nameError }]"
          v-model="localName"
          @change="nameError = false">
        </bk-input>
        <div v-else class="name-text">{{ localName }}</div>
        <i v-if="!isEdit && page.display_type === 'GENERAL'" class="bk-icon icon-eye-slash hidden-icon"></i>
      </div>
      <div class="opt-icons">
        <template v-if="isEdit">
          <i v-if="!namePending" class="bk-icon icon-check-line save-icon" @click.stop="handleSaveNameClick"></i>
          <bk-spin v-else size="mini"></bk-spin>
          <i
            :class="['bk-icon', 'icon-close-line-2', 'close-icon', { disabled: namePending }]"
            @click.stop="handleCloseClick">
          </i>
        </template>
        <template v-else>
          <i v-if="type === 'group'" class="bk-icon icon-plus-line add-icon" @click.stop="$emit('createPage', page.id)">
          </i>
          <bk-popover
            placement="bottom-start"
            theme="light"
            ext-cls="more-actions-popover"
            :on-show="onPopoverShow"
            :on-hide="onPopoverHide"
            :tippy-options="{ arrow: false, hideOnClick: false }">
            <i class="bk-icon icon-more more-icon" @click.stop></i>
            <div class="more-action" slot="content">
              <div class="action-item" @click="onEditNameClick">
                <i class="bk-icon icon-edit-line "></i>
                编辑名称
              </div>
              <div class="action-item" @click="handleDelete">
                <i class="bk-icon icon-delete"></i>
                删除
              </div>
            </div>
          </bk-popover>
        </template>
      </div>
    </div>
    <draggable
      v-if="page.children && page.children.length > 0 && expanded"
      class="group-page-container"
      handle=".drag-icon"
      :group="{ name: 'page', put: handleElPut }"
      :list="page.children"
      @end="$emit('dragEnd', $event)">
      <page-nav-item
        v-for="item in page.children"
        type="page"
        :key="item.id"
        :app-id="appId"
        :page="item"
        :crt-page="crtPage"
        @update="$emit('update', $event)"
        @delete="$emit('delete', $event)"
        @createPage="$emit('createPage', $event)"
        @select="$emit('select', $event)">
      </page-nav-item>
    </draggable>
  </div>
</template>
<script>
import draggable from 'vuedraggable';

export default {
  name: 'PageNavItem',
  components: {
    draggable,
  },
  props: {
    appId: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: 'group', // group, page
    },
    page: {
      type: Object,
      default: () => ({}),
    },
    crtPage: [Number, String],
    edit: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localName: this.page.name || '',
      isEdit: this.edit,
      nameError: false,
      expanded: true,
      namePending: false,
      deletePending: false,
      popoverOpen: false,
    };
  },
  computed: {
    placeholder() {
      return this.type === 'group' ? '请输入分组名称' : '请输入页面名称';
    },
  },
  watch: {
    name(val) {
      this.localName = val;
    },
  },
  mounted() {
    if (this.edit) {
      this.$refs.nameInput.focus();
    }
  },
  methods: {
    // 处理页面拖拽，分组内页面可以拖拽到另外一个分组或最外层
    handleElPut(to, from, el) {
      const groupName = from.options.group.name;
      return groupName === 'page' || (groupName === 'root' && !el.classList.contains('has-group'));
    },
    handlePageClick() {
      if (this.type === 'group') {
        this.expanded = !this.expanded;
      } else {
        this.$emit('select', this.page);
      }
    },
    handleSaveNameClick() {
      if (this.localName === '') {
        this.$bkMessage({
          theme: 'error',
          message: this.placeholder,
        });
        this.nameError = true;
        return;
      }
      if (this.type === 'group' && this.page.id === undefined) {
        this.createGroup();
      } else {
        this.updateName();
      }
    },
    handleCloseClick() {
      if (this.namePending) {
        return;
      }
      if (typeof this.page.id === 'number') {
        this.localName = this.page.name || '';
        this.isEdit = false;
      } else {
        // 取消新建分组
        this.$emit('cancel');
      }
    },
    // 创建分组
    async createGroup() {
      try {
        this.namePending = true;
        const params = {
          project_key: this.appId,
          name: this.localName,
          type: 'GROUP',
        };
        const res = await this.$store.dispatch('setting/createPage', params);
        this.$emit('create', res.data);
      } catch (e) {
        console.error(e);
      } finally {
        this.namePending = false;
      }
    },
    // 更新页面名称
    async updateName() {
      try {
        this.namePending = true;
        const params = {
          project_key: this.appId,
          id: this.page.id,
          type: this.page.type,
          name: this.localName,
        };
        const res = await this.$store.dispatch('setting/updatePage', params);
        this.isEdit = false;
        this.$emit('update', res.data);
      } catch (e) {
        console.error(e);
      } finally {
        this.namePending = false;
      }
    },
    // 删除页面、分组
    handleDelete() {
      if (this.deletePending) {
        return;
      }
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除${this.type === 'group' ? '分组' : '页面'}：${this.page.name}？`,
        confirmLoading: true,
        confirmFn: async () => {
          if (this.deletePending) {
            return;
          }
          try {
            this.formDeletePending = true;
            const params = {
              id: this.page.id,
              project_key: this.page.project_key,
            };
            await this.$store.dispatch('setting/deletePage', params);
            this.$emit('delete', this.page.id);
          } catch (e) {
            console.error(e);
          } finally {
            this.deletePending = false;
          }
        },
      });
    },
    onPopoverShow() {
      this.popoverOpen = true;
    },
    onPopoverHide() {
      this.popoverOpen = false;
    },
    onEditNameClick() {
      this.isEdit = true;
      this.$nextTick(() => {
        this.$refs.nameInput.focus();
      });
    },
  },
};
</script>
<style lang="postcss" scoped>
.page-item-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  cursor: pointer;
  &:hover{
    background: #F0F1F5;
    .name-text {
      color: #3a84ff;
    }
  };
  &.popover-open,
  &.actived {
    background: #e1ecff;
    .name-text {
      color: #3a84ff;
    }
  }
  &:hover,
  &.popover-open {
    .drag-area .drag-icon {
      display: inline-block;
    }
    .opt-icons {
      .add-icon,
      .more-icon {
        visibility: visible;
      }
    }
  }
  .drag-area {
    display: flex;
    align-item: center;
    justify-content: center;
    width: 18px;
    height: 12px;
    .drag-icon {
      display: none;
      font-size: 12px;
      color: #979ba5;
      cursor: move;
    }
  }
  .name-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    padding-left: 18px;
    width: 150px;
  }
  .arrow-icon {
    position: absolute;
    top: 4px;
    left: 4px;
    font-size: 12px;
    color: #c4c6cc;
    transition: transform 0.2 ease-in-out;
    &.expanded {
      transform: rotate(90deg);
    }
  }
  .name-input {
    width: 131px;
  }
  .name-text {
    max-width: 130px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #63656e;
    font-size: 14px;
  }
  .hidden-icon {
    margin-left: 8px;
    color: #c4c6cc;
    font-size: 14px;
  }
  .opt-icons {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 2px 6px 2px 0;
    width: 42px;
    i {
      cursor: pointer;
      &:hover {
        color: #3a84ff;
      }
    }
    .save-icon {
      margin-right: 4px;
      font-size: 16px;
      color: #2dcb56;
      &:hover {
        color: #2dcb56;
      }
    }
    .close-icon {
      font-size: 14px;
      color: #c4c6cc;
      &.disabled {
        cursor: not-allowed;
      }
    }
    .add-icon {
      margin-right: 6px;
      font-size: 12px;
      color: #979ba5;
      visibility: hidden;
    }
    .more-icon {
      font-size: 16px;
      color: #979ba5;
      visibility: hidden;
    }
  }
}
.group-page-container {
  .name-wrapper {
    padding-left: 30px;
  }
}
.more-action {
  .action-item {
    padding: 0 12px;
    height: 32px;
    line-height: 32px;
    color: #63656e;
    cursor: pointer;
    &:hover {
      background: #f0f1f5;
      color: #3a84ff;
    }
    i {
      width: 12px;
      margin-right: 4px;
    }
  }
}
</style>
<style lang="postcss">
.more-actions-popover {
  .tippy-tooltip {
    padding: 0;
  }
}
</style>
