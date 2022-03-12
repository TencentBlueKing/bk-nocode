<template>
    <div v-if="item.showFeild">
        <bk-form-item :label="item.name" :required="item.validate_type === 'REQUIRE'" :ext-cls="'bk-ext-item'" :desc="item.tips" desc-type="icon">
            <div @click="item.checkValue = false" class="member-form-item">
<!--              :placeholder="item.desc"-->
                <member-select :class="{ 'bk-border-error': item.checkValue }"
                    v-model="selectedItems"
                    :disabled="(item.is_readonly && !isCurrent) || item.evaluDisable || disabled"
                    @change="onMemberSelectChange">
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
  name: 'MEMBERS',
  components: {
    memberSelect,
    businessCard,
  },
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
    return {
      selectedItems: [],
    };
  },
  watch: {
    'item.val'(val) {
      this.selectedItems = val ? val.split(',') : [];
    },
  },
  async mounted() {
    if (this.item.value && !this.item.val) {
      this.item.val = this.item.value;
    }
    this.selectedItems = this.item.val ? this.item.val.split(',') : [];
    this.conditionField(this.item, this.fields);
  },
  methods: {
    onMemberSelectChange(data) {
      this.item.val = data.join(',');
    },
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
