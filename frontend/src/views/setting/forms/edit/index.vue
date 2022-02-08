<template>
  <section class="form-edit-page">
    <page-wrapper title="表单设置" :back-icon="true" @back="handleBackClick">
      <div slot="header" class="actions-area">
        <bk-button :disabled="formFieldsSavePending" @click="onResetFormFields">重置</bk-button>
        <bk-button theme="primary" :loading="formFieldsSavePending || checkRelatedPending" @click="handleSaveClick">
          保存
        </bk-button>
      </div>
      <div class="edit-page-main" v-bkloading="{ isLoading: fieldsLoading, zIndex: 10 }">
        <side-panel @move="fieldPanelHover = true" @end="fieldPanelHover = false"></side-panel>
        <div class="form-drag-area">
          <form-panel
            :fields="fieldsList"
            :form-id="formId"
            :hover="fieldPanelHover"
            @add="handleAddField"
            @changeOrder="handleFieldOrderChange"
            @select="handleSelectField"
            @copy="handleCopyField"
            @delete="handleDeleteField">
          </form-panel>
        </div>
        <config-panel :app-id="appId" :field="crtField" :list="fieldsList" @update="updataField"></config-panel>
      </div>
    </page-wrapper>
    <!-- 表单关联页面和功能弹窗 -->
    <bk-dialog
      ok-text="继续"
      :width="800"
      :mask-close="false"
      :value="relatedDataDialogShow"
      @cancel="handleRelatedDataCancel"
      @confirm="handleRelatedDataConfirm">
      <div class="related-data-container">
        <div class="title">
          <i class="bk-icon icon-exclamation warning-icon"></i>
          <span>表单关联的功能和页面：</span>
        </div>
        <bk-table :data="relatedData">
          <bk-table-column label="功能" property="function">
            <template slot-scope="props">
              <div v-if="props.row.function.length > 0" class="link-list">
                <span v-for="(func, index) in props.row.function" class="related-item" :key="func.id">
                  <span v-if="index > 0">、</span>
                  <a
                    target="_blank"
                    :key="func.id"
                    :href="$router.resolve({ name: 'functionFlow', params: { appId, id: func.id } }).href">
                    {{ func.name }}
                  </a>
                </span>
              </div>
              <span v-else>--</span>
            </template>
          </bk-table-column>
          <bk-table-column label="页面" property="page">
            <template slot-scope="props">
              <div v-if="props.row.page.length > 0" class="link-list">
                <span v-for="(page, index) in props.row.page" class="related-item" :key="page.id">
                  <span v-if="index > 0">、</span>
                  <a
                    class="related-item"
                    target="_blank"
                    :key="page.id"
                    :href="$router.resolve({ name: 'pageEdit', params: { appId, id: page.id } }).href">
                    {{ page.name }}
                  </a>
                </span>
              </div>
              <span v-else>--</span>
            </template>
          </bk-table-column>
        </bk-table>
        <p class="tips">表单变更可能会影响到以上功能和页面，建议做好相关维护</p>
      </div>
    </bk-dialog>
  </section>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import PageWrapper from '@/components/pageWrapper.vue';
import SidePanel from './sidePanel.vue';
import FormPanel from './formPanel.vue';
import ConfigPanel from './configPanel.vue';

export default {
  name: 'FormEdit',
  components: { PageWrapper, SidePanel, FormPanel, ConfigPanel },
  props: {
    appId: {
      type: String,
      default: '',
    },
    formId: [Number, String], // 通过路由获取的为字符串
  },
  data() {
    return {
      primaryFields: [], // 用户编辑前字段列表，用户重置还原
      isEdit: false, // 判断用户是否编辑
      fieldsList: [],
      fieldsLoading: false,
      fieldPanelHover: false,
      crtField: {}, // 当前选中字段
      crtIndex: -1, // 当前选中字段索引
      formFieldsSavePending: false,
      checkRelatedPending: false,
      relatedDataDialogShow: false,
      relatedData: [],
    };
  },
  computed: {
    pageType() {
      return this.formId ? 'edit' : 'create';
    },
  },
  created() {
    this.getFormFields();
  },
  methods: {
    async getFormBasic() {
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('setting/getFormBasic', { id: this.formId });
        this.formBasic = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.basicLoading = false;
      }
    },
    async getFormFields() {
      try {
        this.fieldsLoading = true;
        this.$emit('loading', true);
        const res = await this.$store.dispatch('setting/getFormFields', this.formId);
        this.fieldsList = res.data;
        this.primaryFields = cloneDeep(this.fieldsList);
      } catch (e) {
        console.error(e);
      } finally {
        this.fieldsLoading = false;
        this.$emit('loading', false);
      }
    },
    // 添加字段
    handleAddField(field, index) {
      this.isEdit = true;
      this.fieldsList.splice(index, 0, field);
      this.crtField = field;
      this.crtIndex = index;
    },
    // 拖拽字段顺序
    handleFieldOrderChange(newIndex, oldIndex) {
      this.isEdit = true;
      const field = this.fieldsList.splice(oldIndex, 1);
      this.fieldsList.splice(newIndex, 0, field[0]);
      this.crtIndex = newIndex;
      this.crtField = cloneDeep(this.fieldsList[newIndex]);
    },
    // 选中字段
    handleSelectField(field, index) {
      this.crtField = field;
      this.crtIndex = index;
    },
    // 复制字段
    handleCopyField(field, index) {
      this.isEdit = true;
      this.fieldsList.splice(index + 1, 0, field);
      this.crtField = field;
      this.crtIndex = index + 1;
    },
    // 删除字段
    handleDeleteField(index) {
      this.isEdit = true;
      this.fieldsList.splice(index, 1);
      if (this.crtIndex === index) {
        this.crtIndex = -1;
      }
    },
    // 配置字段属性
    updataField(val) {
      this.isEdit = true;
      this.crtField = val;
      this.fieldsList.splice(this.crtIndex, 1, val);
    },
    async handleSaveClick() {
      if (this.checkRelatedPending || this.formFieldsSavePending) {
        return;
      }
      try {
        this.checkRelatedPending = true;
        const res = await this.$store.dispatch('setting/getRelatedFuncAndPage', this.formId);
        const { relate_list_page, relate_service } = res.data;
        if (relate_list_page.length === 0 && relate_service.lenght === 0) {
          this.onSaveFormFields();
        } else {
          this.relatedData = [{ page: relate_list_page, function: relate_service }];
          this.relatedDataDialogShow = true;
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.checkRelatedPending = false;
      }
    },
    handleRelatedDataConfirm() {
      this.relatedDataDialogShow = false;
      this.relatedData = [];
      this.onSaveFormFields();
    },
    handleRelatedDataCancel() {
      this.relatedDataDialogShow = false;
      this.relatedData = [];
    },
    // 保存表单字段
    async onSaveFormFields() {
      try {
        this.formFieldsSavePending = true;
        const params = {
          worksheet_id: this.formId,
          fields: this.fieldsList,
        };
        const res = await this.$store.dispatch('setting/batchSaveFields', params);
        if (res.result) {
          this.fieldsList = res.data;
          this.primaryFields = cloneDeep(this.fieldsList);
          this.$bkMessage({
            theme: 'success',
            message: '保存成功',
          });
          this.isEdit = false;
        }
      } catch (error) {
        console.error(error);
      } finally {
        this.formFieldsSavePending = false;
      }
    },
    onResetFormFields() {
      this.isEdit = true;
      this.fieldsList = cloneDeep(this.primaryFields);
    },
    // 接口数据部分字段类型转换为本地需要类型
    transApiToLocal(data) {
      const { choice, meta } = data;
      let { default: defaultVal } = data;
      if (['MULTISELECT', 'CHECKBOX'].includes(data.type)) {
        defaultVal = JSON.parse(defaultVal);
      }
      return {
        ...data,
        choice,
        meta,
        default: defaultVal,
      };
    },
    handleBackClick() {
      if (this.isEdit) {
        this.$bkInfo({
          title: '此操作会导致您的编辑没有保存，确认吗？',
          type: 'warning',
          width: 500,
          confirmFn: () => {
            this.$router.push({ name: 'formList', params: { appId: this.appId } });
          },
        });
      } else {
        this.$router.push({ name: 'formList', params: { appId: this.appId } });
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
/deep/ .page-header-container {
  display: flex;
  justify-content: space-between;
}
.edit-page-main {
  display: flex;
  justify-content: space-between;
  height: 100%;
}
.side-panel {
}
.form-drag-area {
  width: calc(100% - 600px);
  height: 100%;
  overflow: hidden;
}
.actions-area {
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  .bk-button {
    margin-left: 8px;
    min-width: 88px;
  }
}
.related-data-container {
  .title {
    display: flex;
    align-items: center;
    margin-bottom: 18px;
    font-size: 16px;
    color: #313238;
  }
  .warning-icon {
    margin-right: 10px;
    width: 24px;
    height: 24px;
    line-height: 24px;
    background-color: #ffe8c3;
    color: #ff9c01;
    font-size: 14px;
    border-radius: 50%;
  }
  /deep/ .bk-table {
    tbody .cell {
      -webkit-line-clamp: unset;
    }
  }
  .link-list {
    padding: 8px 0;
    word-break: break-word;
    .related-item {
      font-size: 12px;
      & > a {
        color: #3a84ff;
      }
    }
  }
  .tips {
    margin-top: 24px;
    font-size: 12px;
    color: #63656e;
  }
}
</style>
