<template>
  <section class="page-edit-page" v-bkloading="{ isLoading: pageComponentLoading }">
    <page-wrapper title="页面管理" :back-icon="true" @back="handleBackClick">
      <!--      <quick-entrance></quick-entrance>-->
      <div class="edit-page-main">
        <!--组件区域-->
        <component-panel @move="fieldPanelHover = true" @end="fieldPanelHover = false"></component-panel>
        <!--画布区域-->
        <page-panel
          @add="handleAddComp"
          :page-list="pageList"
          @select="handleSelectField"
          @copy="handleCopyField"
          @delete="handleDeleteField">
        </page-panel>
        <!--设置区域-->
        <setting-panel :page="crtPage" @update="handleUpdate"></setting-panel>
        <div class="bottom-container">
          <bk-button
            class="btn-save"
            theme="primary"
            title="保存"
            :loading="pageComponentSaving"
            @click="handleSave">
            保存
          </bk-button>
          <!--          <bk-button-->
          <!--            style="margin-left: 8px"-->
          <!--            type="submit"-->
          <!--            :title="'基础按钮'">-->
          <!--            重置-->
          <!--          </bk-button>-->
        </div>
      </div>
    </page-wrapper>
  </section>
</template>

<script>
import PageWrapper from '@/components/pageWrapper.vue';
import componentPanel from './componentPanel.vue';
import pagePanel from './pagePanel.vue';
import settingPanel from './settingPanel.vue';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'CustomPage',
  components: {
    PageWrapper,
    componentPanel,
    pagePanel,
    settingPanel,
  },
  props: {
    appId: String,
    pageId: String,
  },
  data() {
    return {
      isEdit: false,
      fieldPanelHover: false,
      pageList: [],
      pageComponentSaving: false,
      pageComponentLoading: false,
      crtPage: {}, // 当前选中组件
    };
  },
  async created() {
    if (this.pageId) {
      await  this.getPageComponent();
    }
  },
  methods: {
    async getPageComponent() {
      try {
        this.pageComponentLoading = true;
        const res = await this.$store.dispatch('setting/getPageComponent', {
          page_id: this.pageId,
          page_size: 1000,
        });
        this.pageList = res.data.items;
      } catch (e) {
        console.error(e);
      } finally {
        this.pageComponentLoading = false;
      }
    },
    handleBackClick() {
      if (this.isEdit) {
        this.$bkInfo({
          title: '此操作会导致您的编辑没有保存，确认吗？',
          type: 'warning',
          width: 500,
          confirmFn: () => {
            this.$router.push({ name: 'pageEdit', params: { appId: this.appId } });
          },
        });
      } else {
        this.$router.push({ name: 'pageEdit', params: { appId: this.appId } });
      }
    },
    handleAddComp(page, index) {
      console.log(page, index);
      this.isEdit = true;
      this.pageList.splice(index, 0, page);
      this.crtPage = page;
      this.crtIndex = index;
    },
    // 选中字段
    handleSelectField(page, index) {
      this.crtPage = page;
      this.crtIndex = index;
    },
    // 复制字段
    handleCopyField(field, index) {
      this.isEdit = true;
      this.pageList.splice(index + 1, 0, field);
      this.crtPage = field;
      this.crtIndex = index + 1;
    },
    // 删除字段
    handleDeleteField(index) {
      this.isEdit = true;
      this.pageList.splice(index, 1);
      if (this.crtIndex === index) {
        this.crtIndex = -1;
      }
    },
    handleUpdate(val) {
      this.isEdit = true;
      this.crtPage = val;
      this.pageList.splice(this.crtIndex, 1, val);
    },
    async handleSave() {
      const components = this.pageList.map(item => ({ ...item, page_id: this.pageId }));
      const params = {
        page_id: this.pageId,
        components,
      };
      try {
        this.pageComponentSaving = true;
        await this.$store.dispatch('setting/batchSaveComponent', params);
        this.$bkMessage({
          message: '保存成功',
          theme: 'success',
        });
        this.isEdit = false;
      } catch (e) {
        console.log(e);
      } finally {
        this.pageComponentSaving = false;
      }
    },
  },
};
</script>

<style scoped lang="postcss">
.edit-page-main {
  display: flex;
  justify-content: space-between;
  height: 100%;
  position: relative;
}

.bottom-container {
  position: absolute;
  bottom: 0;
  left: 240px;
  width: calc(100% - 240px);
  height: 56px;
  line-height: 56px;
  border-top: 1px solid #dcdee5;
  background: #fafbfd;
}

.btn-save {
  margin-left: 24px;
}
</style>
