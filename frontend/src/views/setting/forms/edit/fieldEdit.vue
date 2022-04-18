<template>
  <div class="field-edit">
    <bk-form form-type="vertical">
      <bk-form-item label="字段名称">
        <bk-input v-model.trim="fieldData.name" @change="change" @blur="onNameBlur"></bk-input>
      </bk-form-item>
      <!--   计算控件的配置   -->
      <template v-if="fieldData.type==='FORMULA'">
        <bk-form-item label="计算类型">
          <bk-radio-group v-model="fieldData.meta.config.calculate_type" @change="handleChangeType">
            <bk-radio value="number">数值计算</bk-radio>
            <bk-radio value="date">时间日期</bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <template v-if="fieldData.meta.config.calculate_type==='number'">
          <bk-form-item label="计算公式">
            <bk-select v-model="fieldData.meta.config.type" @change="change">
              <bk-option v-for="item in calculationFormula" :key="item.key" :id="item.key" :name="item.name">
              </bk-option>
            </bk-select>
            <span v-if="fieldData.meta.config.type==='CUSTOM'" class="config-formula"
                  @click="openFormulaConfig">配置公式</span>
          </bk-form-item>
          <bk-form-item label="计算字段">
            <bk-select
              v-model="fieldData.meta.config.fields"
              multiple
              @change="change"
              :key="fieldData.meta.config.type">
              <bk-option v-for="item in formulaFieldList" :key="item.key" :id="item.key" :name="item.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item label="单位">
            <bk-input v-model="fieldData.meta.config.affix" :clearable="true" :font-size="'medium'" @change="change">
              <bk-dropdown-menu
                class="group-text"
                @show="dropdownShow"
                @hide="dropdownHide"
                ref="dropdown"
                slot="prepend"
                :font-size="'medium'">
                <bk-button type="primary" slot="dropdown-trigger">
                  <span v-if="fieldData.meta.config.affix_type === 0">前缀</span>
                  <span v-if="fieldData.meta.config.affix_type === 1">后缀</span>
                  <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li><a @click="triggerHandler(0)">前缀</a></li>
                  <li><a @click="triggerHandler(1)">后缀</a></li>
                </ul>
              </bk-dropdown-menu>
            </bk-input>
          </bk-form-item>
          <bk-form-item label="保留小数位数">
            <bk-input
              type="number"
              :max="1000"
              :min="0"
              v-model="fieldData.meta.config.accuracy"
              @change="change">
            </bk-input>
          </bk-form-item>
        </template>
        <template v-if="fieldData.meta.config.calculate_type==='date'">
          <bk-form-item label="开始日期">
            <bk-select
              v-model="startTime"
              @selected="(val) => handleSelectTime('start',val)"
              :key="fieldData.meta.config.type"
              placeholder="选择开始日期">
              <bk-option v-for="item in formulaFieldList" :key="item.key" :id="item.key" :name="item.name">
              </bk-option>
            </bk-select>
            <bk-date-picker
              v-model="fieldData.meta.config.start_time"
              :placeholder="'选择日期'"
              ext-cls="date-pick"
              @change="handleChangeStartTime"
              format="yyyy-MM-dd"
              v-if="datePickerIsShow.startTimeIsshow">
            </bk-date-picker>
          </bk-form-item>
          <bk-form-item label="结束日期">
            <bk-select
              v-model="endTime"
              @selected="(val) => handleSelectTime('end',val)"
              :key="fieldData.meta.config.type"
              placeholder="选择结束日期">
              <bk-option v-for="item in formulaFieldList" :key="item.key" :id="item.key" :name="item.name">
              </bk-option>
            </bk-select>
            <bk-date-picker
              v-model="fieldData.meta.config.end_time"
              :placeholder="'选择日期'"
              ext-cls="date-pick"
              @change="handleChangeEndTime"
              format="yyyy-MM-dd"
              v-if="datePickerIsShow.endTimeIshow">
            </bk-date-picker>
          </bk-form-item>
          <bk-form-item
            label="结果精确度"
            desc-type="icon"
            desc-icon="icon-info-circle"
            :desc="{ content: '精确度将同步作为结果格式，若选择「工作日」，则只计算工作日时。',width: 208 }">
            <bk-select v-model="fieldData.meta.config.accuracy" placeholder="选择结果精确度" @selected="change">
              <bk-option v-for="item in accurcyTimeList" :key="item.key" :id="item.key" :name="item.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item label="日期字段未选择精确到时间时，默认为" :label-width="270">
            <bk-time-picker
              v-model="fieldData.meta.config.default_time"
              @change="change"
              :placeholder="'选择时间'"
              format="HH:mm">
            </bk-time-picker>
          </bk-form-item>
          <div class="checkbox-group">
            <div>
              <bk-checkbox
                v-model="fieldData.meta.config.can_format"
                @change="change"
                :true-value="true"
                :false-value="false">
                格式自适应
              </bk-checkbox>
              <i class="bk-icon icon-info-circle" v-bk-tooltips="tipsOne"></i>
            </div>
            <div class="checkbox-item">
              <bk-checkbox
                v-model="fieldData.meta.config.can_affix"
                @change="change"
                :true-value="true"
                :false-value="false">
                前缀自适应
              </bk-checkbox>
              <i class="bk-icon icon-info-circle" v-bk-tooltips="tipsTwo"></i>
            </div>
          </div>
        </template>
      </template>
      <bk-form-item
        v-if="fieldProps.fieldsShowDefaultValue.includes(fieldData.type) && fieldData.source_type === 'CUSTOM'"
        label="默认值">
        <default-value
          :key="fieldData.type"
          :field="defaultData"
          @change="handleDefaultValChange"
          @changeMember="handleMemberDefaultValChange"></default-value>
      </bk-form-item>
      <bk-form-item
        v-if="fieldProps.fieldsShowConfigValue.includes(fieldData.type) && fieldData.source_type === 'CUSTOM'"
        label="默认值">
        <config-default-value
          :key="fieldData.type"
          :field="defaultData"
          :field-list="list"
          :value="fieldData.meta.data_config"
          @confirm="handleSetDefaultValue"
          @change="handleSelectType"
          @changeFixedValue="handleDefaultValChange">
        </config-default-value>
      </bk-form-item>
      <bk-form-item v-if="fieldProps.fieldsShowDataSource.includes(fieldData.type)" label="数据源">
        <bk-select :value="fieldData.source_type" :clearable="false" @selected="handleSourceTypeChange">
          <bk-option v-for="item in sourceTypeList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
        </bk-select>
        <div class="source-type-btn" @click="openDataSourceConfig">配置数据源</div>
      </bk-form-item>
      <bk-form-item
        v-if="['MULTISELECT', 'CHECKBOX', 'MEMBERS'].includes(fieldData.type)"
        label="值数目范围"
        desc-type="icon"
        desc-icon="icon-info-circle"
        :desc="{ content: '字段的值为多个时，配置值数目的范围，默认最少0个、最多不限制',width: 208 }">
        <div class="value-num-config">
          最少选择
          <bk-input
            style="width: 100px; margin: 0 4px;"
            type="number"
            :value="fieldData.num_range[0]"
            :min="0"
            :max="9999"
            :precision="0"
            @change="handleValNumMinChange">
          </bk-input>
          个
        </div>
        <div class="value-num-config">
          最多选择
          <bk-input
            :value="fieldData.num_range[1]"
            style="width: 100px; margin: 0 4px;"
            type="number"
            :min="0"
            :max="9999"
            :precision="0"
            @change="handleValNumMaxChange">
          </bk-input>
          个
        </div>
      </bk-form-item>
      <bk-form-item label="校验方式" v-if="fieldData.type!=='FORMULA'">
        <bk-select
          v-model="fieldData.regex"
          :clearable="false"
          :searchable="true"
          :loading="regexListLoading"
          :disabled="
            regexListLoading ||
            fieldData.source === 'TABLE' ||
            (fieldData.meta && fieldData.meta.code === 'APPROVE_RESULT')
          "
          @selected="change">
          <bk-option v-for="option in regexList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
        </bk-select>
      </bk-form-item>
      <template v-if="fieldData.type === 'AUTO-NUMBER'">
        <bk-form-item label="编号预览" style="position: relative">
          <div class="set-number-btn" @click="numberRuleDialogShow = true">配置编号规则</div>
          <div class="auto-number-preview">{{ autoNumberPreviewText }}</div>
        </bk-form-item>
        <bk-form-item label="重置周期">
          <bk-select v-model="autoNumberResetData.period_type" :clearable="false" @change="change">
            <bk-option
              v-for="item in resetPeriodList"
              :key="item.id"
              :id="item.id"
              :name="`${item.id === '0' ? item.name : `按${item.name}重置`}`">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="初始值">
          <bk-input
            v-model="autoNumberResetData.value"
            type="number"
            :min="0"
            :max="Math.pow(10, autoNumberResetData.length) - 1"
            @change="change"></bk-input>
          <div v-if="autoNumberResetData.period_type !== '0'" class="start-num-text">
            <bk-radio-group v-model="autoNumberResetData.format" @change="change">
              <bk-radio :value="0">
                {{ resetTextTips[autoNumberResetData.period_type] }}，从{{ autoNumberResetData.value }}开始流水
              </bk-radio>
              <bk-radio :value="1">{{ resetTextTips[autoNumberResetData.period_type] }}，从系统初始值开始流水</bk-radio>
            </bk-radio-group>
          </div>
        </bk-form-item>
      </template>
      <bk-form-item label="布局">
        <bk-radio-group v-model="fieldData.layout" @change="change">
          <bk-radio value="COL_6" :disabled="fieldProps.fieldsFullLayout.includes(fieldData.type)">半行</bk-radio>
          <bk-radio value="COL_12" :disabled="fieldProps.fieldsFullLayout.includes(fieldData.type)">整行</bk-radio>
        </bk-radio-group>
      </bk-form-item>
      <bk-form-item v-if="!['AUTO-NUMBER', 'TABLE','FORMULA'].includes(fieldData.type)" label="是否必填">
        <bk-checkbox :value="fieldData.validate_type === 'REQUIRE'" @change="handleRequireChange">必填</bk-checkbox>
      </bk-form-item>
      <bk-form-item v-if="!['TABLE'].includes(fieldData.type)" label="全表唯一">
        <bk-radio-group v-model="fieldData.unique" @change="change">
          <bk-radio :value="true">是</bk-radio>
          <bk-radio :value="false">否</bk-radio>
        </bk-radio-group>
      </bk-form-item>
      <bk-form-item label="字段描述">
        <bk-input v-model.trim="fieldData.desc" type="textarea" :rows="4" @change="change"></bk-input>
      </bk-form-item>
      <bk-form-item label="说明">
        <bk-input v-model.trim="fieldData.tips" type="textarea" :rows="4" @change="change"></bk-input>
      </bk-form-item>
    </bk-form>
    <div>
      <data-source-dialog
        :show.sync="dataSourceDialogShow"
        :app-id="appId"
        :source-type="fieldData.source_type"
        :field-type="fieldData.type"
        :value="sourceData"
        @confirm="handleDataSourceChange">
      </data-source-dialog>
      <number-rule-dialog
        v-if="fieldData.type!=='FORMULA'"
        :show.sync="numberRuleDialogShow"
        :fields="list"
        :cur-id="value.id"
        :rules="fieldData.meta.config"
        @confirm="handleRuleConfirm">
      </number-rule-dialog>
      <!--     配置自定义计算公式-->
      <div v-else-if="fieldData.type==='FORMULA'">
        <config-formula-dialog
          :show.sync="configFormulaDialogShow"
          :fields="list"
          :value="fieldData.meta.config.value"
          :bind-fields="fieldData.meta.config.fields"
          @confirm="handleFormulaConfirm">
        </config-formula-dialog>
      </div>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import {
  FIELDS_SOURCE_TYPE,
  FIELDS_SHOW_DEFAULT_VALUE,
  FIELDS_SHOW_DATA_SOURCE,
  FIELDS_FULL_LAYOUT,
  FIELDS_SHOW_CONFIG_VALUE,
  CALCULATION_FORMULA,
  DEAFAULT_TIME,
  ACCURACY_TIME,
} from '@/constants/forms.js';
import DefaultValue from '@/components/form/defaultValue.vue';
import ConfigDefaultValue from './configDefaultValue.vue';
import DataSourceDialog from './dataSourceDialog.vue';
import NumberRuleDialog from './numberRuleDialog.vue';
import configFormulaDialog from './configFormulaDialog.vue';

export default {
  name: 'FieldEdit',
  components: {
    DefaultValue,
    DataSourceDialog,
    NumberRuleDialog,
    ConfigDefaultValue,
    configFormulaDialog,
  },
  model: {
    prop: 'value',
    event: 'change',
  },
  props: {
    appId: String,
    value: {
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
      fieldData: cloneDeep(this.value),
      fieldProps: {
        fieldsShowDefaultValue: FIELDS_SHOW_DEFAULT_VALUE,
        fieldsShowConfigValue: FIELDS_SHOW_CONFIG_VALUE,
        fieldsShowDataSource: FIELDS_SHOW_DATA_SOURCE,
        fieldsFullLayout: FIELDS_FULL_LAYOUT,
      },
      accurcyTimeList: ACCURACY_TIME,
      calculationFormula: CALCULATION_FORMULA,
      isDropdownShow: false,
      defaultData: this.getDefaultData(),
      dataSourceDialogShow: false,
      regexList: [{ id: 'EMPTY', name: '无' }], // 校验方式列表，根据不同字段类型动态请求接口
      regexListLoading: false,
      numberRuleDialogShow: false,
      configFormulaDialogShow: false,
      resetPeriodList: [
        { id: '0', name: '不重置' },
        { id: 'year', name: '年' },
        { id: 'month', name: '月' },
        { id: 'week', name: '周' },
        { id: 'day', name: '日' },
      ],
      datePickerIsShow: {
        startTimeIsshow: false,
        endTimeIshow: false,
      },
      tipsOne: {
        content: '若天数>30天，则结果格式为x月x天;',
        placements: ['top'],
        width: 188,
      },
      tipsTwo: {
        content: '若开始日期小于等于结束日期，则结果输出为“还有x天“；若开始日期大于结束日期，则结果输出为“已经x天”若天数大于365天，则结果格式为x年x月x天',
        placements: ['top'],
        width: 188,
      },
      startTime: '',
      endTime: '',
      resetTextTips: {
        day: '每天00:00',
        week: '每周的第一天00:00',
        month: '每月的第一天00:00',
        year: '每年的第一天00:00',
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
    autoNumberResetData() {
      if (this.fieldData.type === 'AUTO-NUMBER') {
        return this.fieldData.meta.config.find(item => item.type === 'number');
      }
      return {};
    },
    autoNumberPreviewText() {
      let text = '';
      if (this.fieldData.type === 'AUTO-NUMBER') {
        this.fieldData.meta.config.forEach((item, index) => {
          let { value } = item;
          if (item.type === 'number' && item.length > 1) {
            let zeroStr = '';
            for (let i = 0; i < item.length - value.toString().length; i++) {
              zeroStr += '0';
            }
            value = zeroStr + value;
          }
          text += index > 0 ? `-${value}` : value;
        });
      }
      return text;
    },
    formulaFieldList() {
      if (this.fieldData.meta.config.calculate_type === 'number') {
        return this.list.filter(item => item.type === 'INT' && item.id);
      }
      if (this.fieldData.meta.config.calculate_type === 'date') {
        return DEAFAULT_TIME.concat(this.list.filter(item => ['DATETIME', 'DATE'].includes(item.type)));
      }
      return [];
      // 系统字段加上表单的时间类型字段
    },
  },
  watch: {
    value(val, oldVal) {
      this.fieldData = cloneDeep(val);
      // 计算控件为时间计算的时候 需要初始化值 ！val.id 判断为新添加控件也需要重置
      if (val.type === 'FORMULA' && val.meta.config.calculate_type === 'date' && (val.id !== oldVal.id || !val.id)) {
        this.setDefaultDate(this.value);
      }
      this.defaultData = this.getDefaultData();
      if (val.type !== oldVal.type) {
        this.getRegexList();
      }
    },
  },
  created() {
    if (this.value.type) {
      this.getRegexList();
    }
    if (this.value.type === 'FORMULA' && this.value.meta.config.calculate_type === 'date') {
      this.setDefaultDate(this.value);
    }
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
    getDefaultData() {
      const { type, default: defaultVal, choice, meta } = this.value;
      let dftVal;
      if (['MULTISELECT', 'CHECKBOX', 'MEMBERS', 'MEMBER'].includes(type)) {
        dftVal = defaultVal ? defaultVal.split(',') : [];
      }  else {
        dftVal = cloneDeep(defaultVal);
      }
      return {
        type,
        choice,
        value: dftVal,
        meta,
        multiple: ['MULTISELECT', 'CHECKBOX'].includes(type),
      };
    },
    onNameBlur() {
      if (this.fieldData.name === '') {
        this.fieldData.name = '字段名称';
        this.change();
      }
    },
    handleRequireChange(val) {
      this.fieldData.validate_type = val ? 'REQUIRE' : 'OPTION';
      this.change();
    },
    handleDefaultValChange(val) {
      this.fieldData.default = ['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(this.fieldData.type)
        ? val.join(',')
        : cloneDeep(val);
      this.change();
    },
    handleMemberDefaultValChange(val) {
      this.$set(this.fieldData.meta, 'defaultType', val);
      if (val === 'currentUser') {
        this.fieldData.default = window.username;
      } else {
        this.fieldData.default = '';
      }
      this.change();
    },
    handleSetDefaultValue(val) {
      this.fieldData.meta = ['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(this.fieldData.type)
        ? cloneDeep(val).value.join(',')
        : cloneDeep(val);
      this.change();
    },
    openDataSourceConfig() {
      this.dataSourceDialogShow = true;
    },
    openFormulaConfig() {
      this.configFormulaDialogShow = true;
    },
    handleFormulaConfirm(val) {
      const { value, fields } = val;
      this.fieldData.meta.config.value = value;
      this.fieldData.meta.config.fields = fields;
      this.change();
      this.configFormulaDialogShow = false;
    },
    handleChangeEndTime(val) {
      this.fieldData.meta.config.end_time = val;
      this.change();
    },
    handleChangeStartTime(val) {
      this.fieldData.meta.config.start_time = val;
      this.change();
    },
    // 数据源类型切换
    handleSourceTypeChange(val) {
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
          // id: '',
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
      this.change();
    },
    // 数据源配置变更
    handleDataSourceChange(val) {
      const { source_type } = this.fieldData;
      this.dataSourceDialogShow = false;
      if (source_type === 'CUSTOM') {
        this.fieldData.choice = val;
      } else if (source_type === 'API') {
        this.fieldData.api_info = val.api_info;
        this.fieldData.kv_relation = val.kv_relation;
      } else if (source_type === 'WORKSHEET') {
        this.fieldData.meta.data_config = val;
      }
      this.change();
    },
    handleChangeType(val) {
      if (val === 'date') {
        this.fieldData.meta.config.type = 'custom';
      } else {
        this.fieldData.meta.config.type = '';
      }
      this.change();
    },
    setDefaultDate(val) {
      if (this.isDate(val.meta.config.start_time)) {
        this.startTime = 'custom';
        this.datePickerIsShow.startTimeIsshow = true;
      } else {
        this.startTime = val.meta.config.start_time;
        this.datePickerIsShow.startTimeIsshow = false;
      }
      if (this.isDate(val.meta.config.end_time)) {
        this.endTime = 'custom';
        this.datePickerIsShow.endTimeIshow = true;
      } else {
        this.endTime = val.meta.config.end_time;
        this.datePickerIsShow.endTimeIshow = false;
      }
    },
    isDate(val) {
      return isNaN(val) && (!isNaN(Date.parse(val)) || !isNaN(Date.parse(`${val}`)));
    },
    handleSelectTime(type, val) {
      if (type === 'start' && val === 'custom') {
        this.datePickerIsShow.startTimeIsshow = true;
        this.fieldData.meta.config.start_time = '';
      } else if (type === 'end' && val === 'custom') {
        this.datePickerIsShow.endTimeIshow = true;
        this.fieldData.meta.config.end_time = '';
      } else if (type === 'start') {
        this.datePickerIsShow.startTimeIsshow = false;
        this.fieldData.meta.config.start_time = val;
      } else if (type === 'end') {
        this.datePickerIsShow.endTimeIshow = false;
        this.fieldData.meta.config.end_time = val;
      }
      this.$emit('change', this.fieldData);
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(env) {
      this.$refs.dropdown.hide();
      this.fieldData.meta.config.affix_type = env;
      this.$emit('change', this.fieldData);
    },
    handleRuleConfirm(rules) {
      this.fieldData.meta.config = rules;
      this.numberRuleDialogShow = false;
      this.change();
    },
    change() {
      this.$emit('change', this.fieldData);
    },
    handleSelectType(val) {
      if (val === 'defaultValue') {
        this.fieldData.meta = {};
      } else if (val === 'curTime') {
        this.fieldData.default = 'curTime';
      } else {
        this.fieldData.default = '';
      }
      this.change();
    },
    // 值数目可选范围最小个数变更
    handleValNumMinChange(val) {
      let numVal;
      if (val === '') {
        numVal = undefined;
      } else {
        numVal = Number(val);
      }
      this.fieldData.num_range.splice(0, 1, numVal);
      this.change();
    },
    // 值数目可选范围最大个数变更
    handleValNumMaxChange(val) {
      let numVal;
      if (val === '') {
        numVal = undefined;
      } else {
        numVal = Number(val);
      }
      this.fieldData.num_range.splice(1, 1, numVal);
      this.change();
    },
  },
};
</script>
<style lang="postcss" scoped>
.source-type-btn {
  display: inline-block;
  margin-top: 8px;
  padding: 0 16px;
  height: 32px;
  line-height: 32px;
  font-size: 14px;
  color: #3a84ff;
  border: 1px solid #3a84ff;
  border-radius: 4px;
  cursor: pointer;
}

.value-num-config {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  font-size: 12px;
  color: #63656e;

  &:first-of-type {
    margin-bottom: 10px;
  }
}

.auto-number-preview {
  line-height: 22px;
  font-size: 14px;
  color: #63656e;
  word-break: break-all;
}

.set-number-btn {
  position: absolute;
  top: -27px;
  right: 0;
  font-size: 14px;
  line-height: 22px;
  color: #3a84ff;
  cursor: pointer;
}

.start-num-text {
  margin-top: 8px;
  font-size: 12px;
  color: #63656e;
  line-height: 20px;

  /deep/ .bk-form-radio {
    margin-top: 6px;
    margin-right: 0;

    .bk-radio-text {
      font-size: 12px;
    }
  }
}

.checkbox-group {
  margin-top: 16px;
  display: flex;
  flex-direction: column;

  .checkbox-item {
    margin-top: 12px;
    margin-bottom: 16px;
  }

  i {
    color: #979ba5;
  }
}

.date-pick {
  margin-top: 8px;
  width: 255px;
}

.config-formula {
  margin-top: 8px;
  color: #3A84FF;
  font-size: 14px;
  cursor: pointer;
}
</style>
