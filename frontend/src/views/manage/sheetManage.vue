<template>
  <section class="sheet-manage-content">
    <page-wrapper title="表单开放管理">
      <div class="sheet-manage-container">
        <div class="header-search">
          <bk-button theme="primary" icon="plus" @click="handleAddSheet">新增</bk-button>
          <bk-select
            v-model="project_key"
            ext-cls="search-width"
            :placeholder="'请选择应用'"
            @selected="handleSearch"
            @clear="() => initData()"
            searchable
            clearable
           >
            <bk-option v-for="option in appList" :key="option.key" :id="option.key" :name="option.name"></bk-option>
          </bk-select>
          <!--          <bk-input-->
          <!--            class="search-width"-->
          <!--            :placeholder="'请选择应用'"-->
          <!--            :left-icon="'bk-icon icon-search'"-->
          <!--            v-model="project_key"-->
          <!--            @change="handleChange"-->
          <!--            @enter="handlerSearch"-->
          <!--            @right-icon-click="handlerSearch">-->
          <!--          </bk-input>-->
        </div>
        <div class="sheet-manage-table">
          <bk-table
            v-bkloading="{ isLoading: tableLoading }"
            ext-cls="custom-table"
            :data="tableList"
            size="small"
            :outer-border="false"
            :header-border="false"
            :pagination="pagination"
            :max-height="defaultTableHeight"
            @page-change="handlePageChange"
            @page-limit-change="handlePageLimitChange">
            <bk-table-column v-for="field in columnList" :key="field.id" :label="field.label">
              <template slot-scope="{ row }">
                <bk-button
                  v-if="field.id==='operate'"
                  theme="primary"
                  text
                  @click="handleEditor(row)">编辑
                </bk-button>
                <bk-button
                  v-if="field.id==='operate'"
                  theme="primary"
                  text
                  style="margin-left: 8px"
                  @click="handleDelete(row)">删除
                </bk-button>
                <span v-else-if="field.id==='granted_project_name'">
                  {{ row[field.id] && row[field.id].toString() || '--' }}
                </span>
                <span v-else>{{ row[field.id] || '--' }}</span>
              </template>
            </bk-table-column>
          </bk-table>
        </div>
      </div>
    </page-wrapper>
    <bk-dialog
      v-model="AddSheetDialogVisible"
      theme="primary"
      :mask-close="false"
      width="640"
      header-position="left"
      :title="formStatus==='ADD'?'新增开放表单':'编辑'">
      <bk-form :label-width="200" :model="addSheetFormData" form-type="vertical" :rules="rules">
        <bk-form-item label="选择应用" :property="'name'" :required="true" v-if="formStatus==='ADD'">
          <bk-select
            v-model="addSheetFormData.checkApp"
            searchable
            @selected="handleSelect"
            @clear="handleClear">
            <bk-option v-for="option in appList" :key="option.key" :id="option.key" :name="option.name"></bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          label="选择表单"
          :property="'name'"
          :required="true"
          :loading="sheetLoading"
          v-if="formStatus==='ADD'">
          <bk-select v-model="addSheetFormData.checkSheet" :disabled="!addSheetFormData.checkApp" searchable>
            <bk-option v-for="option in sheetList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="开放应用" :property="'name'" :required="true">
          <bk-tag-input
            v-model="addSheetFormData.openApplication"
            :disabled="formStatus==='ADD'&&!addSheetFormData.checkApp"
            :trigger="'focus'"
            save-key="key"
            display-key="name"
            placeholder="请选择开放应用"
            :has-delete-icon="true"
            :list="applicationList">
          </bk-tag-input>
        </bk-form-item>
      </bk-form>
      <div slot="footer" class="king-slider-footer">
        <bk-button theme="primary" @click="onSubmit" :loading="submitPending"> 确定</bk-button>
        <bk-button theme="default" @click="onCancel" style="margin-left: 8px">取消</bk-button>
      </div>
    </bk-dialog>
  </section>
</template>

<script>
import PageWrapper from '@/components/pageWrapper.vue';

const COLUMN_LIST = [
  {
    id: 'project_name',
    label: '应用',
    prop: 'project_name',
    width: '140',
  },
  {
    id: 'worksheet_name',
    label: '表单',
    prop: 'worksheet_name',
    width: '140',
  },
  {
    id: 'granted_project_name',
    label: '开放应用',
    prop: 'granted_project_name',
    width: '140',
  },
  {
    id: 'operate',
    label: '操作',
    minWidth: '80',
    disabled: true,
  },
];
export default {
  name: 'SheetManage',
  components: {
    PageWrapper,
  },
  data() {
    return {
      defaultTableHeight: '',
      project_key: '',
      submitPending: false,
      tableLoading: false,
      sheetLoading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      formStatus: 'ADD',
      tableList: [{}],
      settingList: COLUMN_LIST,
      columnList: COLUMN_LIST,
      visible: false,
      AddSheetDialogVisible: false,
      addSheetFormData: {
        openApplication: [],
        checkSheet: '',
        checkApp: '',
      },
      rules: {
        openApplication: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
        checkSheet: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
        checkApp: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
      appList: [],
      sheetList: [],
      applicationList: [],
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 48;
    this.initData();
    this.getAppList();
    this.getAllAppList();
  },
  methods: {
    async initData(searchParams) {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
      };
      if (searchParams) {
        params.project_key = searchParams;
      }
      console.log(searchParams);
      console.log(params);
      try {
        this.tableLoading = true;
        const res = await this.$store.dispatch('manage/getOpenSheetList', params);
        this.tableList = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },
    async getAppList() {
      try {
        const params = {
          need_page: 0,
        };
        const res = await this.$store.dispatch('setting/getAllApp', params);
        // this.applicationList = res.data;
        this.appList = res.data.filter(item => item.publish_status !== 'UNRELEASED');
      } catch (e) {
        console.error(e);
      } finally {
      }
    },
    async getAllAppList() {
      try {
        const res = await this.$store.dispatch('setting/getAllApp');
        this.applicationList = res.data;
      } catch (e) {
        console.error(e);
      } finally {
      }
    },
    async getFormsList(appId) {
      try {
        this.sheetLoading = true;
        const params = {
          project_key: appId,
          page: 1,
          page_size: 10000,
        };
        const res = await this.$store.dispatch('setting/getFormList', params);
        this.sheetList = res.data.items;
      } catch (e) {
        console.error(e);
      } finally {
        this.sheetLoading = false;
      }
    },
    async addOpenSheetList() {
      const { checkApp, checkSheet, openApplication } = this.addSheetFormData;
      const params = {
        project_key: checkApp,
        value: checkSheet,
        projects: openApplication,
        type: 'WORKSHEET',
      };
      try {
        this.submitPending = true;
        const res = await this.$store.dispatch('manage/addOpenSheetList', params);
        if (res.result) {
          this.$bkMessage({
            message: '新增成功',
            theme: 'success',
          });
          this.addSheetFormData = {};
          this.AddSheetDialogVisible = false;
          this.initData();
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.submitPending = false;
      }
    },
    async deleteOpenSheet(id) {
      const params = {
        id,
      };
      try {
        const res = await this.$store.dispatch('manage/deleteOpenSheetList', params);
        if (res.result) {
          this.$bkMessage({
            message: '删除成功',
            theme: 'success',
          });
          this.initData();
        }
      } catch (e) {
        console.warn(e);
      } finally {
      }
    },
    async updateOpenSheet() {
      const { openApplication, id } = this.addSheetFormData;
      const params = { id,  projects: openApplication };
      try {
        this.submitPending = true;
        const res = await this.$store.dispatch('manage/updateOpenSheetList', params);
        if (res.result) {
          this.$bkMessage({
            message: '修改成功',
            theme: 'success',
          });
          this.AddSheetDialogVisible = false;
          this.addSheetFormData = {};
          this.initData();
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.submitPending = false;
      }
    },
    async handleAddSheet() {
      this.formStatus = 'ADD';
      this.AddSheetDialogVisible = true;
    },
    handleSearch(val) {
      this.initData(val);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.initData();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.initData();
    },
    handleEditor(row) {
      this.formStatus = 'EDIT';
      console.log(row);
      this.addSheetFormData.openApplication = row.granted_project;
      this.addSheetFormData.id = row.id;
      this.AddSheetDialogVisible = true;
    },
    handleClear() {
      this.addSheetFormData.checkSheet = '';
      this.addSheetFormData.openApplication = [];
      this.applicationList = [];
    },
    handleDelete(row) {
      this.$bkInfo({
        title: `此操作将删除访问${row.project_name}对外开发,是否确认？`,
        type: 'warning',
        width: 500,
        confirmFn: async () => {
          await this.deleteOpenSheet(row.id);
        },
      });
    },
    async handleSelect(val) {
      await this.getFormsList(val);
      this.applicationList = this.appList.filter(item => item.key !== val);
    },
    async onSubmit() {
      this.formStatus === 'ADD' ? this.addOpenSheetList() : this.updateOpenSheet();
    },
    onCancel() {
      this.addSheetFormData = {};
      this.AddSheetDialogVisible = false;
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../css/scroller.css";

.sheet-manage-container {
  margin: 24px;
  padding: 24px;
  background: #ffffff;

  .sheet-manage-table {
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
    }
  }
}
</style>
