<template>
  <div class="app-selector">
    <bk-popover
      ext-cls="app-selector-popover"
      placement="bottom"
      :disabled="disabled"
      :tippy-options="{ arrow: false, theme: 'light', distance: 0, trigger: 'click' }"
      :on-show="onPopoverOpen"
      :on-hide="onPopoverClose">
      <div class="app-info-area">
        <template v-if="crtApp">
          <div class="logo" :style="{ background: `linear-gradient(90deg, ${crtApp.color[0]}, ${crtApp.color[1]})` }">
            {{ crtApp.logo }}
          </div>
          <template v-if="!simple">
            <div class="name">{{ crtApp.name }}</div>
            <i :class="['arrow-icon', 'bk-icon', 'icon-down-shape', { opened: popoverOpen }]"></i>
          </template>
        </template>
        <bk-spin v-if="loading" class="app-loading-icon" size="mini"></bk-spin>
      </div>
      <div class="app-select-panel" slot="content">
        <div class="search-input">
          <bk-input
            v-model.trim="searchStr"
            behavior="simplicity"
            right-icon="bk-icon icon-search"
            :clearable="true"
            @clear="searchStr = ''">
          </bk-input>
        </div>
        <div class="app-list" v-if="listInPanel.length > 0">
          <div
            v-for="item in listInPanel"
            :class="['app-item', { selected: crtApp && crtApp.key === item.key }]"
            :key="item.key"
            @click="onSelectApp(item)">
            {{ item.name }}
          </div>
        </div>
        <div v-else class="app-empty">暂无数据</div>
        <div class="extend-area" @click="$router.push({ name: 'applicationList' })">
          <i class="custom-icon-font icon-app-store"></i>
          <span>应用中心</span>
        </div>
      </div>
    </bk-popover>
  </div>
</template>
<script>
export default {
  name: 'AppSelector',
  props: {
    list: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    simple: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    value: String,
  },
  data() {
    return {
      crtApp: this.getCrtApp(this.value),
      popoverOpen: false,
      searchStr: '',
    };
  },
  computed: {
    listInPanel() {
      if (this.searchStr) {
        return this.list.filter((item) => {
          console.log(
            item.name.toLowerCase(),
            this.searchStr.toLowerCase(),
            item.name.toLowerCase().includes(this.searchStr.toLowerCase())
          );
          return item.name.toLowerCase().includes(this.searchStr.toLowerCase());
        });
      }
      return this.list;
    },
  },
  watch: {
    list() {
      this.crtApp = this.getCrtApp(this.value);
    },
    value(val) {
      this.crtApp = this.getCrtApp(val);
    },
  },
  methods: {
    getCrtApp(val) {
      return this.list.find(item => item.key === val);
    },
    onPopoverOpen() {
      this.popoverOpen = true;
    },
    onPopoverClose() {
      this.popoverOpen = false;
    },
    onSelectApp(app) {
      this.crtApp = app;
      this.$emit('change', app);
    },
  },
};
</script>
<style lang="postcss" scoped>
.app-selector {
  width: 100%;
  background: #ffffff;
  box-shadow: 0 1px 0 0 #f0f1f5;
  cursor: pointer;
  .bk-tooltip {
    display: block;
    /deep/ .bk-tooltip-ref {
      display: block;
    }
  }
}
.app-info-area {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 0 22px;
  width: 100%;
  height: 52px;
}
.logo {
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  font-size: 12px;
  border-radius: 50%;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.8);
}
.name {
  padding: 0 4px;
  width: calc(100% - 50px);
  font-size: 14px;
  color: #63656e;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.arrow-icon {
  font-size: 14px;
  color: #c4c6cc;
  transition: all ease-in-out 0.2s;
  &.opened {
    transform: rotate(-180deg);
  }
}
.app-loading-icon {
  position: absolute;
  top: 18px;
  right: 10px;
}
.search-input {
  padding: 0 10px;
}
.app-select-panel {
  width: 260px;
}
.app-list {
  padding: 6px 0;
  background: #ffffff;
  max-height: 238px;
  overflow: auto;
  .app-item {
    padding: 0 10px;
    height: 32px;
    line-height: 32px;
    color: #63656e;
    font-size: 12px;
    cursor: pointer;
    &.selected {
      background: #eaf3ff;
      color: #3a84ff;
    }
    &:hover {
      background: #F0F1F5;
    }
  }
}
.app-empty {
  height: 200px;
  line-height: 160px;
  font-size: 12px;
  color: #63656e;
  text-align: center;
}
.extend-area {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  font-size: 12px;
  color: #63656e;
  background: #fafbfd;
  border-top: 1px solid #dcdee5;
  cursor: pointer;
  &:hover {
    color: #3a84ff;
  }
  i {
    margin-right: 4px;
    font-size: 16px;
  }
}
</style>
<style lang="postcss">
.tippy-popper.app-selector-popover {
  background: #ffffff;
  .tippy-tooltip {
    padding: 0;
    border: 1px solid #dcdee5;
    box-shadow: -2px 2px 4px #dcdee5, 2px 2px 2px #dcdee5;
  }
}
</style>
