<template>
  <div class="config-panel">
    <div class="panel-title">{{ fieldType[configData.type] }}</div>
    <div class="config-wrapper">
      <field-edit v-if="field.type" v-model="configData" :app-id="appId" :list="list" @change="$emit('update', $event)">
      </field-edit>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import FieldEdit from './fieldEdit.vue';
import { FIELDS_TYPES_MAPS } from '@/constants/fromTypeMap.js';

export default {
  name: 'ConfigPanel',
  components: {
    FieldEdit,
  },
  props: {
    appId: String,
    field: {
      type: Object,
      default: () => ({}),
    },
    list: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      configData: cloneDeep(this.field),
      fieldType: FIELDS_TYPES_MAPS,
    };
  },
  watch: {
    field(val) {
      this.configData = cloneDeep(val);
    },
  },
};
</script>
<style lang="postcss" scoped>
.config-panel {
  position: relative;
  width: 320px;
  height: 100%;
  background: #ffffff;
  z-index: 1;
}
.panel-title {
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  color:#313238 ;
  background: #ffffff;
  border-top: 1px solid #dcdee5;
  border-bottom: 1px solid #dcdee5;
}
.config-wrapper {
  padding: 16px 24px;
  height: calc(100% - 40px);
  overflow: auto;
}
</style>
