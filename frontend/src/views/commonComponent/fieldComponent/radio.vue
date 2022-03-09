<template>
  <div v-if="item.showFeild">
    <bk-form-item :label="item.name"
                  :required="item.validate_type === 'REQUIRE'"
                  :desc="item.tips"
                  :ext-cls="'bk-line-height'"
                  desc-type="icon">
      <bk-radio-group v-model="item.val" @change="item.checkValue = false">
        <template v-for="radio in item.choice">
          <bk-radio :disabled="disabled" :value="radio.key" :key="radio.key" :ext-cls="'mr20'">{{ radio.name }}
          </bk-radio>
        </template>
      </bk-radio-group>
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
  name: 'RADIO',
  mixins: [mixins],
  props: {
    item: {
      type: Object,
      required: true,
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
  watch: {
    'item.val'() {
      this.conditionField(this.item, this.fields);
    },
    'item.value': {
      handler() {
        this.item.val = this.item.value;
      },
      deep: true,
    },
  },
  async mounted() {
    this.item.choice = await this.getFieldOptions(this.item);
    if (this.item.value && !this.item.val) {
      this.item.val = this.item.value;
    }
    const valueStatus = await this.judgeValue(this.item.val, this.item.choice);
    this.item.val = valueStatus ? this.item.val : '';
    this.conditionField(this.item, this.fields);
  },
  methods: {},
};
</script>

<style lang='postcss' scoped>

</style>
