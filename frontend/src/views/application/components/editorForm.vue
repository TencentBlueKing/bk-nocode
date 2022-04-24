<template>
  <bk-form :label-width="100" ext-cls="custom-edit-form">
    <form-fields :fields="currentFields" :value="value" @change="handleSetValue" />
  </bk-form>
</template>
<script>
import FormFields from '@/components/form/formFields/index.vue';
import clonedeep from 'lodash.clonedeep';
import { CONDITION_FUNCTION_MAP } from '@/constants/forms.js';
export default {
  name: 'EditorForm',
  components: { FormFields },
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
      fieldsList: clonedeep(this.fields),
    };
  },
  computed: {
    currentFields() {
      return this.fields.filter(item => !['id', 'title'].includes(item.key));
    },
  },
  created() {
    this.judgeCondition();
  },
  methods: {
    handleSetValue(key, $event) {
      this.$emit('change', $event);
    },
    judgeCondition() {
      // 过滤掉不用填的字段
      const fields =  this.fields.filter(item => !['id', 'title'].includes(item.key));
      const  len = fields.length;
      this.fieldsList = fields;
      for (let i = 0; i < len;i++) {
        // 必填
        if (this.isObjectHaveAttr(fields[i].mandatory_conditions)) {
          // 遍历条件  or  some || and every
          this.judgeFieldsCondition(fields[i].mandatory_conditions);
          // function 判断是否符合设置条件 里面包含 各种操作符号 >= ...
        }
        // 只读
        if (this.isObjectHaveAttr(fields[i].read_only_conditions)) {
          this.judgeFieldsCondition(fields[i].read_only_conditions);
        }
        // 显隐
        if (this.isObjectHaveAttr(fields[i].show_conditions)) {
          this.judgeFieldsCondition(fields[i].show_conditions);
        }
      }
    },
    isObjectHaveAttr(value) {
      return !!Object.keys(value).length;
    },

    //
    judgeFieldsCondition(condition) {
      // 且或逻辑处理
      if (condition.connector === 'and') {
        // 这里需要对符号判断
        const a = condition.expressions.every((item) => {
          const  func = CONDITION_FUNCTION_MAP[item.condition];
          return this[func](
            this.fieldsList.find(el => el.key === item.key)?.value,
            item.value
          );
        });
        console.log(a);
      }
    },
    equeal(param1, param2) {
      return param1 === param2;
    },
    greaterOrEqual(param1, param2) {
      return param1 >= param2;
    },
    lessOrEaqual(param1, param2) {
      return param1 <= param2;
    },
    greater(param1, param2) {
      return param1 > param2;
    },
    lesser(param1, param2) {
      return param1 < param2;
    },
    include(param1, param2) {
      return   param2.includes(param1);
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
