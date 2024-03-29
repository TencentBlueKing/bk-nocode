<template>
  <div class="worksheet-data-wrapper">
    <bk-form ref="sourceForm" class="select-worksheet" form-type="vertical" :model="localVal" :rules="sourceRules">
      <bk-form-item v-if="changeSource" label="数据源" :required="true">
        <bk-select value="WORKSHEET" :clearable="false" @change="$emit('sourceTypeChange', $event)">
          <bk-option v-for="item in sourceTypeList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="表单" property="target" :required="true">
        <bk-select
          placeholder="请选择表单"
          :value="localVal.target.worksheet_id"
          :clearable="false"
          :disabled="formListLoading"
          :loading="formListLoading"
          @selected="handleSelectForm">
          <bk-option v-for="item in formList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="字段" property="field" :required="true">
        <bk-select
          v-model="localVal.field"
          placeholder="请选择字段"
          :clearable="false"
          :disabled="fieldListLoading"
          :loading="fieldListLoading"
          @selected="update">
          <bk-option v-for="item in fieldList" :key="item.key" :id="item.key" :name="item.name"></bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
    <div class="filter-rules-wrapper">
      <div class="connector-rule">
        <label>筛选条件</label>
        <bk-radio-group v-model="localVal.conditions.connector" @change="update">
          <bk-radio value="and">且</bk-radio>
          <bk-radio value="or">或</bk-radio>
        </bk-radio-group>
      </div>
      <div v-if="localVal.conditions.expressions && localVal.conditions.expressions.length > 0" class="condition-list">
        <div class="condition-item" v-for="(expression, index) in localVal.conditions.expressions" :key="index">
          <bk-select
            v-model="expression.key"
            placeholder="字段"
            style="width: 160px; margin-right: 8px"
            :clearable="false"
            @selected="handleSelectField(expression)">
            <bk-option v-for="item in fieldList" :key="item.key" :id="item.key" :name="item.name"></bk-option>
          </bk-select>
          <bk-select
            v-model="expression.condition"
            placeholder="逻辑"
            style="width: 100px; margin-right: 8px"
            :clearable="false"
            @selected="update">
            <bk-option
              v-for="item in getConditionOptions(expression.key)"
              :key="item.id"
              :id="item.id"
              :name="item.name">
            </bk-option>
          </bk-select>
          <bk-select
            v-if="useVariable"
            v-model="expression.type"
            placeholder="值类型"
            style="width: 100px; margin-right: 8px"
            :clearable="false"
            @selected="handleSelectType(expression)">
            <bk-option id="const" name="值"></bk-option>
            <bk-option id="field" name="引用变量"></bk-option>
          </bk-select>
          <bk-select
            v-if="expression.type === 'field'"
            v-model="expression.value"
            placeholder="选择变量"
            style="width: 140px"
            :clearable="false"
            :loading="relationListLoading"
            :disabled="relationListLoading"
            @selected="update">
            <bk-option v-for="item in relationList" :key="item.key" :id="item.key" :name="item.name"></bk-option>
          </bk-select>
          <field-value
            v-else
            :style="{ width: useVariable ? '140px' : '250px' }"
            :field="getField(expression.key)"
            :value="expression.value"
            @change="handleValChange(expression, $event)">
          </field-value>
          <div class="operate-btns" style="margin-left: 8px">
            <i class="custom-icon-font icon-add-circle" @click="handleAddExpression(index)"></i>
            <i class="custom-icon-font icon-reduce-circle" @click="handleDeleteExpression(index)">
            </i>
          </div>
        </div>
        <p v-if="errorTips" class="common-error-tips">请检查筛选条件</p>
      </div>
      <div v-else class="data-empty" @click="handleAddExpression(0)">点击添加</div>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import { getFieldConditions } from '@/utils/form.js';
import FieldValue from '@/components/form/fieldValue.vue';

export default {
  name: 'WorksheetData',
  components: {
    FieldValue,
  },
  props: {
    appId: String,
    changeSource: {
      type: Boolean,
      default: false,
    },
    useVariable: {
      // 参数值是否支持引用变量
      type: Boolean,
      default: false,
    },
    sourceTypeList: {
      type: Array,
      default: () => [],
    },
    flowId: Number,
    nodeId: Number,
    value: Object,
  },
  data() {
    return {
      localVal: cloneDeep(this.value),
      formList: [],
      formListLoading: false,
      fieldList: [],
      fieldListLoading: false,
      relationList: [],
      relationListLoading: false,
      errorTips: false,
      sourceRules: {
        target: [
          {
            validator(val) {
              return typeof val.worksheet_id === 'number';
            },
            message: '必填项',
            trigger: 'blur',
          },
        ],
        field: [
          {
            required: true,
            trigger: 'blur',
            message: '必填项',
          },
        ],
      },
    };
  },
  watch: {
    value(val) {
      this.localVal = cloneDeep(val);
    },
  },
  created() {
    this.getFormList();
    if (this.value.target.worksheet_id) {
      this.getFieldList();
    }
    if (this.useVariable) {
      this.getRelationList();
    }
  },
  methods: {
    async getFormList() {
      try {
        this.formListLoading = true;
        const params = {
          project_key: this.appId,
          page_size: 10000,
        };
        const res = await this.$store.dispatch('setting/getFormList', params);
        this.formList = res.data.items;
        this.formListLoading = false;
      } catch (e) {
        console.error(e);
      }
    },
    async getFieldList() {
      try {
        this.fieldListLoading = true;
        const res = await this.$store.dispatch('setting/getFormFields', this.localVal.target.worksheet_id);
        this.fieldList = res.data;
        this.fieldListLoading = false;
      } catch (e) {
        console.error(e);
      }
    },
    async getRelationList() {
      try {
        this.relationListLoading = true;
        const params = {
          workflow: this.flowId,
          state: this.nodeId,
        };
        const res = await this.$store.dispatch('setting/getNodeVars', params);
        this.relationList = res.data.map(item => {
          const { key, name } = item;
          return { key: `\${params_${key}}`, name };
        });
      } catch (e) {
        console.error(e);
      } finally {
        this.relationListLoading = false;
      }
    },
    // 筛选条件字段逻辑选项，不同类型的字段有不同的逻辑关系
    getConditionOptions(key) {
      if (key) {
        const field = this.fieldList.find(i => i.key === key);
        return field ? getFieldConditions(field.type) : [];
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
    // 选择表单，清空已选数据
    handleSelectForm(val) {
      this.localVal = {
        field: '',
        source: {
          project_key: this.appId,
        },
        target: {
          project_key: this.appId,
          worksheet_id: val,
        },
        conditions: {
          connector: '',
          expressions: [],
        },
      };
      this.getFieldList();
      this.update();
    },
    // 选择筛选条件字段
    handleSelectField(expression) {
      expression.condition = '';
      expression.type = this.useVariable ? '' : 'const';
      expression.value = '';
      this.update();
    },
    // 选择字段值类型
    handleSelectType(expression) {
      expression.value = '';
      this.update();
    },
    // 选择引用变量
    handleSelectRelation() {
      this.update();
    },
    handleValChange(expression, val) {
      expression.value = val;
      this.update();
    },
    // 增加筛选条件
    handleAddExpression(index) {
      this.localVal.conditions.expressions.splice(index + 1, 0, {
        key: '',
        condition: '',
        type: this.useVariable ? '' : 'const',
        value: '',
      });
    },
    // 删除筛选条件
    handleDeleteExpression(index) {
      this.localVal.conditions.expressions.splice(index, 1);
    },
    update() {
      this.$emit('update', cloneDeep(this.localVal));
    },
    validate() {
      this.$refs.sourceForm.validate();
      const sourceFormValid = this.localVal.target.worksheet_id && this.localVal.field;
      const filterRuleValid = this.localVal.conditions.expressions.every(exp => {
        const { key, condition, type, value } = exp;
        return key !== '' && condition !== '' && type !== '' && value !== '';
      });
      this.errorTips = !filterRuleValid;
      return sourceFormValid && filterRuleValid;
    },
  },
};
</script>
<style lang="postcss" scoped>
.worksheet-data-wrapper {
  .select-worksheet {
    display: flex;
    align-items: center;
    .bk-form-item {
      margin-top: 0;
      flex: 1;
      &:not(:last-of-type) {
        margin-right: 10px;
      }
    }
  }
  .filter-rules-wrapper {
    margin-top: 24px;
  }
  .connector-rule {
    display: flex;
    align-items: center;
    height: 20px;
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
  .condition-item {
    display: flex;
    align-items: center;
    margin-top: 16px;
    .operate-btns {
      color: #c4c6cc;
      cursor: pointer;
      user-select: none;
      .disabled {
        color: #dcdee5;
        cursor: not-allowed;
      }
    }
  }
  .data-empty {
    margin-top: 16px;
    padding: 24px 0;
    font-size: 12px;
    text-align: center;
    color: #dcdee5;
    border: 1px dashed #dcdee5;
    cursor: pointer;
    &:not(.disabled):hover {
      border-color: #3a84ff;
      color: #3a84ff;
    }
    &.disabled {
      cursor: not-allowed;
    }
  }
}
</style>
