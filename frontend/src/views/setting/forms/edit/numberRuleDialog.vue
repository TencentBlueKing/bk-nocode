<template>
  <bk-dialog
    title="配置编号规则"
    header-position="left"
    ext-cls="number-rule-dialog"
    :mask-close="false"
    :auto-close="false"
    :width="416"
    :value="show"
    @confirm="onConfirm"
    @cancel="$emit('update:show', false)">
    <div class="rule-content">
      <bk-form class="form-wrapper" form-type="vertical">
        <draggable handle=".drag-icon" :list="listData" :animation="200">
          <bk-form-item
            v-for="(rule, index) in listData"
            :key="index"
            :label="autoNumberRules.find(item => item.type === rule.type).name">
            <i class="drag-icon bk-icon icon-grag-fill"></i>
            <i v-if="rule.type !== 'number'" class="delete-icon bk-icon icon-delete" @click="handleDelRule(index)"> </i>
            <div v-if="rule.type === 'number'" class="serial-form">
              <bk-input v-model="rule.length" type="number" style="margin-right: 8px" :max="10" :min="4"></bk-input>
              位
            </div>
            <bk-select v-else-if="rule.type === 'datetime'" v-model="rule.value" :clearable="false">
              <bk-option v-for="item in ruleCreateTime" :key="item.id" :id="item.id" :name="item.name"></bk-option>
            </bk-select>
            <bk-select v-else-if="rule.type === 'field'" v-model="rule.value" :clearable="false">
              <bk-option v-for="item in fieldList" :key="item.key" :id="item.key" :name="item.name"></bk-option>
            </bk-select>
            <bk-input v-else v-model="rule.value"></bk-input>
          </bk-form-item>
        </draggable>
      </bk-form>
      <div class="add-btn">
        <bk-dropdown-menu align="left" trigger="click">
          <template slot="dropdown-trigger">
            <span class="trigger-btn"><i class="bk-icon icon-plus"></i>添加规则</span>
          </template>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li v-for="item in ruleList" :key="item.type" @click="handleAddRule(item.type)">{{ item.name }}</li>
          </ul>
        </bk-dropdown-menu>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
import draggable from 'vuedraggable';
import cloneDeep from 'lodash.clonedeep';
import { AUTO_NUMBER_RULES, RULE_CREATE_TIME } from '@/constants/forms.js';

export default {
  name: 'NumberRuleDialog',
  components: {
    draggable,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    rules: {
      type: Array,
      default: () => [],
    },
    fields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      listData: cloneDeep(this.rules),
      autoNumberRules: AUTO_NUMBER_RULES.slice(0),
      ruleCreateTime: RULE_CREATE_TIME.slice(0),
    };
  },
  computed: {
    ruleList() {
      return this.autoNumberRules.filter(item => {
        if (item.type !== 'number') {
          if (item.type === 'datetime') {
            return !this.listData.some(data => data.type === 'datetime');
          }
          return true;
        }
      });
    },
    fieldList() {
      return this.fields.filter(item => item.key);
    },
  },
  watch: {
    rules(val) {
      this.listData = cloneDeep(val);
    },
  },
  methods: {
    handleAddRule(type) {
      const value = type === 'datetime' ? 'YYYY-MM-DD' : '';
      this.listData.push({ type, value });
    },
    handleDelRule(index) {
      this.listData.splice(index, 1);
    },
    onConfirm() {
      this.$emit('confirm', this.listData);
    },
  },
};
</script>
<style lang="postcss" scoped>
.rule-content {
  padding: 4px 0 24px;

  .form-wrapper {
    padding: 0 20px 0 30px;
    max-height: 310px;
    overflow: auto;
  }
  .bk-form-item:hover {
    .delete-icon {
      display: inline-block;
    }
  }
  .drag-icon {
    position: absolute;
    left: -20px;
    top: 9px;
    color: #c4c6cc;
    cursor: move;
    &:hover {
      color: #313238;
    }
  }
  .delete-icon {
    display: none;
    position: absolute;
    top: -22px;
    right: 0px;
    color: #979ba5;
    font-size: 16px;
    cursor: pointer;
    &:hover {
      color: #3a84ff;
    }
  }
  .serial-form {
    display: flex;
    justify-content: space-between;
  }
  .add-btn {
    margin-top: 16px;
    padding: 0 20px 0 30px;
    .trigger-btn {
      font-size: 14px;
      color: #3a84ff;
      cursor: pointer;
      i {
        font-size: 18px;
      }
    }
    .bk-dropdown-list {
      width: 100%;
      & > li {
        padding: 0 16px;
        line-height: 32px;
        font-size: 12px;
        color: #63656e;
        white-space: nowrap;
        cursor: pointer;
        &:hover {
          color: #3a84ff;
          background: #eaf3ff;
        }
      }
    }
  }
}
</style>
<style lang="postcss">
.number-rule-dialog {
  .bk-dialog-body {
    padding: 0;
  }
}
</style>
