<template>
  <div class="form-container">
    <bk-form
      ref="cardForm"
      :label-width="200"
      form-type="vertical"
      :model="configData">
      <bk-form-item label="功能绑定" :property="'functionBind'" v-show="configData.option!=='TABLE'">
        <bk-select v-model="configData.value" @change="change">
          <bk-option
            v-for="func in funcList"
            :key="func.id"
            :id="func.id"
            :name="func.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="工作表绑定" v-show="configData.option==='TABLE'">
        <bk-select v-model="configData.workSheetId" @change="change">
          <bk-option
            v-for="list in workSheetList"
            :key="list.id"
            :id="list.id"
            :name="list.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="数据可见范围" v-show="configData.option==='TABLE'">
        <bk-select v-model="configData.showMode" @change="change">
          <bk-option
            v-for="list in dataPermission"
            :key="list.id"
            :id="list.id"
            :name="list.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="按钮名称" v-show="configData.option!=='TABLE'">
        <bk-input v-model="configData.name" placeholder="请输入按钮名称" @change="change"></bk-input>
      </bk-form-item>
    </bk-form>
  </div>
</template>
<script>
import Bus from '@/utils/bus.js';
import cloneDeep from 'lodash.clonedeep';

export default {

  name: 'AttributeForm',
  props: {
    group: {
      type: String,
      default: 'FUNCTION',
    },
    functionList: {
      type: Array,
      default: () => [],
    },
    workSheetList: {
      type: Array,
      default: () => [],
    },
    workSheetId: [Number, String],
    showMode: [Number, String],
  },
  data() {
    return {
      configData: {
        workSheetId: cloneDeep(this.workSheetId),
        value: '',
        name: '',
        option: 'TABLE',
        type: '',
        showMode: cloneDeep(this.showMode),
      },
      dataPermission: [{
        id: 0, name: '全部可见',
      },
      {
        id: 1, name: '仅本人创建的',
      }],
      buttonDetail: {},
    };
  },
  computed: {
    funcList() {
      return this.configData.option === 'HEADER'
        ? this.functionList.filter(item => !['EDIT', 'DETAIL'].includes(item.type))
        : this.functionList.filter(item => ['EDIT', 'DELETE', 'DETAIL'].includes(item.type));
    },
  },
  watch: {
    workSheetId(val) {
      this.configData.workSheetId = val;
    },
    showMode(val) {
      this.configData.showMode = val;
    },
  },
  mounted() {
    // 选中按钮
    Bus.$on('selectFunction', (val) => {
      this.configData = { ...val };
    });
  },
  beforeDestroy() {
    Bus.$off('selectFunction');
  },
  methods: {
    change() {
      if (this.configData.value) {
        const { value } = this.configData;
        this.functionList.forEach((item) => {
          if (item.id === value) {
            this.configData.type = item.type;
          }
        });
      }
      Bus.$emit('sendFormData', this.configData);
    },
  },
};
</script>

<style scoped lang="postcss">
.form-container {
  width: 272px;
  margin-left: 24px;
}
</style>
