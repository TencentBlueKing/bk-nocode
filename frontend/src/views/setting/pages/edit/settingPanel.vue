<template>
  <div class="setting-panel">
    <div class="panel-title">
      <span>组件属性</span>
    </div>
    <div class="config-wrapper">
      <page-edit
        v-if="page.type"
        :page="configData"
        :type="configData.type"
        @change="$emit('update', $event)">
      </page-edit>
    </div>
  </div>
</template>

<script>
import pageEdit from './pageEdit.vue';
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'SettingPanel',
  components: { pageEdit },
  props: {
    page: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      configData: cloneDeep(this.page),
    };
  },
  watch: {
    page: {
      handler(val) {
        this.configData = cloneDeep(val);
      },
      deep: true,
    },
  },
};
</script>

<style scoped lang="postcss">
.setting-panel {
  position: relative;
  width: 320px;
  height: calc(100% - 56px);
  background: #ffffff;
  z-index: 1;
  flex-shrink: 0;
}

.panel-title {
  padding: 8px 24px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  color: #313238;
  background: #ffffff;
  border-top: 1px solid #dcdee5;
  border-bottom: 1px solid #dcdee5;
  display: flex;
  align-items: center;
}
.config-wrapper {
  padding: 16px 24px;
  height: calc(100% - 40px);
  overflow-x: hidden;
}
</style>
