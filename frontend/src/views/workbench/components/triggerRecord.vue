<template>
  <div class="trigger-container">
    <bk-table
      v-bkloading="{ isLoading: tableLoading }"
      ext-cls="custom-table"
      :data="tableList"
      size="small"
      :outer-border="false"
      :header-border="false"
      :max-height="defaultTableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column :label="'执行时间'" :sortable="'custom'" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span :title="props.row.end_time">
            {{ props.row.end_time || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'响应动作'" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span :title="props.row.display_name">
            {{ props.row.component_name || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'执行状态'" :sortable="'custom'">
        <template slot-scope="props">
          <span class="bk-status-success"
                :class="{ 'bk-status-failed': props.row.status === 'FAILED' }"
                :title="props.row.status_name">
            {{ props.row.status_name || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'操作人'" :show-overflow-tooltip="true">
        <template slot-scope="props">
          <span :title="props.row.operator_username">
            {{ props.row.operator_username || '--' }}
          </span>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>
<script>
import { errorHandler } from '../../../utils/errorHandler';

export default {
  name: 'TriggerRecord',
  data() {
    return {
      tableLoading: false,
      tableList: [],
      pagination: {
        current: 1,
        count: 1,
        limit: 10,
      },
      defaultTableHeight: '',
    };
  },
  created() {
    this.initData();
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 50 - 48;
  },
  methods: {
    async initData() {
      console.log(1);
      const params = { operate_type: 'all' };
      const { id } = this.$route.params;
      this.tableLoading = true;
      const res = await this.$store.dispatch('workbench/getTicketHandleTriggers', { id, params });
      if (res.result) {
        this.tableList =  res.data.filter(item => item.status === 'FAILED' || item.status === 'SUCCEED');
      } else {
        errorHandler(res, this);
      }
      this.tableLoading = false;
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.initData();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.initData();
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../css/scroller.css";

.trigger-container {
  padding: 24px;
}

.custom-table {
  /deep/ .bk-table-body-wrapper {
    @mixin scroller;
  }
}

/deep/ .bk-table {
  &::before {
    height: 0;
  }

  .bk-link-text {
    font-size: 12px;
  }

  .bk-table-column-setting {
    border-left: none;
  }
}
.bk-status-success{
  color: #2DCB56;
}
.bk-status-failed{
  color: #FF5656;
}
</style>
