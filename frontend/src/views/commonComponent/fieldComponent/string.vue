<template>
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name"
                  :required="item.validate_type === 'REQUIRE'"
                  :desc="item.tips"
                  desc-type="icon">
      <!--     :placeholder="item.desc"-->
      <bk-input :class="{ 'bk-border-error': item.checkValue }"
                v-model="item.val"
                :maxlength="maxLength"
                :disabled="(item.is_readonly && !isCurrent) || disabled"
                @focus="item.checkValue = false">
      </bk-input>
      <template v-if="item.checkValue">
        <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
        <p class="bk-task-error" v-else>{{ item.name }}为必填项！</p>
      </template>
    </bk-form-item>
  </div>
</template>

<script>
import mixins from '@/commonMix/field.js';

export default {
  name: 'STRING',
  mixins: [mixins],
  props: {
    item: {
      type: Object,
      default: () => {
      },
    },
    fields: {
      type: Array,
      default() {
        return [];
      },
    },
    isCurrent: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {};
  },
  computed: {
    maxLength() {
      if (this.item.key === 'title') {
        return 120;
      }
      if (this.item.key === 'task_name') { // 标准运维任务名限制 50
        return 50;
      }
      return null;
    },
  },
  watch: {
    'item.val'(val) {
      this.item.value = val;
      this.conditionField(this.item, this.fields);
    },
  },
  mounted() {
    this.conditionField(this.item, this.fields);
    if (this.item.value && !this.item.val) {
      this.item.val = this.item.value;
    }
  },
};
</script>

<style lang='postcss' scoped>

</style>
