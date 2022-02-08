<template>
  <div class="form-field-edit">
    <div class="form-content-area">
      <bk-form ref="fieldForm" form-type="vertical" :rules="rules" :model="fieldData">
        <bk-form-item label="字段名称" property="name" :required="true">
          <bk-input v-model.trim="fieldData.name" :disabled="isCitedFromWorksheet" @change="handleNameChange">
          </bk-input>
        </bk-form-item>
        <bk-form-item label="唯一标识" property="key" :required="true">
          <bk-input v-model.trim="fieldData.key" :disabled="!isCreate || isCitedFromWorksheet"></bk-input>
        </bk-form-item>
        <bk-form-item label="字段类型" property="type" :required="true">
          <bk-select v-model="fieldData.type" :disabled="isCitedFromWorksheet" @change="handleTypeChange">
            <bk-option v-for="item in fieldProps.fieldTypeList" :key="item.type" :id="item.type" :name="item.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="计算类型" v-if="fieldData.type==='FORMULA'">
          <bk-radio-group v-model="meta.calculate_type">
            <bk-radio value="number">数值计算</bk-radio>
            <bk-radio value="date">时间日期</bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item label="计算公式" v-if="fieldData.type==='FORMULA'">
          <bk-select v-model="meta.type">
            <bk-option v-for="item in calculationFormula" :key="item.key" :id="item.key" :name="item.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="计算字段" v-if="fieldData.type==='FORMULA'">
          <bk-select v-model="meta.fields">
            <bk-option v-for="item in fieldProps.fieldTypeList" :key="item.type" :id="item.type" :name="item.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="单位" v-if="fieldData.type==='FORMULA'">
          <bk-input v-model="meta.affix" :clearable="true" :font-size="'medium'">
            <bk-dropdown-menu
              class="group-text"
              @show="dropdownShow"
              @hide="dropdownHide"
              ref="dropdown" slot="prepend"
              :font-size="'medium'">
              <bk-button type="primary" slot="dropdown-trigger">
                <span v-if="meta.affix_type === 0">前缀</span>
                <span v-if="meta.affix_type === 1">后缀</span>
                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li><a @click="triggerHandler(0)">前缀</a></li>
                <li><a @click="triggerHandler(1)">后缀</a></li>
              </ul>
            </bk-dropdown-menu>
          </bk-input>
        </bk-form-item>
        <bk-form-item label="保留小数位数" v-if="fieldData.type==='FORMULA'">
          <bk-input type="number" :max="1000" :min="0" v-model="meta.accuracy"></bk-input>
        </bk-form-item>
        <bk-form-item label="校验方式" :required="true" v-if="fieldData.type!=='FORMULA'">
          <bk-select
            v-model="fieldData.regex"
            :clearable="false"
            :searchable="true"
            :loading="regexListLoading"
            :disabled="
              isCitedFromWorksheet ||
              regexListLoading ||
              fieldData.source === 'TABLE' ||
              (fieldData.meta && fieldData.meta.code === 'APPROVE_RESULT')
            ">
            <bk-option v-for="option in regexList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          class="full-row-form"
          v-if="fieldProps.fieldsShowDefaultValue.includes(fieldData.type) && fieldData.source_type === 'CUSTOM'"
          label="默认值">
          <default-value
            :key="fieldData.type"
            :field="defaultData"
            :disabled="isCitedFromWorksheet"
            @change="handleDefaultValChange">
          </default-value>
        </bk-form-item>
        <template v-if="fieldProps.fieldsShowDataSource.includes(fieldData.type)">
          <bk-form-item class="full-row-form" v-if="fieldData.source_type === 'CUSTOM'" label="数据源">
            <bk-select
              class="data-source-type-select"
              :value="fieldData.source_type"
              :clearable="false"
              @selected="handleSelectSourceType">
              <bk-option v-for="item in sourceTypeList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
            </bk-select>
          </bk-form-item>
          <data-source
            ref="dataSource"
            class="field-data-source-container"
            :show-type-select="true"
            :source-type-list="sourceTypeList"
            :source-type="fieldData.source_type"
            :field-type="fieldData.type"
            :app-id="appId"
            :flow-id="field.workflow"
            :node-id="field.state"
            :value="sourceData"
            @sourceTypeChange="handleSelectSourceType"
            @change="handleDataSourceChange">
          </data-source>
        </template>
        <bk-form-item label="布局" :required="true">
          <bk-radio-group v-model="fieldData.layout">
            <bk-radio value="COL_6" :disabled="fieldProps.fieldsFullLayout.includes(fieldData.type)">半行</bk-radio>
            <bk-radio value="COL_12" :disabled="fieldProps.fieldsFullLayout.includes(fieldData.type)">整行</bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <bk-form-item label="是否必填" v-if="fieldData.type!=='FORMULA'">
          <bk-checkbox
            :disabled="fieldData.type === 'DESC' || (isCitedFromWorksheet && field.validate_type === 'REQUIRE')"
            :value="fieldData.validate_type === 'REQUIRE'"
            @change="handleRequireChange">
            必填
          </bk-checkbox>
          <span
            v-if="fieldData.validate_type === 'REQUIRE' && !fieldData.mandatory_conditions.connector"
            class="add-condition"
            @click="handleOpenConditionsPanel('mandatory_conditions')">
            <i class="bk-icon icon-plus-circle"></i>
            必填条件
          </span>
          <condition-group
            v-if="fieldData.validate_type === 'REQUIRE' && fieldData.mandatory_conditions.connector"
            :fields="fieldList"
            :fields-loading="fieldListLoading"
            :value="fieldData.mandatory_conditions"
            @delete="fieldData.mandatory_conditions = {}"
            @change="fieldData.mandatory_conditions = $event">
          </condition-group>
        </bk-form-item>
        <bk-form-item label="是否只读">
          <bk-checkbox
            :value="fieldData.is_readonly"
            :disabled="fieldData.type === 'DESC'"
            @change="handleReadOnlyChange">
            只读
          </bk-checkbox>
          <span
            v-if="fieldData.is_readonly && !fieldData.read_only_conditions.connector"
            class="add-condition"
            @click="handleOpenConditionsPanel('read_only_conditions')">
            <i class="bk-icon icon-plus-circle"></i>
            只读条件
          </span>
          <condition-group
            v-if="fieldData.is_readonly && fieldData.read_only_conditions.connector"
            :fields="fieldList"
            :fields-loading="fieldListLoading"
            :value="fieldData.read_only_conditions"
            @delete="fieldData.read_only_conditions = {}"
            @change="fieldData.read_only_conditions = $event">
          </condition-group>
        </bk-form-item>
        <bk-form-item label="是否隐藏">
          <bk-checkbox :value="!!fieldData.show_conditions.connector" @change="handleHideFieldChange">
            隐藏
          </bk-checkbox>
          <condition-group
            v-if="fieldData.show_conditions.connector"
            :fields="fieldList"
            :fields-loading="fieldListLoading"
            :show-delete-icon="false"
            :value="fieldData.show_conditions"
            @change="fieldData.show_conditions = $event">
          </condition-group>
        </bk-form-item>
        <bk-form-item label="字段描述">
          <bk-input v-model.trim="fieldData.desc" type="textarea" :rows="4" :disabled="isCitedFromWorksheet"></bk-input>
        </bk-form-item>
        <bk-form-item label="说明">
          <bk-input v-model.trim="fieldData.tips" type="textarea" :rows="4" :disabled="isCitedFromWorksheet"></bk-input>
        </bk-form-item>
      </bk-form>
    </div>
    <div class="slider-actions-area">
      <bk-button
        theme="primary"
        style="margin-right: 4px; min-width: 88px; text-align: center"
        :loading="fieldSavePending"
        @click="handleSave">
        确定
      </bk-button>
      <bk-button style="min-width: 88px; text-align: center" :disabled="fieldSavePending" @click="$emit('close')">
        取消
      </bk-button>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import pinyin from 'pinyin';
import {
  FIELDS_TYPES,
  FIELDS_SOURCE_TYPE,
  FIELDS_SHOW_DEFAULT_VALUE,
  FIELDS_SHOW_DATA_SOURCE,
  FIELDS_FULL_LAYOUT,
  CALCULATION_FORMULA,
} from '@/constants/forms.js';
import DefaultValue from '@/components/form/defaultValue.vue';
import DataSource from '@/components/form/dataSource/index.vue';
import ConditionGroup from './conditionGroup.vue';

export default {
  name: 'FormFieldEdit',
  components: {
    DefaultValue,
    DataSource,
    ConditionGroup,
  },
  props: {
    appId: String,
    flowId: Number,
    nodeId: Number,
    field: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      fieldData: cloneDeep(this.field),
      calculationFormula: CALCULATION_FORMULA,
      fieldProps: {
        fieldTypeList: FIELDS_TYPES.filter(item => item.type !== 'AUTO-NUMBER'),
        fieldsShowDefaultValue: FIELDS_SHOW_DEFAULT_VALUE,
        fieldsShowDataSource: FIELDS_SHOW_DATA_SOURCE,
        fieldsFullLayout: FIELDS_FULL_LAYOUT,
      },
      meta: {
        calculate_type: 'number',
        affix: '',
        affix_type: 0,
        fields: '',
        type: '',
        accuracy: 0,
      },
      isDropdownShow: false,
      defaultData: this.getDefaultData(this.field),
      regexList: [{ id: 'EMPTY', name: '无' }], // 校验方式列表，根据不同字段类型动态请求接口
      regexListLoading: false,
      fieldList: [], // 节点可获取变量列表
      fieldListLoading: false,
      fieldSavePending: false,
      rules: {
        name: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
        key: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
        type: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
    };
  },
  computed: {
    sourceTypeList() {
      if (this.fieldData.type === 'TABLE') {
        return FIELDS_SOURCE_TYPE.filter(item => item.id === 'CUSTOM');
      }
      return FIELDS_SOURCE_TYPE;
    },
    sourceData() {
      const { source_type, choice, meta, api_info, kv_relation } = this.fieldData;
      let data = {};
      switch (source_type) {
        case 'CUSTOM':
          data = choice;
          break;
        case 'API':
          data = { api_info, kv_relation };
          break;
        case 'WORKSHEET':
          data = meta.data_config;
          break;
      }
      return data;
    },
    isCitedFromWorksheet() {
      return this.field.meta && 'worksheet' in this.field.meta && 'id' in this.field.meta.worksheet;
    },
    isCreate() {
      return !('id' in this.field);
    },
  },
  created() {
    if (this.fieldData.type) {
      this.getRegexList();
    }
    this.getFieldList();
  },
  methods: {
    async getRegexList() {
      try {
        this.regexListLoading = true;
        const params = {
          type: this.fieldData.type,
        };
        const resp = await this.$store.dispatch('setting/getRegexList', params);
        this.regexList = resp.data.regex_choice.map((item) => {
          const [id, name] = item;
          return { id, name: name === '' ? '无' : name };
        });
      } catch (e) {
        console.error(e);
      } finally {
        this.regexListLoading = false;
      }
    },
    // 获取节点可使用变量
    async getFieldList() {
      try {
        this.fieldListLoading = true;
        const res = await this.$store.dispatch('setting/getNodeVars', {
          workflow: this.flowId,
          state: this.nodeId,
        });
        this.fieldList = res.data.map((item) => {
          const { key, name, type } = item;
          return { key: `\${params_${key}}`, name, type };
        });
      } catch (e) {
        console.error(e);
      } finally {
        this.fieldListLoading = false;
      }
    },
    getDefaultData(field) {
      const { type, default: defaultVal, choice } = field;
      let dftVal;
      if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(type)) {
        dftVal = defaultVal ? defaultVal.split(',') : [];
      } else {
        dftVal = cloneDeep(defaultVal);
      }
      return {
        type,
        choice,
        value: dftVal,
        multiple: ['MULTISELECT', 'CHECKBOX'].includes(type),
      };
    },
    getDefaultChoice(type) {
      if (['SELECT', 'INPUTSELECT', 'MULTISELECT', 'CHECKBOX', 'RADIO', 'TABLE'].includes(type)) {
        return [
          { key: 'XUANXIANG1', name: '选项1' },
          { key: 'XUANXIANG2', name: '选项2' },
        ];
      }
      return [];
    },
    handleNameChange(val) {
      if (this.isCreate) {
        const key = pinyin(val, {
          style: pinyin.STYLE_NORMAL,
          heteronym: false,
        })
          .join('_')
          .toUpperCase();
        this.fieldData.key = key;
      }
    },
    handleTypeChange(val) {
      if (val === 'FORMULA') {
        this.fieldData.is_readonly = true;
      }
      const field = this.fieldProps.fieldTypeList.find(item => item.type === val);
      const defaultVal = ['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS', 'TABLE'].includes(val)
        ? ''
        : cloneDeep(field.default);
      this.getRegexList();
      this.fieldData.choice = this.getDefaultChoice(val);
      this.fieldData.default = defaultVal;
      this.defaultData = this.getDefaultData(this.fieldData);
    },
    // 修改默认值
    handleDefaultValChange(val) {
      this.fieldData.default = ['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(this.fieldData.type)
        ? val.join(',')
        : cloneDeep(val);
    },
    // 切换数据源
    handleSelectSourceType(val) {
      this.fieldData.source_type = val;
      if (val === 'CUSTOM') {
        this.fieldData.choice = [
          { key: 'XUANXIANG1', name: '选项1' },
          { key: 'XUANXIANG2', name: '选项2' },
        ];
        this.fieldData.api_info = {};
        this.fieldData.kv_relation = {};
      } else if (val === 'API') {
        this.fieldData.choice = [];
        this.fieldData.api_info = {
          remote_api_id: '',
          remote_system_id: '',
          req_body: {},
          req_params: {},
          rsp_data: '',
        };
        this.fieldData.kv_relation = { key: '', name: '' };
      } else if (val === 'WORKSHEET') {
        this.fieldData.choice = [];
        this.fieldData.api_info = {};
        this.fieldData.kv_relation = {};
        this.fieldData.meta.data_config = {
          field: '',
          source: {
            project_key: this.appId,
          },
          target: {
            project_key: this.appId,
            worksheet_id: '',
          },
          conditions: {
            connector: '',
            expressions: [],
          },
        };
      }
    },
    // 数据源配置更新
    handleDataSourceChange(val) {
      console.log(val);
      const { source_type } = this.fieldData;
      if (source_type === 'CUSTOM') {
        this.fieldData.choice = val;
      } else if (source_type === 'API') {
        this.fieldData.api_info = val.api_info;
        this.fieldData.kv_relation = val.kv_relation;
      } else if (source_type === 'WORKSHEET') {
        this.fieldData.meta.data_config = val;
      }
    },
    // 切换是否必填
    handleRequireChange(val) {
      this.fieldData.validate_type = val ? 'REQUIRE' : 'OPTION';
      if (!val) {
        this.fieldData.mandatory_conditions = {};
      }
    },
    // 切换是否必填
    handleReadOnlyChange(val) {
      this.fieldData.is_readonly = val;
      if (!val) {
        this.fieldData.read_only_conditions = {};
      }
    },
    // 切换是否隐藏
    handleHideFieldChange(val) {
      if (val) {
        this.handleOpenConditionsPanel('show_conditions');
      } else {
        this.fieldData.show_conditions = {};
      }
    },
    // 打开添加条件面板
    handleOpenConditionsPanel(key) {
      this.fieldData[key] = { connector: '', expressions: [] };
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(env) {
      this.$refs.dropdown.hide();
      this.meta.affix_type = env;
    },
    handleSave() {
      this.fieldSavePending = true;
      this.$refs.fieldForm
        .validate()
        .then(async () => {
          try {
            const {
              id,
              state,
              workflow,
              name,
              key,
              type,
              regex,
              layout,
              desc,
              source_type,
              tips,
              choice,
              meta,
              api_info,
              kv_relation,
              validate_type, // 必填
              mandatory_conditions, // 必填条件
              is_readonly, // 只读
              read_only_conditions, // 只读条件
              show_conditions, // 隐藏条件
              default: defaultVal,
            } = this.fieldData;
            const action = this.isCreate ? 'createNodeField' : 'updateNodeField';
            const params = {
              id,
              state,
              workflow,
              name,
              key,
              type,
              regex,
              layout,
              validate_type,
              is_readonly,
              desc,
              source_type,
              tips,
              choice,
              meta: type === 'FORMULA' ? this.meta : meta,
              api_info,
              kv_relation,
              mandatory_conditions,
              read_only_conditions,
              show_conditions,
              default: defaultVal,
            };
            const res = await this.$store.dispatch(`setting/${action}`, params);
            this.$emit('save', this.isCreate ? 'add' : 'update', res.data);
          } catch (e) {
            console.error(e);
          } finally {
            this.fieldSavePending = false;
          }
        })
        .catch(() => {
          this.fieldSavePending = false;
        });
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../../../../../css/scroller.css';

.form-field-edit {
  .form-content-area {
    padding-bottom: 24px;
    height: calc(100% - 48px);
    overflow: auto;
    @mixin scroller;

    .bk-form::after {
      display: none;
    }
  }

  .bk-form {
    display: flex;
    flex-flow: wrap;
    justify-content: space-between;
    margin: 0 auto;
    width: 880px;

    .bk-form-item {
      margin-top: 24px;
      width: 428px;

      &.full-row-form {
        width: 100%;
      }
    }
  }

  .data-source-type-select {
    width: calc(50% - 18px);
  }

  .field-data-source-container {
    margin-top: 20px;
    width: 100%;
  }

  .add-condition {
    display: inline-flex;
    align-items: center;
    color: #3a84ff;
    font-size: 14px;
    cursor: pointer;

    & > i {
      margin: 0 6px 0 20px;
      font-size: 18px;
    }
  }

  .condition-group {
    margin-top: 6px;
  }

  .slider-actions-area {
    padding: 0 24px;
    height: 48px;
    line-height: 48px;
    background: #fafbfd;
  }
}
</style>
