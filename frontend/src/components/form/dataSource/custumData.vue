<template>
  <div class="custom-data-wrapper">
    <li v-for="(item, index) in localVal" class="cutsom-data-item" :key="index">
      <bk-checkbox v-if="showRequire" class="required-checkbox" v-model="item.required">必填</bk-checkbox>
      <div class="form-area">
        <bk-input
          class="custom-input"
          placeholder="请输入选项名"
          :maxlength="120"
          v-model="item.name"
          @change="handleValChange">
        </bk-input>
        <bk-input
          class="custom-input"
          placeholder="请输入选项ID"
          :maxlength="120"
          v-model="item.key"
          @change="handleValChange">
        </bk-input>
      </div>
      <div class="btn-area">
        <i class="custom-icon-font icon-add-circle add-btn" @click="handleAddItem(index)"></i>
        <i
          :class="['custom-icon-font', 'icon-reduce-circle', 'delete-btn', { disabled: localVal.length < 2 }]"
          @click="handleDeleteItem(index)"></i>
      </div>
    </li>
    <div v-if="!isValid" class="common-error-tips">选项名、ID为必填项，请检查配置</div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'CustomData',
  props: {
    value: Array,
    showRequire: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localVal: cloneDeep(this.value),
      isValid: true,
    };
  },
  watch: {
    value(val) {
      this.localVal = cloneDeep(val);
    },
  },
  methods: {
    handleAddItem(index) {
      const dataItem = { name: '', key: '' };
      if (this.fieldType === 'TABLE') {
        dataItem.required = false;
      }
      this.localVal.splice(index + 1, 0, dataItem);
      this.handleValChange();
    },
    handleDeleteItem(index) {
      if (this.localVal.length < 2) {
        return;
      }
      this.localVal.splice(index, 1);
      this.handleValChange();
    },
    handleValChange() {
      this.validate();
      this.$emit('update', cloneDeep(this.localVal));
    },
    validate() {
      const result = !this.localVal.some(item => item.name === '' || item.key === '');
      this.isValid = result;
      return result;
    },
  },
};
</script>
<style lang="postcss" scoped>
.custom-data-wrapper .cutsom-data-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  &:last-of-type {
    margin-bottom: 0;
  }
}
.required-checkbox {
  margin-right: 24px;
  /deep/ .bk-checkbox-text {
    font-size: 12px;
  }
}
.form-area {
  display: flex;
  justify-content: space-between;
  margin-right: 8px;
  .bk-form-control {
    width: 206px;
    &:not(:last-child) {
      margin-right: 10px;
    }
  }
}
.btn-area {
  user-select: none;
  .add-btn,
  .delete-btn {
    font-size: 16px;
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
</style>
