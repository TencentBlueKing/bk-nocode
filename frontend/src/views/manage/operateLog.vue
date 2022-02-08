<template>
  <section class="manage-operate-log-content">
    <page-wrapper title="操作日志">
      <div class="operate-log-container">
        <bk-form form-type="inline">
          <bk-form-item label="操作人" ext-cls="custom-item">
            <bk-input
              style="width: 200px"
              placeholder="请输入操作人"
              v-model="search.operator__icontains"
              class="search-width"
              clearable
              @clear="handleSearchClear('operator')">
            </bk-input>
          </bk-form-item>
          <bk-form-item label="应用" ext-cls="custom-item">
            <bk-input
              style="width: 200px"
              placeholder="请输入应用"
              v-model="search.project_name"
              class="search-width"
              clearable
              @clear="handleSearchClear('project_name')">
            </bk-input>
          </bk-form-item>
          <bk-form-item label="操作时间" ext-cls="custom-item">
            <bk-date-picker
              class="search-width"
              placeholder="请输入操作时间"
              :value="search.create_at"
              type="daterange"
              @change="onSelectDate"
              @clear="handleSearchClear('create_at')" />
          </bk-form-item>
          <bk-form-item ext-cls="custom-item">
            <bk-button :theme="'primary'" :title="'搜索'" @click="handleSearch"> 搜索</bk-button>
            <bk-button :theme="'default'" :title="'重置'" @click="handleRest" class="rest" style="margin-left: 8px">
              重置
            </bk-button>
          </bk-form-item>
        </bk-form>
        <div class="operate-log-table">
          <bk-table
            v-bkloading="{ isLoading: operateLogLoading }"
            :data="tableList"
            ext-cls="custom-table"
            :size="size"
            :outer-border="false"
            :header-border="false"
            :pagination="pagination"
            :max-height="defaultTableHeight"
            @page-change="handlePageChange"
            @page-limit-change="handlePageLimitChange">
            <bk-table-column type="index" label="顺序" width="60"></bk-table-column>
            <bk-table-column label="应用" prop="project_name"></bk-table-column>
            <bk-table-column label="模块" prop="module"></bk-table-column>
            <bk-table-column label="操作内容" prop="content" :show-overflow-tooltip="true"></bk-table-column>
            <bk-table-column label="操作人" prop="operator"></bk-table-column>
            <bk-table-column label="操作时间" prop="create_at"></bk-table-column>
          </bk-table>
        </div>
      </div>
    </page-wrapper>
  </section>
</template>
<script>
import PageWrapper from '@/components/pageWrapper.vue';

export default {
  name: 'OperateLog',
  components: {
    PageWrapper,
  },
  data() {
    return {
      search: {
        project_name: '',
        operator_icontains: '',
        create_at: '',
      },
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      operateLogLoading: false,
      tableList: [],
      size: 'small',
      defaultTableHeight: '',
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 80 - 24;
  },
  mounted() {
    this.initData();
  },
  methods: {
    handleSearch() {
      const { project_name, operator__icontains, create_at } = this.search;
      // eslint-disable-next-line camelcase
      const start_time = create_at[0] || '';
      // eslint-disable-next-line camelcase
      const end_time = create_at[1] || '';
      this.pagination.current = 1;
      this.initData({ project_name, operator__icontains, start_time, end_time });
    },
    handleRest() {
      this.search = {};
      this.pagination.current = 1;
      this.initData();
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.initData();
    },
    async initData(searchParams) {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        ...searchParams,
      };
      this.operateLogLoading = true;
      try {
        const res = await this.$store.dispatch('manage/getOperateLog', params);
        this.tableList = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.log(e);
      } finally {
        this.operateLogLoading = false;
      }
    },
    onSelectDate(val) {
      this.search.create_at = val;
    },
    handleSearchClear(key) {
      this.search[key] = '';
      this.pagination.current = 1;
      this.handleSearch();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.initData();
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../css/scroller.css';
.operate-log-container {
  background: #fff;
  padding: 24px;
  margin: 24px;

  .custom-table {
    /deep/ .bk-table-body-wrapper{
      @mixin scroller;
    }
  }
  /deep/ .bk-table::before {
    height: 0;
  }

  /deep/ .bk-form.bk-inline-form .bk-label{
    padding: 0 8px 0 0;
  }
  .search-width {
    width: 240px;
  }

  .operate-log-table {
    margin-top: 16px;
  }

  .custom-table {
    max-height: 610px;
  }
}


.custom-item {
  margin-left: 0 !important;
  padding-top: 8px;
  margin-right: 24px !important;
}

.rest {
  margin-left: 8px;
}
</style>
