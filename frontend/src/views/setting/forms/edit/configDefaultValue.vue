<template>
  <div>
    <bk-select
      :value="defaultValue"
      @selected="handleSelect">
      <bk-option v-for=" option in optionList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
    </bk-select>
    <div class="fixed-value" v-show="defaultValue==='defaultValue'">
      <default-value
        :key="field.type"
        :field="field"
        @change="handleDefaultValChange">
      </default-value>
    </div>
    <div class="linkage-rules" v-show="defaultValue==='linkageRules'" @click="handleAddLinkAgeRules">
      <span>配置联动规则</span>
    </div>
    <bk-dialog
      v-model="visible"
      theme="primary"
      width="720"
      :mask-close="false"
      header-position="left"
      @cancel="onCancel"
      @confirm="onConfirm"
      title="配置联动规则">
      <bk-form :model="formData" form-type="vertical">
        <bk-form-item label="关联内容" :required="true" :property="'name'">
          <bk-radio-group v-model="formData.container" @change="handleChangeContainer">
            <bk-radio :value="1">
              本表单字段
            </bk-radio>
            <bk-radio :value="2">
              本应用其他表单
            </bk-radio>
            <bk-radio :value="3">
              其他应用表单
            </bk-radio>
          </bk-radio-group>
        </bk-form-item>
        <bk-container :col="12">
          <bk-row>
            <bk-col :span="6">
              <div class="content" style="margin-right: 12px;">
                <bk-form-item label="应用名称" :required="true" :property="'name'" v-if="formData.container===3">
                  <bk-select
                    ext-cls="sheet-name"
                    v-model="formData.appId"
                    :searchable="true"
                    :loading="appLoading"
                    @selected="handleSelectApp">
                    <bk-option
                      v-for="option in appList"
                      :key="option.key"
                      :id="option.key"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </bk-form-item>
              </div>
            </bk-col>
            <bk-col :span="6">
              <div class="content">
                <bk-form-item label="表单名称" :required="true" :property="'name'" v-if="formData.container!==1">
                  <bk-select
                    ext-cls="sheet-name"
                    v-model="formData.sheetId"
                    :searchable="true"
                    :loading="sheetLoading"
                    @selected="handleSelectSheet">
                    <bk-option
                      v-for="option in sheetList"
                      :key="option.id"
                      :id="option.id"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </bk-form-item>
              </div>
            </bk-col>
          </bk-row>
        </bk-container>
        <bk-form-item label="关联条件" :property="'name'">
          <div class="condition-area">
            <div class="condition-item" v-for="(item,index) in formData.condition" :key="item.key">
              <bk-select
                ext-cls="condition-select"
                v-model="item.id"
                :multiple="field.multiple"
                :disabled="disabled"
                :searchable="true"
                :loading="SheetFieldsLoading"
                @selected="((val) => handleCurrentFieldsSelect(item,val))">
                <bk-option
                  v-for="option in currentSheetFields"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
              <span class="condition-equal">值等于</span>
              <bk-select
                ext-cls="type-select"
                v-model="item.type"
                @selected="((val) => handleSelectVariable(item,val))"
              >
                <bk-option
                  v-for="option in typeList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
              </bk-select>
              <bk-select
                v-if="item.type!=='const'"
                ext-cls="condition-select"
                v-model="item.relationCurrentValue"
                :disabled="item.type!=='variable'"
                :searchable="true"
                :loading="SheetFieldsLoading"
                @selected="handleSelect">
                <bk-option
                  v-for="option in item.relationCurrentSheet" :key="option.id" :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
              <div class="condition-select" v-else>
                <component
                  :is="item.fieldComp"
                  :field="field"
                  :value="item.relationCurrentValue"
                  :disabled="item.type!=='const'"
                  @change="(val) => handleRuleChange(item,val)">
                </component>
              </div>
              <div class="icon-group">
                <i class="custom-icon-font icon-add-circle" @click="handleAddCondition" />
                <i class="custom-icon-font icon-reduce-circle"
                   v-if="formData.condition.length > 1"
                   @click="handleDeleteCondition(index)" />
              </div>
            </div>
          </div>
          <div class="default-value">
            <span>则默认值为</span>
            <div class="default-com">
              <component
                :is="defaultValueFieldComp"
                :field="field"
                :value="formData.value"
                @change="handleDefaultValueChange">
              </component>
            </div>
            <span>的值</span>
          </div>
        </bk-form-item>
        <bk-form-item label="支持用户修改字段值" :required="true" :property="'name'">
          <bk-radio-group v-model="formData.changeFields">
            <bk-radio :value="true">
              是
            </bk-radio>
            <bk-radio :value="false">
              否
            </bk-radio>
          </bk-radio-group>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
import DefaultValue from '@/components/form/defaultValue.vue';
import { uuid } from '@/utils/uuid.js';
import { FIELDS_TYPES, FIELDS_SHOW_CONFIG_VALUE } from '@/constants/forms.js';

// 注册fields文件夹下所有字段类型组件
function registerField() {
  const fields = require.context('@/components/form/formFields/fields/', false, /\w+\.(vue)$/);
  const components = {};
  fields.keys().forEach((fileName) => {
    const componentConfig = fields(fileName);
    const comp = componentConfig.default;
    components[comp.name] = comp;
  });

  return components;
}

export default {
  name: 'ConfigDefaultValue',
  components: {
    DefaultValue,
  },
  props: {
    field: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: Object,
      default: () => ({}),
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      visible: false,
      defaultValue: 'defaultValue',
      optionList: [{
        id: 'defaultValue',
        name: '固定值',
      }, {
        id: 'linkageRules',
        name: '联动规则',
      }],
      formData: {
        container: 1,
        condition: [{
          key: `${uuid(8)}`,
          id: '',
          type: '',
          relationCurrentSheetId: '',
          relationCurrentSheet: [],
          relationCurrentValue: '',
          fieldComp: '',
        }],
        sheetId: '',
        appId: '',
        value: '',
        changeFields: true,
      },
      currentSheetFields: [],
      appList: [],
      sheetList: [],
      SheetFieldsLoading: false,
      appLoading: false,
      sheetLoading: false,
      type: 'const',
      typeList: [{
        id: 'const',
        name: '常量',
      },
      {
        id: 'variable',
        name: '变量',
      }],
    };
  },
  computed: {
    defaultValueFieldComp() {
      return FIELDS_TYPES.find(el => el.type === this.field.type).comp;
    },
  },
  beforeCreate() {
    const fields = registerField();
    Object.keys(fields).forEach((item) => {
      this.$options.components[item] = fields[item];
    });
  },
  created() {
    this.initData(cloneDeep(this.value));
  },
  methods: {
    async initData(localValue) {
      if (Object.keys(localValue).length !== 0) {
        const { value, type, conditions, changeFields } = localValue;
        this.defaultValue = 'linkageRules';
        this.formData.value = value;
        this.formData.container = type;
        this.formData.changeFields = changeFields;
        this.formData.condition = conditions;
        if (type === 2) {
          this.formData.sheetId = localValue.target.worksheet_id;
          await this.getSheetList();
          await this.getFieldList(localValue.target.worksheet_id);
        } else if (type === 3) {
          this.formData.sheetId = localValue.target.worksheet_id;
          this.formData.appId = localValue.target.project_key;
          await this.getAppList();
          await this.getSheetListFromApp(localValue.target.project_key);
          this.currentSheetFields = this.sheetList.find(item => item.id === localValue.target.worksheet_id).fields;
        }
      }
    },
    async getFieldList(workSheetId) {
      const { version, appId, formId } = this.$route.params;
      const params = {
        project_key: appId,
        version_number: version,
        worksheet_id: workSheetId || formId,
      };
      try {
        this.SheetFieldsLoading = true;
        const result = await this.$store.dispatch('application/getWorksheetFiledConfig', params);
        this.currentSheetFields = result.data.filter(item => FIELDS_SHOW_CONFIG_VALUE.includes(item.type));
      } catch (e) {
        console.log(e);
      } finally {
        this.SheetFieldsLoading = false;
      }
    },
    async getSheetList() {
      const { appId } = this.$route.params;
      const params = {
        project_key: appId,
        need_page: 0,
      };
      try {
        this.sheetLoading = true;
        const res = await this.$store.dispatch('setting/getFormList', params);
        this.sheetList = res.data.items;
      } catch (e) {
        console.error(e);
      } finally {
        this.sheetLoading = false;
      }
    },
    // 获取某个app下的开放表单
    async getSheetListFromApp(relateApp) {
      const { appId } = this.$route.params;
      const params = {
        project: appId,
        relate_project: relateApp,
      };
      try {
        this.sheetLoading = true;
        const res = await this.$store.dispatch('setting/getWorkSheets', params);
        this.sheetList = res;
      } catch (e) {
        console.error(e);
      } finally {
        this.sheetLoading = false;
      }
    },
    async getAppList() {
      const { appId } = this.$route.params;
      const params = {
        project_key: appId,
      };
      try {
        this.appLoading = true;
        const res = await this.$store.dispatch('setting/getProjectGranted', params);
        this.appList = res;
      } catch (e) {
        console.warn(e);
      } finally {
        this.appLoading = false;
      }
    },
    handleSelect(val) {
      this.defaultValue = val;
      this.$emit('change', cloneDeep(val));
    },
    handleCurrentFieldsSelect(item, val) {
      const { type } = this.currentSheetFields.find(el => el.id === val);
      if (item.type === 'variable') {
        item.relationCurrentSheet = this.currentSheetFields
          .filter(field => field.type === type && field.id !== item.id);
        item.relationCurrentSheetId = '';
      } else if (item.type === 'const') {
        item.fieldComp = FIELDS_TYPES.find(el => el.type === type).comp;
        item.relationCurrentValue = '';
      }
    },
    handleSelectSheet(val) {
      if (this.formData.container !== 3) {
        this.getFieldList(val);
      } else {
        this.currentSheetFields = this.sheetList.find(item => item.id === val).fields;
      }
    },
    async handleSelectApp(val) {
      this.sheetList = [];
      this.getSheetListFromApp(val);
    },
    handleSelectVariable(item, val) {
      if (!item.id) {
        this.$bkMessage({
          message: '请选择本表单字段',
          theme: 'warning',
        });
        return;
      }
      const { type } = this.currentSheetFields.find(el => el.id === item.id);
      if (val === 'variable') {
        item.relationCurrentSheet = this.currentSheetFields
          .filter(field => field.type === type && field.id !== item.id);
      } else if (val === 'const') {
        item.fieldComp = FIELDS_TYPES.find(el => el.type === type).comp;
      }
    },
    handleDefaultValChange(val) {
      this.$emit('changeFixedValue', val);
    },
    handleAddLinkAgeRules() {
      this.getFieldList();
      this.visible = true;
    },
    handleAddCondition() {
      this.formData.condition.push({
        key: `${uuid(8)}`,
        id: '',
        currentSheetId: '',
        type: '',
        relationCurrentSheetId: '',
        relationCurrentSheet: [],
        relationCurrentValue: '',
        fieldComp: '',
      });
    },
    handleDeleteCondition(index) {
      this.formData.condition.splice(index, 1);
    },
    handleChangeContainer(val) {
      this.formData = {
        container: val,
        condition: [{
          key: `${uuid(8)}`,
          id: '',
          type: '',
          relationCurrentSheetId: '',
          relationCurrentSheet: [],
          relationCurrentValue: '',
          fieldComp: '',
        }],
        sheetId: '',
        appId: '',
        value: '',
        changeFields: true,
      };
      if (val === 1) {
        this.getFieldList();
      }
      if (val === 2) {
        this.getSheetList();
      }
      if (val === 3) {
        this.getAppList();
      }
    },
    onCancel() {
      this.formData = {
        container: 1,
        condition: [{
          key: `${uuid(8)}`,
          id: '',
          type: '',
          relationCurrentSheetId: '',
          relationCurrentSheet: [],
          relationCurrentValue: '',
          fieldComp: '',
        }],
        sheetId: '',
        appId: '',
        value: '',
        changeFields: true,
      };
    },
    onConfirm() {
      const params = this.getParams();
      this.$emit('confirm', params);
    },
    getParams() {
      const { container, value, condition, changeFields } = this.formData;
      const { appId, formId } = this.$route.params;
      const conditions = [];
      condition.forEach((item) => {
        conditions.push({
          id: item.id,
          key: item.key,
          relationCurrentValue: item.relationCurrentValue,
          type: item.type,
          fieldComp: item.fieldComp,
        });
      });
      const params = {
        data_config: {
          source: {
            project_key: appId,
          },
          target: {
            project_key: this.formData.appId || appId,
            worksheet_id: this.formData.sheetId || formId,
          },
          conditions,
          value,
          type: container,
          changeFields,
        },
      };
      return params;
    },
    handleRuleChange(item, val) {
      item.relationCurrentValue = val;
    },
    handleDefaultValueChange(val) {
      this.formData.value = val;
    },
  },
};
</script>

<style scoped lang="postcss">
.fixed-value {
  margin-top: 8px
}

.linkage-rules {
  margin-top: 8px;
  height: 21px;

  span {
    display: inline-block;
    font-size: 14px;
    color: #3A84FF;

    &:hover {
      cursor: pointer;
    }
  }
}

.condition-area {
  width: 640px;
  background: #FAFBFD;
  border: 1px solid #DCDEE5;
  border-radius: 2px;
  padding: 16px;

  .condition-item {
    margin-top: 16px;
    display: flex;
    align-items: center;
    height: 32px;
  }

  .condition-select {
    width: 200px;
  }

  .type-select {
    width: 80px;
    margin-right: 8px;
  }

  .condition-equal {
    display: inline-block;
    margin: 0 8px;
  }

  .icon-group {
    margin-left: 8px;

    i {
      margin-left: 8px;
      color: #63656E;

      &:hover {
        cursor: pointer;
      }
    }
  }
}

.default-value {
  margin-top: 24px;
  font-size: 14px;
  color: #63656E;
  display: flex;

  span {
    display: inline-block;
  }

  .default-com {
    width: 200px;
    margin: 0 8px;
  }
}

.sheet-name {
  width: 312px;
}

/deep/ .bk-grid-container {
  padding: 0 !important;
}
</style>
