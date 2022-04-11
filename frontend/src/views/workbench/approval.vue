<template>
  <page-wrapper title="带我审批">
    <div class="workbench-todo-container">
      <div class="header-search">
        <div>
          <bk-button :theme="'primary'" :title="'导出'" @click="handleExport"> 导出</bk-button>
          <bk-button
            :theme="'default'"
            :disabled="!selectedList.length"
            style="margin-left: 5px"
            @click="onBatchApprovalClick">
            批量审批
          </bk-button>
        </div>
        <div class="option-area">
          <bk-input
            class="search-width"
            :placeholder="'请输入编码'"
            :left-icon="'bk-icon icon-search'"
            clearable
            v-model="keyword"
            @change="handleChange"
            @enter="handlerSearch"
            @right-icon-click="handlerSearch">
          </bk-input>
          <bk-select
            v-model="project_key"
            ext-cls="search-width"
            :placeholder="'请选择应用'"
            @selected="handlerSearch"
            @clear="() => initData()"
            searchable
            clearable
          >
            <bk-option v-for="option in appList" :key="option.key" :id="option.key" :name="option.name"></bk-option>
          </bk-select>
        </div>
      </div>
      <div class="workbench-todo-table">
        <bk-table
          ref="ticketList"
          v-bkloading="{ isLoading: tableLoading, zIndex: 9999 }"
          ext-cls="custom-table"
          :data="tableList"
          :size="size"
          :outer-border="false"
          :header-border="false"
          :pagination="pagination"
          :max-height="defaultTableHeight"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          @select-all="handleSelectAll">
          <bk-table-column type="selection" width="60" :selectable="canSelected">
            <template slot-scope="props">
              <bk-checkbox
                v-if="props.row.waiting_approve"
                v-model="props.row.checkStatus"
                @change="changeSelection(props.row)">
              </bk-checkbox>
            </template>
          </bk-table-column>
          <bk-table-column label="流程编号" fixed="left" width="150">
            <template slot-scope="{ row }">
              <column-sn :row="row"></column-sn>
            </template>
          </bk-table-column>
          <bk-table-column
            v-for="field in columnList"
            :key="field.id"
            :label="field.label"
            :show-overflow-tooltip="true">
            <template slot-scope="{ row }">
                <span v-if="field.id==='current_steps'">
                  {{ row.current_steps[0] && row.current_steps[0].name || '--' }}
                </span>
              <span v-else>{{ row[field.id] || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="'节点状态'"
            prop="current_status_display"
            :filters="statusFilters"
            :filter-method="statusFilterMethod"
            :filter-multiple="true">
            <template slot-scope="{ row }">
              <div>
                <span
                  :class="['status',statusMap[row.current_status]]"
                  v-if="!['RUNNING','QUEUEING'].includes(row.current_status)"></span>
                <bk-spin size="mini" v-else></bk-spin>
                <span>{{ row.current_status_display || '--' }}</span>
              </div>
            </template>
          </bk-table-column>
          <bk-table-column label="操作" fixed="right">
            <!-- 操作 -->
            <template slot-scope="{ row }">
              <bk-link class="table-link" theme="primary" @click="onOpenApprovalDialog(row.id, true)">
                通过
              </bk-link>
              <bk-link class="table-link" theme="primary" @click="onOpenApprovalDialog(row.id, false)">
                拒绝
              </bk-link>
            </template>
          </bk-table-column>
          <bk-table-column type="setting">
            <bk-table-setting-content
              :fields="settingList"
              :selected="columnList"
              @setting-change="handleSettingChange">
            </bk-table-setting-content>
          </bk-table-column>
        </bk-table>
      </div>
      <approval-dialog
        :is-show.sync="isApprovalDialogShow"
        :approval-info="approvalInfo"
        @cancel="onApprovalDialogHidden">
      </approval-dialog>
    </div>
  </page-wrapper>
</template>

<script>
import PageWrapper from '@/components/pageWrapper.vue';
import approvalDialog from './approvalDialog.vue';
import ColumnSn from './components/columnSn.vue';
import status from './mixin/status';
import { getQuery } from '../../utils/util';
import { errorHandler } from '../../utils/errorHandler';

export default {
  name: 'Approval',
  components: {
    PageWrapper,
    ColumnSn,
    approvalDialog,
  },
  mixins: [status],
  data() {
    return {
      keyword: '',
      tableList: [],
      tableLoading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      selectedList: [],
      defaultTableHeight: '',
      size: 'small',
      isApprovalDialogShow: false,
      approvalInfo: {
        showAllOption: false,
        result: true,
        approvalList: [],
      },
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 80 - 24;
  },
  mounted() {
    this.initData();
  },
  methods: {
    handleExport() {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        view_type: 'my_approval',
        keyword: this.keyword,
      };
      this.project_key ? params.project_key = this.project_key : '';
      const paramsStr = getQuery(params);
      const BASE_URL = `${window.SITE_URL}api/ticket/receipts/export_group_by_service/${paramsStr}`;
      window.open(BASE_URL);
    },
    handleChange(val) {
      if (!val) {
        this.pagination.current = 1;
        this.initData();
      }
    },
    handlerSearch() {
      const searchParams = {};
      this.project_key ? searchParams.project_key = this.project_key : '';
      this.keyword ? searchParams.keyword = this.keyword : '';
      this.pagination.current = 1;
      this.initData(searchParams);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.initData();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.initData();
    },
    async initData(searchParams) {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        view_type: 'my_approval',
        ...searchParams,
      };
      this.project_key ? params.project_key = this.project_key : '';
      this.keyword ? params.keyword = this.keyword : '';
      this.tableLoading = true;
      const res = await this.$store.dispatch('workbench/getList', { params });
      if (res.result) {
        this.tableList = res.data.items.map(item => ({ ...item, checkStatus: false }));
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } else {
        errorHandler(res, this);
      }
      this.tableLoading = false;
    },
    handleSettingChange({ fields, size }) {
      this.size = size;
      this.columnList = fields;
    },
    handleSelectAll(selection) {
      this.tableList.forEach((item) => {
        item.checkStatus = !!selection.length;
      });
      this.selectedList = selection;
    },
    onBatchApprovalClick() {
      this.isApprovalDialogShow = true;
      this.approvalInfo = {
        result: true,
        showAllOption: true,
        approvalList: this.selectedList.map(item => ({ ticket_id: item.id })),
      };
    },
    onApprovalDialogHidden(result) {
      this.isApprovalDialogShow = false;
      this.approvalInfo = {
        result: true,
        showAllOption: false,
        approvalList: [],
      };
      if (result) {
        this.initData();
      }
    },
    // 可以选中
    canSelected(row, index) {
      return row.waiting_approve;
    },
    // 改变中选态，与表头选择相呼应
    changeSelection(value) {
      this.$refs.ticketList.toggleRowSelection(value, value.checkStatus);
      if (value.checkStatus) {
        if (!this.selectedList.some(item => item.id === value.id)) {
          this.selectedList.push(value);
        }
      } else {
        this.selectedList = this.selectedList.filter(item => item.id !== value.id);
      }
    },
    onOpenApprovalDialog(id, result) {
      this.isApprovalDialogShow = true;
      this.approvalInfo = {
        result,
        approvalList: [{ ticket_id: id }],
      };
    },
  },
};
</script>

<style lang="postcss" scoped>
@import "../../css/scroller.css";

.workbench-todo-container {
  margin: 24px;
  padding: 24px;
  background: #ffffff;

  .workbench-todo-table {
    margin-top: 24px;
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

    .bk-table-column-setting {
      border-left: none;
    }
  }

  .header-search {
    display: flex;
    justify-content: space-between;

    .search-width {
      width: 240px;
      margin-right: 16px;
    }
  }

  .option-area {
    display: flex;
  }

,
. status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}

  .wait-status {
    background: #FFE8C3;
    border: 1px solid #FF9C01;
  }

  .finish-status {
    background: #E5F6EA;
    border: 1px solid #3FC06D;
  }

  .fail-status {
    background: #FFE6E6;
    border: 1px solid #EA3636;
  }
}

.table-link {
  margin-right: 8px;

  /deep/ span {
    font-size: 12px;
  }
}
</style>
