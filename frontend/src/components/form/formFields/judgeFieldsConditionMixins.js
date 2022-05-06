import { CONDITION_FUNCTION_MAP } from '@/constants/forms.js';
export default {
  methods: {
    judgeCondition() {
      // 过滤掉不用填的字段
      const fields =  this.fields.filter(item => !['id', 'title'].includes(item.key));
      const  len = fields.length;
      this.fieldsList = fields;
      for (let i = 0; i < len;i++) {
        // 必填
        if (this.isObjectHaveAttr(fields[i].mandatory_conditions)) {
          this.judgeFieldsCondition(fields[i].mandatory_conditions)
            ? this.$set(this.fieldsList[i], 'validate_type', 'REQUIRE')
            : this.$set(this.fieldsList[i], 'validate_type', 'OPTION');
          // function 判断是否符合设置条件 里面包含 各种操作符号 >= ...
        }
        // 只读
        if (this.isObjectHaveAttr(fields[i].read_only_conditions)) {
          this.judgeFieldsCondition(fields[i].read_only_conditions)
            ? this.$set(this.fieldsList[i], 'is_readonly', true)
            : this.$set(this.fieldsList[i], 'is_readonly', false);
        }
        // 显隐
        if (this.isObjectHaveAttr(fields[i].show_conditions)) {
          // 1 为展示，0为隐藏
          this.judgeFieldsCondition(fields[i].show_conditions)
            ? this.$set(this.fieldsList[i], 'show_type', 0)
            : this.$set(this.fieldsList[i], 'show_type', 1);
        }
      }
    },

    judgeFieldsCondition(condition) {
      // 且或逻辑处理        遍历条件  or  some || and every
      if (condition.connector === 'and' || condition.type === 'and') {
        // 这里需要对符号判断
        return  condition.expressions?.every((item) => {
          const  func = CONDITION_FUNCTION_MAP[item.condition];
          return this[func](
            this.fieldsList.find(el => el.key === item.key)?.value,
            item.value
          );
        });
      }
      //  or 的条件处理
      return condition.expressions?.some((item) => {
        const  func = CONDITION_FUNCTION_MAP[item.condition];
        return this[func](
          this.fieldsList.find(el => el.key === item.key)?.value,
          item.value
        );
      });
    },

    isObjectHaveAttr(value) {
      return !!Object.keys(value).length;
    },

    judgePageCondition() {
      const  len = this.fieldList.length;
      for (let i = 0; i < len;i++) {
        const  isNumber = this.fieldList[i].type === 'INT';
        // 必填
        if (this.isObjectHaveAttr(this.fieldList[i].mandatory_conditions)) {
          this.judgePageFieldsCondition(this.fieldList[i].mandatory_conditions, isNumber)
            ? this.$set(this.fieldList[i], 'validate_type', 'REQUIRE')
            : this.$set(this.fieldList[i], 'validate_type', 'OPTION');
          // function 判断是否符合设置条件 里面包含 各种操作符号 >= ...
        }
        // 只读
        if (this.isObjectHaveAttr(this.fieldList[i].read_only_conditions)) {
          this.judgePageFieldsCondition(this.fieldList[i].read_only_conditions, isNumber)
            ? this.$set(this.fieldList[i], 'is_readonly', true)
            : this.$set(this.fieldList[i], 'is_readonly', false);
        }
        // 显隐
        if (this.isObjectHaveAttr(this.fieldList[i].show_conditions)) {
          // 1 为展示，0为隐藏
          this.judgePageFieldsCondition(this.fieldList[i].show_conditions, isNumber)
            ? this.$set(this.fieldList[i], 'show_type', 0)
            : this.$set(this.fieldList[i], 'show_type', 1);
        }
      }
    },
    judgePageFieldsCondition(condition, isNumber) {
      // 且或逻辑处理        遍历条件  or  some || and every
      if (condition.connector === 'and' || condition.type === 'and') {
        // 这里需要对符号判断
        return  condition.expressions?.every((item) => {
          const  func = CONDITION_FUNCTION_MAP[item.condition];
          return this[func](
            isNumber ? item.value : Number(item.value),
            isNumber ? this.formValue[item.key] : Number(this.formValue[item.key])
          );
        });
      }
      //  or 的条件处理
      return condition.expressions?.some((item) => {
        const  func = CONDITION_FUNCTION_MAP[item.condition];
        return this[func](
          isNumber ? item.value : Number(item.value),
          isNumber ? this.formValue[item.key] : Number(this.formValue[item.key])
        );
      });
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
      return param2 < param1 ;
    },
    include(param1, param2) {
      return   param2.includes(param1);
    },
  },
};
