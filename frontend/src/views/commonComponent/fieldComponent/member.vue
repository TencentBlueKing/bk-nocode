<template>
    <div v-if="item.showFeild" class="member-field">
        <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :ext-cls="'bk-ext-item'" :desc="item.tips" desc-type="icon">
            <div @click="item.checkValue = false" class="member-form-item">
                <member-select :class="{ 'bk-border-error': item.checkValue }"
                    v-model="selectedItems"
                    :multiple="false"
                    :disabled="item.is_readonly">
                </member-select>
                <business-card
                    :item="item">
                </business-card>
            </div>
            <template v-if="item.checkValue">
                <p class="bk-task-error" v-if="item.checkMessage">{{ item.checkMessage }}</p>
                <p class="bk-task-error" v-else>{{ item.name }}为必填项！</p>
            </template>
        </bk-form-item>
    </div>
</template>

<script>

import mixins from '../../../commonMix/field.js';
import memberSelect from '../memberSelect/index.vue';
import businessCard from '../../workbench/components/businessCard.vue';

export default {
  name: 'MEMBER',
  components: { memberSelect, businessCard },
  mixins: [mixins],
  props: {
    item: {
      type: Object,
      default() {
        return {};
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
  },
  data() {
    return {
      selectedItems: [],
    };
  },
  watch: {
    'item.val'() {
      if (this.item.val) {
        this.selectedItems = this.item.val ? [this.item.val] : [];
      }
      this.conditionField(this.item, this.fields);
    },
    'item.value': {
      handler(val) {
        if (!val) {
          this.selectedItems  = val ? val.split(',') : [];
        }
      },
      deep: true,
    },
    selectedItems: {
      handler(newval, oldval) {
        this.item.val = this.selectedItems.join(',');
      },
    },
  },
  async mounted() {
    if (this.item.value && !this.item.val) {
      this.item.val = this.item.value;
    }
    this.selectedItems = this.item.val ? [this.item.val] : [];
    this.conditionField(this.item, this.fields);
  },
};
</script>

<style lang='postcss' scoped>
    @import '../../../css/scroller.css';
    .member-form-item {
        position: relative;
        /deep/ .business-popover {
            position: absolute;
            right: 10px;
            top: 0px;
            z-index: 1;
        }
    }
    .bk-ext-item {
        position: relative;
    }
</style>
