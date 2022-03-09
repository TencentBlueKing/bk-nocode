<template>
  <section class="forms-list-page">
    <page-wrapper title="表单管理">
      <div class="list-table">
        <div class="operate-area">
          <bk-button theme="primary" icon="plus" @click="onCreateForm">新建</bk-button>
          <bk-input
            v-model.trim="searchStr"
            class="search-input"
            placeholder="请输入表单名称"
            right-icon="bk-icon icon-search"
            :clearable="true"
            @change="handleSearchStrChange"
            @enter="handleSearch"
            @clear="handleSearchClear">
          </bk-input>
        </div>
        <bk-table
          ext-cls="custom-table"
          v-bkloading="{ isLoading: listLoading }"
          :data="listData"
          :outer-border="false"
          :pagination="pagination"
          @page-change="handlePageChange"
          :max-height="defaultTableHeight"
          @page-limit-change="handlePageLimitChange">
          <bk-table-column label="No." prop="id" :width="80"></bk-table-column>
          <bk-table-column show-overflow-tooltip label="表单名称" prop="name">
            <template slot-scope="props">
              <div v-if="!props.row.nameEditing" class="name-wrapper">
                <div class="form-name">{{ props.row.name }}</div>
                <bk-spin v-if="props.row.namePending" class="pending-icon" size="mini"></bk-spin>
                <i v-else class="bk-icon icon-edit-line edit-icon" @click="handleFormEdit($event, props.row)"></i>
              </div>
              <bk-input v-else v-model="props.row.name" @blur="handleFormSave(props.row)"> </bk-input>
            </template>
          </bk-table-column>
          <bk-table-column show-overflow-tooltip label="表单标识" prop="key"></bk-table-column>
          <bk-table-column show-overflow-tooltip label="表单说明">
            <template slot-scope="props">
              <div v-if="!props.row.descEditing" class="desc-wrapper">
                <div class="form-name">{{ props.row.desc || '--' }}</div>
                <bk-spin v-if="props.row.descPending" class="pending-icon" size="mini"></bk-spin>
                <i v-else class="bk-icon icon-edit-line edit-icon" @click="handleFormEdit($event, props.row, 'desc')">
                </i>
              </div>
              <bk-input
                v-else
                v-model="props.row.desc"
                @blur="handleFormSave(props.row, 'desc')">
              </bk-input>
            </template>
          </bk-table-column>
          <bk-table-column label="创建人" prop="creator" :width="100"></bk-table-column>
          <bk-table-column label="创建时间" prop="create_at" :width="160"></bk-table-column>
          <bk-table-column label="操作" :width="120" fixed="right">
            <template slot-scope="props">
              <bk-button :text="true" @click="onEditForm(props.row)">编辑</bk-button>
              <bk-button :text="true" @click="onDeleteForm(props.row)" style="margin-left: 12px">删除</bk-button>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </page-wrapper>
    <bk-dialog
      title="新建表单"
      header-position="left"
      :mask-close="false"
      :auto-close="false"
      :width="640"
      :loading="createFormPending"
      :value="createFormDialogShow"
      @confirm="onCreateFormConfirm"
      @cancel="onCreateFormCancel">
      <div class="form-basic-info">
        <bk-form ref="basicInfo" form-type="vertical" :rules="basicRules" :model="formBasic">
          <bk-form-item label="表单名称" property="name" :required="true" :error-display-type="'normal'">
            <bk-input v-model.trim="formBasic.name"></bk-input>
          </bk-form-item>
          <bk-form-item label="表单描述" property="desc" :error-display-type="'normal'">
            <bk-input type="textarea" :rows="7" v-model.trim="formBasic.desc"></bk-input>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </section>
</template>
<script>
import PageWrapper from '@/components/pageWrapper.vue';

export default {
  name: 'FormList',
  components: { PageWrapper },
  props: {
    appId: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      listData: [],
      listLoading: false,
      searchStr: '',
      createFormDialogShow: false,
      createFormPending: false,
      formDeletePending: false,
      formBasic: {
        name: '',
        desc: '',
      },
      basicRules: {
        name: [
          {
            required: true,
            message: '表单名称为必填项',
            trigger: 'blur',
          },
        ],
      },
      pagination: {
        current: 1,
        count: 0,
        'limit-list': [15, 30, 50],
        limit: 15,
      },
      defaultTableHeight: '',
    };
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 80 - 24;
    this.getFormsList();
  },
  methods: {
    async getFormsList() {
      try {
        this.listLoading = true;
        const params = {
          project_key: this.appId,
          page: this.pagination.current,
          page_size: this.pagination.limit,
        };
        if (this.searchStr) {
          params.name__icontains = this.searchStr;
        }
        const res = await this.$store.dispatch('setting/getFormList', params);
        this.listData = res.data.items.map(item => Object.assign(item, {
          nameEditing: false,
          namePending: false,
          descEditing: false,
          descPending: false,
        }));
        this.pagination.count = res.data.count;
      } catch (e) {
        console.error(e);
      } finally {
        this.listLoading = false;
      }
    },
    handleSearchStrChange(val) {
      if (!val) {
        this.handleSearch();
      }
    },
    handleSearch() {
      this.pagination.current = 1;
      this.getFormsList();
    },
    handleSearchClear() {
      this.searchStr = '';
      this.pagination.current = 1;
      this.getFormsList();
    },
    async handleFormSave(form, type = 'name') {
      try {
        if (type === 'name') {
          form.nameEditing = false;
          form.namePending = true;
        } else {
          form.descEditing = false;
          form.descPending = true;
        }
        const { id, name, desc, project_key } = form;
        const params = {
          id,
          data: { name, desc, project_key },
        };
        await this.$store.dispatch('setting/updateForm', params);
      } catch (e) {
        console.error(e);
      } finally {
        if (type === 'name') {
          form.namePending = false;
        } else {
          form.descPending = false;
        }
      }
    },
    // 点击编辑名称按钮，输入框focus
    handleFormEdit(e, form, type = 'name') {
      const $parentEl = e.target.parentElement.parentElement;
      if (type === 'name') {
        form.nameEditing = true;
      } else {
        form.descEditing = true;
      }
      this.$nextTick(() => {
        const selector = 'input';
        const $el = $parentEl.querySelector(selector);
        $el && $el.focus();
      });
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
    onCreateForm() {
      this.formBasic = { name: '', desc: '' };
      this.createFormDialogShow = true;
    },
    onEditForm(form) {
      const { version } = this.$route.params;
      this.$router.push({ name: 'formEdit', params: { appId: this.appId, formId: form.id, version } });
    },
    onDeleteForm(form) {
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除表单：${form.name}？`,
        confirmLoading: true,
        confirmFn: async () => {
          if (this.formDeletePending) {
            return;
          }
          try {
            this.formDeletePending = true;
            await this.$store.dispatch('setting/deleteForm', form.id);
            if (this.listData.length === 1 && this.pagination.current > 1) {
              this.pagination.current -= 1;
            }
            this.getFormsList();
          } catch (e) {
            console.error(e);
          } finally {
            this.formDeletePending = false;
          }
        },
      });
    },
    onCreateFormConfirm() {
      this.createFormPending = true;
      this.$refs.basicInfo
        .validate()
        .then(async () => {
          try {
            const params = {
              ...this.formBasic,
              project_key: this.appId,
            };
            const resp = await this.$store.dispatch('setting/createForm', params);
            this.formBasic = { name: '', desc: '' };
            this.$router.push({ name: 'formEdit', params: { appId: this.appId, formId: resp.data.id } });
          } catch (e) {
            console.error(e);
          } finally {
            this.createFormPending = false;
          }
        })
        .catch(() => {
          this.createFormPending = false;
        });
    },
    onCreateFormCancel() {
      this.createFormDialogShow = false;
      this.$refs.basicInfo.clearError();
      this.formBasic = { name: '', desc: '' };
    },
  },
};
</script>
<style lang="postcss" scoped>
@import "../../../css/scroller.css";
.list-table {
  margin: 24px;
  padding: 24px;
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;
  /deep/ .bk-table-body-wrapper{
    @mixin scroller;
  }
  /deep/ .bk-table {
    &::before {
      height: 0;
    }
  }
}
.operate-area {
  position: relative;
  margin-bottom: 24px;
  .search-input {
    position: absolute;
    right: 0;
    top: 0;
    width: 240px;
  }
}
.name-wrapper,
.desc-wrapper {
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
  .pending-icon {
    position: absolute;
    top: 2px;
    right: 0;
  }
}
.desc-edit-textarea {
  position: absolute;
  top: 10px;
  left: 15px;
  z-index: 1;
}
</style>
