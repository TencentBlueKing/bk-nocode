<template>
  <div class="list-table">
    <div class="operate-area">
      <bk-input
        v-model.trim="searchStr"
        class="search-input"
        placeholder="请输入应用名称"
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
      :pagination="pagination"
      @page-change="handlePageChange"
      :max-height="defaultTableHeight"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column show-overflow-tooltip label="应用" prop="name"></bk-table-column>
      <bk-table-column show-overflow-tooltip label="应用开发管理员">
        <template slot-scope="{ row,$index }">
          <div v-if="ownerEditIndex!==$index" class="editor-container">
            <span>{{ row.owner && row.owner.toString() || '--' }}</span>
            <bk-spin class="pending-icon" size="mini" v-if="pending"></bk-spin>
            <i class="bk-icon icon-edit-line edit-icon" @click="handleEditOwner($index)"></i>
          </div>
          <div v-else-if="ownerEditIndex===$index">
            <member-select
              v-bk-clickoutside="handleSave"
              ext-cls="members-editor"
              v-model="row.owner"
              :multiple="true">
            </member-select>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column show-overflow-tooltip label="应用数据管理员">
        <template slot-scope="{ row,$index }">
          <div v-if="dataEditIndex!==$index" class="editor-container">
            <span>{{ row.data_owner && row.data_owner.toString() || '--' }}</span>
<!--            <bk-spin class="pending-icon" size="mini"></bk-spin>-->
            <i class="bk-icon icon-edit-line edit-icon" @click="handleEditData($index)"></i>
          </div>
          <div v-else-if="dataEditIndex===$index">
            <member-select
              v-bk-clickoutside="handleDataOwnerSave"
              ext-cls="members-editor"
              v-model="row.data_owner"
              :multiple="true">
            </member-select>
          </div>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import memberSelect from '@/components/memberSelect.vue';
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'ApplicationAdmin',
  components: {
    memberSelect,
  },
  data() {
    return {
      dataEditIndex: -1,
      ownerEditIndex: -1,
      pending: false,
      arr: [],
      listLoading: false,
      members: [1, 2, 3],
      pagination: {
        current: 1,
        count: 0,
        'limit-list': [10, 20, 50],
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
      listData: [],
      defaultTableHeight: '',
      localListData: [],
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 50 - 48 - 24 - 76 - 32;
    this.getAppList();
  },
  methods: {
    async getAppList() {
      try {
        this.listLoading = true;
        const params = {
          show_type: 'manager_center',
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        if (this.searchValue !== '') {
          params.name__icontains = this.searchStr;
        }
        const res = await this.$store.dispatch('setting/getAppList', params);
        this.listData = res.data.items;
        this.localListData = cloneDeep(res.data.items);
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.error(e);
      } finally {
        this.listLoading = false;
      }
    },
    handleSearch() {
      this.pagination.current = 1;
      this.getAppList();
    },
    // 应用管理员保存
    async handleSave() {
      this.pending = true;
      const params = {
        users: this.listData[this.ownerEditIndex].owner,
        action: 'ADD',
        project_key: this.listData[this.ownerEditIndex].project_config.project_key,
      };
      try {
        const res =  await this.$store.dispatch('manage/addApplicationAdmin', params);
        this.localListData[this.ownerEditIndex].owner = res.data.owner.users;
      } catch (e) {
        this.listData = cloneDeep(this.localListData);
        console.error(e);
      } finally {
        this.pending = false;
        this.ownerEditIndex = -1;
      }
    },
    async handleDataOwnerSave() {
      const params = {
        users: this.listData[this.dataEditIndex].data_owner,
        action: 'ADD',
        project_key: this.listData[this.dataEditIndex].project_config.project_key,
      };
      try {
        const res = await this.$store.dispatch('manage/addApplicationDataAdmin', params);
        this.localListData[this.dataEditIndex].data_owner = res.data.data_owner;
      } catch (e) {
        this.listData = cloneDeep(this.localListData);
        console.log(e);
      } finally {
        this.dataEditIndex = -1;
      }
    },
    handleSearchClear() {
      this.searchStr = '';
      this.pagination.current = 1;
      this.getAppList();
    },
    handlePageChange(val) {
      this.pagination.current = val;
      this.getAppList();
    },
    handlePageLimitChange(val) {
      this.pagination.current = 1;
      this.pagination.limit = val;
      this.getAppList();
    },
    handleAddMember(row) {
      this.$emit('addApp', row);
    },
    handleChange(val) {
      if (!val) {
        this.getAppList();
      }
    },
    handleEditOwner(index) {
      this.ownerEditIndex = index;
    },
    handleEditData(index) {
      this.dataEditIndex = index;
    },

  },
};
</script>

<style scoped lang="postcss">
@import "../../../css/scroller.css";

/deep/ .bk-table {
  .cell {
    overflow: unset;
  }

  ::before {
    height: 0;
  }
}

.list-table {
  background: #ffffff;
  border-radius: 2px;

  /deep/ .bk-table-body-wrapper {
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

.bk-icon {
  margin-right: 16px;

  &:hover {
    color: #3a84ff;
    cursor: pointer;
  }
}

.save-icon {
  margin-right: 4px;
  font-size: 16px;
  color: #2dcb56;

  &:hover {
    color: #2dcb56;
  }
}

.members-editor {
  width: 320px;
}

.editor-container {
  position: relative;
  padding-right: 20px;

  &:hover {
    .edit-icon {
      display: inline-block;
    }
  }

  .edit-icon {
    display: none;
    position: absolute;
    top: 2px;
    right: 0;
    font-size: 14px;
    cursor: pointer;

    &:hover {
      color: #3a84ff;
    }
  }
}

.pending-icon {
  position: absolute;
  top: 2px;
  right: 0;
}
</style>
