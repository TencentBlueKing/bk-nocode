<template>
  <bk-form :label-width="100" ext-cls="custom-edit-form">
    <form-fields :fields="fieldsList" :value="value" @change="debounceChange" />
  </bk-form>
</template>
<script>
import FormFields from '@/components/form/formFields/index.vue';
import clonedeep from 'lodash.clonedeep';
import {debounce} from '@/utils/util';
import judgeFieldsConditionMixins from '@/components/form/formFields/judgeFieldsConditionMixins';
export default {
  name: 'EditorForm',
  components: { FormFields },
  mixins: [judgeFieldsConditionMixins],
  props: {
    fields: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      fieldsList: clonedeep(this.fields).filter(item => !['id', 'title'].includes(item.key)),
    };
  },
  watch: {
    fields: {
      handler(val) {
        this.judgeCondition();
      },
      deep: true,
    },
  },
  created() {
    this.initWorkSheetData();
    this.debounceChange = debounce(this.handleSetValue, 300);
    this.judgeCondition();
  },
  methods: {
    async initWorkSheetData() {
        const formVale = {};
        this.fields.forEach((item) => {
          formVale[item.key] = item.value;
        });
        for (let i = 0; i < this.fields.length; i++) {
          console.log("执行了");
          this.setWorkSheetData(this.fields[i].key, formVale);
        }
    },
    async setWorkSheetData(key, $event) {
      // 临时方案，当值变化是，需要先计算好变化的值所依赖的所有的下拉框, 之后填充字段值
      // 如果变化的不是被联动的字段，则返回
      this.fieldList = [];
      for (let i = 0; i < this.fields.length; i++) {
        if (this.fields[i].meta.data_config) {
          this.fieldList.push(this.fields[i]);
        }
      }

      const currentIndex = this.fieldList.findIndex(i => i.key === key);
      const currentField = this.fieldList[currentIndex];

      if (!currentField) {
        return;
      }

      if (!(currentField.type === "SELECT")) {
        return;
      }
      if (!currentField.meta.worksheet) {
        return;
      }
      const worksheetFieldList = [];
      // 先过滤出来所有的和当前字段有关的包含变量引用的下拉框字段
      for (let i = 0; i < this.fieldList.length; i++) {
        if (this.fieldList[i].meta.data_config) {
          const expressions = this.fieldList[i].meta.data_config.conditions.expressions;
          let isField = false;
          for (let j = 0; j < expressions.length; j++) {
            if (expressions[j].type === "field" && expressions[j].value === currentField.meta.worksheet.field_key) {
              isField = true;
            }
          }
          if (isField) {
            worksheetFieldList.push(this.fieldList[i]);
          }
        }
      }
      // 计算这些字段
      for (let i = 0; i < worksheetFieldList.length; i++) {
        const data_config = clonedeep(worksheetFieldList[i].meta.data_config);
        const expressions = data_config.conditions.expressions || [];
        for (let j = 0; j < expressions.length; j++) {
          for (let k = 0; k < this.fieldList.length; k++) {
            if (expressions[j].value === currentField.meta.worksheet.field_key) {
              expressions[j].value = $event[key];
              expressions[j].type = "const";
            }
            if (expressions[j].value === this.fieldList[k].meta.worksheet.field_key && expressions[j].value !== currentField.meta.worksheet.field_key) {
              expressions[j].value = $event[this.fieldList[k].key];
              expressions[j].type = "const";
            }
          }
        }
        const {field, conditions} = data_config;
        let params;
        if (!conditions.connector && !conditions.expressions.every(i => i)) {
          params = {
            token: worksheetFieldList[i].token,
            fields: [field],
            conditions: {},
          };
        } else {
          params = {
            token: worksheetFieldList[i].token,
            fields: [field],
            conditions,
          };
        }
        try {
          const res = await this.$store.dispatch('setting/getWorksheetData', params);
          const choices = res.data.map((item) => {
            const val = item[field];
            return {key: val, name: val};
          });
          worksheetFieldList[i].choice = choices;
        } catch (e) {
          console.error(e);
        }
      }
    },
    handleSetValue(key, $event) {
      this.setWorkSheetData(key, $event);
      this.$emit('change', key, $event);
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-edit-form {
  padding: 0 40px 24px;
  /deep/ .bk-label-text {
    font-size: 14px;
    color: #979ba5;
  }
  /deep/ .bk-form-content {
    font-size: 14px;
    color: #63656e;
  }
}
</style>
