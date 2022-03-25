<template>
  <bk-dialog
    title="配置公式"
    header-position="left"
    ext-cls="formula-config-dialog"
    :mask-close="false"
    :auto-close="false"
    :close-icon="false"
    width="560"
    :value="show"
    @confirm="onConfirm"
    @cancel="$emit('update:show', false)">
    <div class="config-container">
      <div class="field-container">
        <div class="search-input">
          <bk-input
            behavior="simplicity"
            :clearable="true"
            v-model="fieldSearch"
            :right-icon="'bk-icon icon-search'"
            @enter="handleSearchField"
            @clear="handleClearSearch"
            @change="handleChange"
            placeholder="输入引用字段">
          </bk-input>
        </div>
        <ul class="field-content">
          <template v-if="fields.length>0">
            <li v-for="field in fieldList" :key="field.id" @click="handleSelectField(field)">
              {{ field.name }}
            </li>
          </template>
        </ul>
      </div>
      <div class="formula-container">
        <div class="formula-content">
          <span
            v-for="formula in Object.values(formulaMap)"
            :key="formula"
            @click="handleSelectFormula(formula)">
            {{ formula }}
          </span>
        </div>
        <div class="editor-area">
          <bk-input
            ref="textarea"
            id="editor-input"
            placeholder="请输入计算公式"
            ext-cls="editor-input"
            v-model="formulaValue"
            clearable
            :type="'textarea'"
            @change="handleInput"
            @keydown="handleKeyDown"
            @clear="handleClearFormulaValue">
          </bk-input>
          <p v-show="!checkedValidate">公式无效，请重新选择</p>
          <p v-show="!validateInput">如需要删除字段，请清空定义公式配置</p>
        </div>
      </div>
    </div>
  </bk-dialog>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'ConfigFormulaDialog',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    fields: {
      type: Array,
      default: () => [],
    },
    value: {
      type: String,
      default: '',
    },
    bindFields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      fieldSearch: '',
      fieldList: cloneDeep(this.fields).filter(item => item.type === 'INT'),
      formulaMap: {
        add: '+',
        subtraction: '-',
        multiplication: '*',
        division: '/',
        leftBracket: '(',
        rightBracket: ')',
      },
      checkedValidate: true,
      validateInput: true,
      localFields: cloneDeep(this.bindFields),
      // 传个后端的字段
      localValue: cloneDeep(this.value),
      // 展示公式
      formulaValue: '',
      showValue: '',
    };
  },
  watch: {
    value() {
      this.initData();
    },
  },
  created() {
    this.initData();
  },
  mounted() {
    const input = document.getElementById('editor-input');
    const _this = this;
    input.onclick =  async function (e) {
      const textarea = document.querySelector('#editor-input textarea');
      const len = _this.formulaValue.length;
      if (textarea.setSelectionRange) {
        // 现代浏览器
        textarea.setSelectionRange(len, len);
        textarea.focus();
      } else if (textarea.createTextRange) {
        // 兼容非现代浏览器
        const range = textarea.createTextRange();
        range.collapse(true);
        range.moveStart(_this.formulaValue, len);
        range.moveEnd(_this.formulaValue, len);
        range.select();
      }
    };
  },
  methods: {
    initData() {
      if (this.value) {
        let tempVale = cloneDeep(this.value);
        this.fieldList.forEach((item) => {
          tempVale = tempVale.replaceAll(`{${item.key}}`, item.name);
        });
        this.formulaValue = tempVale;
      } else {
        this.formulaValue = '';
        this.localValue = '';
      }
    },
    onConfirm() {
      if (this.checkFormula(this.localValue)) {
        this.$emit('confirm', {
          value: cloneDeep(this.localValue),
          fields: cloneDeep(this.localFields),
          show: this.formulaValue,
        });
      } else {
        this.checkedValidate = false;
      }
    },
    checkFormula(str) {
      return this.isCloseBrackets(str);
    },
    // 检查括号是否闭合
    isCloseBrackets(s) {
      const array = [];
      for (let i = 0; i < s.length; i++) {
        const item = s[i];
        if (item === '(') {
          array.push('(');
        } else if (item === ')') {
          if (array.length === 0) {
            return false;
          }
          array.pop();
        } else {
          continue;
        }
      }
      ;
      return array.length === 0;
    },
    handleSearchField(val) {
      this.fieldList = this.fieldList.filter(item => item.name.includes(val) && item.type === 'INT');
    },
    handleChange(val) {
      if (!val) {
        this.fieldList = cloneDeep(this.fields);
      }
    },
    handleClearSearch() {
      this.fieldList = cloneDeep(this.fields);
    },
    handleSelectField(field) {
      this.formulaValue += field.name;
      this.localValue += `{${field.key}}`;
      if (!this.localFields.includes(field.key)) {
        this.localFields.push(field.key);
      }
      this.showValue = this.formulaValue;
    },
    handleClearFormulaValue() {
      this.formulaValue = '';
      this.localValue = '';
      this.localFields = [];
    },
    handleSelectFormula(formula) {
      this.formulaValue += formula;
      this.localValue += formula;
      this.showValue = this.formulaValue;
    },
    handleInput(val, event) {
      this.validateInput = true;
      const len = this.localValue.length;
      const lastChar = this.localValue.charAt(len - 1);
      if (/^\d+$/.test(event.data)) {
        this.localValue += event.data;
        this.showValue = this.formulaValue;
      } else if (event.inputType === 'deleteContentBackward' && lastChar !== '}') {
        this.localValue = this.localValue.substring(0, len - 1);
        this.showValue = this.formulaValue;
      } else if (event.inputType === 'deleteContentBackward' && lastChar === '}') {
        this.validateInput = false;
        this.$nextTick(() => {
          this.formulaValue = cloneDeep(this.showValue);
        });
      }
    },
    handleKeyDown(val, event) {
      const { keyCode } = event;
      if (keyCode === 37 || keyCode === 39) {
        event.returnValue = false;
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
@import "../../../../css/scroller.css";

.formula-config-dialog {
  .config-container {
    display: flex;
    width: 512px;
    height: 343px;
    background: #FFFFFF;
    border: 1px solid #C4C6CC;
    border-radius: 2px;

    .field-container {
      width: 131px;
      height: 100%;
      border-right: 1px solid #C4C6CC;
    }

    .formula-container {
      width: 380px;
      height: 100%;
    }

    .search-input {
      height: 40px;
      width: 100%;
      padding: 8px 12px 0 12px;

      /deep/ .bk-form-input {
        padding-right: 10px !important;
      }

      /deep/ .control-icon {
        right: 0 !important;
      }
    }

    .field-content {
      @mixin scroller;
      width: 130px;
      height: 300px;
      overflow: auto;
      margin-top: 12px;

      li {
        width: 130px;
        height: 32px;
        line-height: 32px;
        padding-left: 12px;

        &:hover {
          background: #E1ECFF;
          color: #3a84ff;
          cursor: pointer;
        }
      }
    }

    .formula-content {
      height: 40px;
      width: 100%;
      border-bottom: 1px solid #C4C6CC;
      background: #F5F7FA;
      display: flex;
      flex-direction: row;
      align-items: center;

      span {
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        margin-left: 8px;

        &:hover {
          cursor: pointer;
          background: #E1ECFF;
          color: #3a84ff;
        }
      }
    }
  }

  .editor-area {
    .editor-input {
      width: 100%;
      height: calc(100% - 40px);
      padding: 8px;

      /deep/ .bk-textarea-wrapper {
        border: none;

        .bk-form-textarea {
          @mixin scroller;
          overflow: auto;
          min-height: 250px;
        }
      }
    }

    p {
      color: #EA3636;
      margin-top: 8px;
      margin-left: 8px;
    }

  }

}
</style>
