<template>
  <div class="form-container">
    <bk-form
      ref="cardForm"
      :label-width="200"
      form-type="vertical"
      :rules="rules"
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
      <bk-form-item
        label="工作表绑定"
        v-show="configData.option==='TABLE'"
        property="workSheetId"
        :required="true"
        :error-display-type="'normal'">
        <bk-select v-model="configData.workSheetId" @selected="change">
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
      <bk-form-item label="时间筛选" v-show="configData.option==='TABLE'">
        <bk-select v-model="localTimeRange" @selected="handleSelectTime">
          <bk-option
            v-for="list in timeRangeList "
            :key="list.id"
            :id="list.id"
            :name="list.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="排序规则" v-show="configData.option==='TABLE'">
        <bk-select v-model="localSortBy" @selected="handleSelectSort">
          <bk-option
            v-for="list in sortList"
            :key="list.id"
            :id="list.id"
            :name="list.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="数据筛选" v-show="configData.option==='TABLE'" ext-cls="data-filter">
        <div class="data-switch">
          <bk-switcher v-model="isDataFilter" size="small" theme="primary" @change="handleChangeStatus"></bk-switcher>
        </div>
        <div class="rule-config" @click="handleRuleConfig" v-if="isDataFilter">配置规则</div>
      </bk-form-item>
    </bk-form>
    <bk-dialog
      title="配置规则"
      v-model="dialog.visible"
      theme="primary"
      :mask-close="false"
      :header-position="dialog.position"
      :width="dialog.width"
      :confirm-fn="handleConfirm"
      :on-close="handleCancel">
      <div class="dialog-container">
        <div>表格将展示满足以下条件的数据</div>
        <div class="connector-rule">
          <label>筛选条件</label>
          <bk-radio-group v-model="localVal.connector">
            <bk-radio value="and">且</bk-radio>
            <bk-radio value="or">或</bk-radio>
          </bk-radio-group>
        </div>
        <div class="condition-item">
          <div style="width: 160px; margin-right: 8px">字段名称</div>
          <div style="width: 140px">筛选逻辑</div>
        </div>
        <div class="condition-item" :key="index" v-for="(expression, index) in localVal.expressions">
          <bk-select
            v-model="expression.key"
            placeholder="字段"
            style="width: 160px; margin-right: 8px"
            @selected="handleSelectField(expression)"
            :clearable="false">
            <bk-option v-for="item in fieldList" :key="item.key" :id="item.key" :name="item.name"></bk-option>
          </bk-select>
          <bk-select
            v-model="expression.condition"
            placeholder="逻辑"
            style="width: 100px; margin-right: 8px"
            :clearable="false">
            <bk-option
              v-for="item in getConditionOptions(expression.key)"
              :key="item.id"
              :id="item.id"
              :name="item.name">
            </bk-option>
          </bk-select>
          <field-value
            :style="{ width: '140px' }"
            :field="getField(expression.key)"
            :value="expression.value"
            @change="handleValChange(expression, $event)">
          </field-value>
          <div class="operate-btns" style="margin-left: 8px">
            <i class="custom-icon-font icon-add-circle" @click="handleAddExpression(index)"></i>
            <i :class="['custom-icon-font', 'icon-reduce-circle',
            { disabled: localVal.expressions.length < 2 }]" @click="handleDeleteExpression(index)"></i>
          </div>
        </div>
        <p v-if="errorTips" class="common-error-tips">请检查筛选条件</p>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
import Bus from '@/utils/bus.js';
import cloneDeep from 'lodash.clonedeep';
import { getFieldConditionsInTablePage } from '@/utils/form.js';
import FieldValue from '@/components/form/fieldValue.vue';
import { FIELDS_FILTER_CONFIG } from '@/constants/forms.js';
import { TIME_RANGE, SORT_LIST } from '@/constants/sysField.js';


export default {
  name: 'AttributeForm',
  components: {
    FieldValue,
  },
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
    timeRange: String,
    sortBy: String,
    conditions: {
      type: Object,
      default: () => ({}),
    },
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
      sortList: SORT_LIST,
      localTimeRange: cloneDeep(this.timeRange),
      localSortBy: cloneDeep(this.sortBy),
      timeRangeList: TIME_RANGE,
      dataPermission: [{
        id: 0, name: '全部可见',
      }, {
        id: 1, name: '仅本人创建的',
      }],
      rules: {
        workSheetId: [{
          required: true,
          message: '工作表绑定为必填项',
          trigger: 'blur',
        }],
      },
      isDataFilter: '',
      buttonDetail: {},
      dialog: {
        visible: false,
        position: 'left',
        width: '560',
      },
      localVal: cloneDeep(this.conditions),
      // expression: {condition: '', key: "", value: ''},
      relationList: [],
      fieldList: [],
      errorTips: false,
      relationListLoading: false,
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
    conditions(val) {
      this.localVal = cloneDeep(val);
      !val.connector ?  this.isDataFilter = false : this.isDataFilter = true;
    },
    timeRange(val) {
      this.localTimeRange = cloneDeep(val);
    },
    sortBy(val) {
      this.localSortBy = cloneDeep(val);
    },
    functionList(val) {
      console.log(val);
    },
  },
  mounted() {
    // 选中按钮
    Bus.$on('selectFunction', (val) => {
      this.configData = { ...val };
    });
    !this.conditions.connector ?  this.isDataFilter = false : this.isDataFilter = true;
  },
  beforeDestroy() {
    Bus.$off('selectFunction');
  },
  methods: {
    async getFieldList() {
      try {
        this.fieldListLoading = true;
        const res = await this.$store.dispatch('setting/getFormFields', this.configData.workSheetId);
        this.fieldList = res.data.filter(item => !FIELDS_FILTER_CONFIG.includes(item.type));
      } catch (e) {
        console.error(e);
      } finally {
        this.fieldListLoading = false;
      }
    },
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
    handleRuleConfig() {
      if (!this.configData.workSheetId) {
        this.$bkMessage({
          theme: 'warning',
          message: '请选择工作表',
        });
        return;
      }
      this.dialog.visible = true;
      this.errorTips = false;
      this.getFieldList();
    },
    handleAddExpression(index) {
      this.localVal.expressions.splice(index + 1, 0, {
        key: '',
        condition: '',
        value: '',
        type: 'const',
      });
    },
    // 删除筛选条件
    handleDeleteExpression(index) {
      if (this.localVal.expressions.length > 1) {
        this.localVal.expressions.splice(index, 1);
      }
    },
    // 筛选条件字段逻辑选项，不同类型的字段有不同的逻辑关系
    getConditionOptions(key) {
      if (key) {
        const field = this.fieldList.find(i => i.key === key);
        return field ? getFieldConditionsInTablePage(field.type) : [];
      }
      return [];
    },
    // 筛选条件字段
    getField(key) {
      if (key) {
        return this.fieldList.find(item => item.key === key);
      }
      return {};
    },
    handleValChange(expression, val) {
      expression.value = val;
    },
    handleConfirm() {
      if (!this.localVal.connector) {
        this.errorTips = true;
        return;
      }
      Bus.$emit('sendConfigRules', this.localVal);
      this.dialog.visible = false;
    },
    handleSelectTime(val) {
      Bus.$emit('sendTimeRange', val);
    },
    handleSelectSort(val) {
      Bus.$emit('sendSortRule', val);
    },
    handleCancel() {
      this.dialog.visible = false;
    },
    handleChangeStatus(val) {
      if (!val) {
        this.localVal = { connector: '', expressions: [{ condition: '', key: '', value: '', type: 'const' }] };
        Bus.$emit('sendConfigRules', {});
      }
    },
    handleSelectField(expression) {
      expression.condition = '';
      expression.value = '';
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../css/scroller.css";

.form-container {
  width: 272px;
  margin-left: 24px;
}

.rule-config {
  font-size: 14px;
  color: #3a84ff;

  &:hover {
    cursor: pointer;
  }
}

.condition-item {
  display: flex;
  align-items: center;
  margin-top: 16px;

  .operate-btns {
    color: #c4c6cc;
    cursor: pointer;
    user-select: none;

    i {
      color: #c4c6cc;
      cursor: pointer;

      &:hover {
        color: #979ba5;
      }

      &.disabled {
        color: #dcdee5;
        cursor: not-allowed;
      }
    }
  }
}

.connector-rule {
  display: flex;
  align-items: center;
  height: 20px;
  margin-top: 16px;

  & > label {
    position: relative;
    margin-right: 30px;
    color: #63656e;
    font-size: 14px;
    white-space: nowrap;

    &:after {
      content: '*';
      position: absolute;
      top: 50%;
      height: 8px;
      line-height: 1;
      color: #ea3636;
      font-size: 12px;
      transform: translate(3px, -50%);
    }
  }
}


.dialog-container {
  max-height: 512px;
  overflow: auto;
  @mixin scroller;
}
.data-filter{
  position: relative;
  .data-switch{
    position: absolute;
    right: 0;
    top: -32px;
  }
}
</style>
