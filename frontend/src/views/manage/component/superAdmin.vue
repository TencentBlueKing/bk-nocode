<template>
  <div class="list-table">
    <div class="operate-area">
      <bk-button theme="primary" icon="plus" @click="handleAddMember">添加成员</bk-button>
      <bk-input
        v-model.trim="searchStr"
        class="search-input"
        placeholder="请输入成员名称"
        right-icon="bk-icon icon-search"
        :clearable="true"
        @enter="handleSearch"
        @change="handleChange"
        @clear="handleSearchClear">
      </bk-input>
    </div>
    <bk-table
      v-bkloading="{ isLoading: listLoading }"
      :data="listData"
      :outer-border="false"
      :max-height="defaultTableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column show-overflow-tooltip label="成员" prop="username"></bk-table-column>
      <bk-table-column label="操作" :width="120">
        <template slot-scope="props">
          <bk-button :text="true" @click="handleDelete(props.row)">删除</bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
export default {
  name: 'SuperAdmin',
  data() {
    return {
      listLoading: false,
      pagination: {
        current: 1,
        count: 0,
        'limit-list': [10, 30, 50],
        limit: 10,
      },
      formBasic: {
        name: '',
        desc: '',
      },
      basicRules: {
        name: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
      searchStr: '',
      listData: [{}],
      defaultTableHeight: '',
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 50 - 48 - 24 - 76 ;
    this.getFormsList();
  },
  methods: {
    handleChange(val) {
      if (!val) {
        this.pagination.current = 1;
        this.getFormsList();
      }
    },
    handleSearch() {
      this.pagination.current = 1;
      this.getFormsList();
    },
    async getFormsList() {
      try {
        this.listLoading = true;
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.limit,
          username__icontains: this.searchStr,
        };
        const res = await this.$store.dispatch('manage/getSuperAdmin', params);
        this.listData = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.log(e);
      } finally {
        this.listLoading = false;
      }
    },
    handleSearchClear() {
      this.searchStr = '';
      this.pagination.current = 1;
      this.getFormsList();
    },
    handlePageChange(val) {
      this.pagination.current = val;
      this.getFormsList();
    },
    handlePageLimitChange(val) {
      this.pagination.current = 1;
      this.pagination.limit = val;
      this.getFormsList();
    },
    handleAddMember() {
      this.$emit('add');
    },
    handleDelete(row) {
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除超级管理员${row.username}？`,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            const params = {
              action: 'DELETE',
              users: [row.username],
            };
            const res = await this.$store.dispatch('manage/deleteSuperAdmin', params);
            if (res.result) {
              this.$bkMessage({
                message: '删除成功',
                theme: 'success',
              });
              this.getFormsList();
            }
          } catch (e) {
            console.error(e);
          } finally {
            this.appDeletePending = false;
          }
        },
      });
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../css/scroller.css";

/deep/ .bk-table::before {
  height: 0;
}

.list-table {
  background: #ffffff;
  border-radius: 2px;
  /deep/ .bk-table-body-wrapper{
    @mixin scroller;
  }
}

.operate-area {
  position: relative;
  margin-bottom: 24px;
  height: 32px;

  .search-input {
    position: absolute;
    right: 0;
    top: 0;
    width: 240px;
  }
}
</style>
