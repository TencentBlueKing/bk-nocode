<template>
  <section class="workbench-process-content">
    <page-wrapper title="我关注的">
      <div class="workbench-attention-container">
        <div class="header-search">
          <bk-button :theme="'primary'" :title="'导出'" @click="handleExport"> 导出</bk-button>
          <bk-input
            class="search-width"
            :placeholder="'请输入编码'"
            :left-icon="'bk-icon icon-search'"
            clearable
            @change="handleChange"
            v-model="keyword"
            @enter="handlerSearch"
            @right-icon-click="handlerSearch">
          </bk-input>
        </div>
        <div class="workbench-attention-table">
          <bk-table
            v-bkloading="{ isLoading: tableLoading }"
            ext-cls="custom-table"
            :data="tableList"
            :size="size"
            :outer-border="false"
            :header-border="false"
            :pagination="pagination"
            :max-height="defaultTableHeight"
            @page-change="handlePageChange"
            @page-limit-change="handlePageLimitChange">
            <bk-table-column type="index" label="No." width="60"></bk-table-column>
            <bk-table-column v-for="field in columnList" :key="field.id" :label="field.label">
              <template slot-scope="{ row }">
                <column-sn v-if="field.id === 'sn'" :row="row"></column-sn>
                <span v-else-if="field.id==='current_steps'">
                  {{row.current_steps[0]&&row.current_steps[0].name|| '--' }}
                </span>
                <bk-button
                  v-else-if="field.id==='operate'"
                  theme="primary"
                  text
                  @click="handleUnsubscribe(props.row)">取消关注
                </bk-button>
                <span v-else>{{ row[field.id] || '--' }}</span>
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
      </div>
    </page-wrapper>
  </section>
</template>
<script>
import PageWrapper from '@/components/pageWrapper.vue';
import ColumnSn from './components/columnSn.vue';
import { errorHandler } from '../../utils/errorHandler';
import { getQuery } from '../../utils/util';

const COLUMN_LIST = [
  {
    id: 'sn',
    label: '流程编号',
    prop: 'sn',
    width: '140',
    disabled: true,
  },
  {
    id: 'service_name',
    label: '流程名称',
    prop: 'service_name',
    width: '140',
    disabled: true,
  },
  {
    id: 'current_steps',
    label: '当前节点',
    prop: 'current_steps[0].name',
    width: '140',
  },
  {
    id: 'creator',
    label: '发起人',
    prop: 'creator',
    width: '140',
    disabled: true,
  },
  {
    id: 'create_at',
    label: '创建时间',
    minWidth: '140',
    prop: 'create_at',
  },
  {
    id: 'current_status_display',
    label: '节点状态',
    minWidth: '140',
    prop: 'current_status_display',
  },
  {
    id: 'operate',
    label: '操作',
    minWidth: '80',
    disabled: true,
  },
];
export default {
  name: 'Attention',
  components: {
    PageWrapper,
    ColumnSn,
  },
  data() {
    return {
      keyword: '',
      columnList: COLUMN_LIST,
      tableList: [],
      tableLoading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      defaultTableHeight: '',
      settingList: COLUMN_LIST,
      size: 'small',
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
        view_type: 'my_attention',
        keyword: this.keyword,
      };
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
      const searchParams = {
        keyword: this.keyword,
      };
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
        view_type: 'my_attention',
        ...searchParams,
      };
      this.tableLoading = true;
      const res = await this.$store.dispatch('workbench/getList', { params });
      if (res.result) {
        this.tableList = res.data.items;
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
    handleUnsubscribe(row) {
      const { id } = row;
      const params = {
        attention: false,
      };
      this.$store.dispatch('workbench/setAttention', { params, id }).then(() => {
        this.$bkMessage({
          message: '取消关注成功~',
          theme: 'success',
          ellipsisLine: 0,
        });
        this.initData();
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
  },
};
</script>
<style lang="postcss" scoped>
@import "../../css/scroller.css";

.workbench-attention-container {
  margin: 24px;
  padding: 24px;
  background: #fff;

  .workbench-attention-table {
    margin-top: 24px;
  }

  .custom-table {
    /deep/ .bk-table-body-wrapper{
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
    }
  }
}
</style>
