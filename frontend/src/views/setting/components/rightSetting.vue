<template>
  <div>
    <div class="setting-title">
      <span> 列表属性 </span>
    </div>
    <attribute-form
      :function-list="functionList"
      :group="type"
      ref="attributeForm"
      :work-sheet-id="workSheetId"
      :show-mode="showMode"
      :conditions="conditions"
      :time-range="timeRange"
      :sort-by="ordering"
      :work-sheet-list="tableList"
      @select="handleSelect">
    </attribute-form>
  </div>
</template>

<script>
import Bus from '@/utils/bus.js';
import attributeForm from './attributeForm.vue';
export default {
  name: 'RightSetting',
  components: {
    attributeForm,
  },
  props: {
    type: {
      type: String,
      default: '',
    },
    workSheetId: [Number, String],
    showMode: [Number, String],
    timeRange: String,
    ordering: String,
    conditions: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      functionList: [],
      tableList: [],
    };
  },
  watch: {
    workSheetId: {
      handler(val) {
        if (val) {
          this.getFunctionList();
        }
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    this.getList();
    Bus.$on('sendFormData', async (val) => {
      const { workSheetId } = val;
      if (workSheetId) {
        this.getFunctionList(workSheetId);
      }
    });
  },
  methods: {
    async getFunctionList(id) {
      const { appId } = this.$route.params;
      const params = {
        project_key: appId,
        worksheet_id: id || this.workSheetId,
      };
      try {
        const res = await this.$store.dispatch('setting/getFunctionBindList', params);
        this.functionList = res.data;
      } catch (e) {
        console.log(e);
      }
    },
    // 获取表单字段
    async getList() {
      if (this.type === 'LIST') {
        const { appId } = this.$route.params;
        const params = {
          project_key: appId,
          page_size: 10000,
        };
        try {
          const res = await this.$store.dispatch('setting/getWorkSheetList', params);
          this.tableList = res.data.items;
        } catch (e) {
          console.log(e);
        }
      }
    },
    handleSelect(val) {
      this.$emit('select', val);
    },
  },
};
</script>

<style lang="postcss" scoped>
.setting-title {
  width: 320px;
  height: 40px;
  background: #FFFFFF;
  border-bottom: 1px solid #DCDEE5;
  display: table;
  -webkit-border-horizontal-spacing: 24px;

  span {
    margin-left: 24px;
    font-size: 14px;
    color: #313238;
    letter-spacing: 0;
    line-height: 22px;
    display: table-cell;
    vertical-align: middle;
  }
}
</style>
