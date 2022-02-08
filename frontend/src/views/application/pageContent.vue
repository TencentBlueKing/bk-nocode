<template>
  <div class="app-page-container" v-bkloading="{ isLoading: pageConfigLoading, zindex: 999 }">
    <div v-if="crtPage.type === 'SHEET' && pageConfig.length > 0" class="form-page-container">
      <create-ticket
        ref="formPage"
        :app-id="appId"
        :app-name="appName"
        :func-id="Number(pageConfig[0].value)"
        :component-id="pageConfig[0].id"
        :page="crtPage"
        :version="version"
        :actions-perm-map="actionsPermMap">
      </create-ticket>
    </div>
    <function-card-page
      v-if="crtPage.type === 'FUNCTION'"
      :app-id="appId"
      :app-name="appName"
      :version="version"
      :page="crtPage"
      :cards="pageConfig"
      :actions-perm-map="actionsPermMap">
    </function-card-page>
    <table-page
      v-if="crtPage.type === 'LIST' && pageConfig.length !== 0"
      :app-id="appId"
      :app-name="appName"
      :version="version"
      :page="crtPage"
      :component-id="pageConfig[0].id"
      :form-id="pageConfig[0].value"
      :config="pageConfig[0].config"
      :actions-perm-map="actionsPermMap"
      @isFinishLoading="onLoadingIsFinish">
    </table-page>
  </div>
</template>
<script>
import FunctionCardPage from './components/functionCardPage.vue';
import TablePage from './components/tablePage.vue';
import CreateTicket from './components/createTicket.vue';

export default {
  name: 'PageContent',
  components: {
    FunctionCardPage,
    TablePage,
    CreateTicket,
  },
  props: {
    appId: String,
    appName: String,
    version: String,
    crtPage: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      pageConfig: [],
      pageConfigLoading: true,
      actionsPermMap: {},
      actionsPermLoading: true,
    };
  },
  watch: {
    crtPage(val) {
      if (val.type) {
        this.pageConfig = [];
        this.getPageConfig();
        this.getPageActionsPerm();
      }
    },
  },
  created() {
    if (this.crtPage.type) {
      this.getPageConfig();
      this.getPageActionsPerm();
    }
  },
  methods: {
    async getPageConfig() {
      try {
        this.pageConfigLoading = true;
        const params = {
          project_key: this.appId,
          version_number: this.version,
          page_id: this.crtPage.id,
        };
        const res = await this.$store.dispatch('application/getPageConfig', params);
        res.data.forEach(item => (item.collected = item.is_collection));
        this.pageConfig = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.pageConfigLoading = false;
      }
    },
    async getPageActionsPerm() {
      try {
        this.actionsPermLoading = true;
        const params = {
          project_key: this.appId,
          page_id: this.crtPage.id,
        };
        const res = await this.$store.dispatch('permission/getPageActionPerm', params);
        this.actionsPermMap = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.actionsPermLoading = false;
      }
    },
    onLoadingIsFinish() {
      if (this.pageConfigLoading) {
        this.pageConfigLoading = false;
      }
    },
    getFormNeedConfirmState() {
      return this.$refs.formPage && this.$refs.formPage.needLeaveConfirm;
    },
  },
  beforeRouteLeave(to, from, next) {
    if (this.crtPage.type === 'SHEET' && this.pageConfig.length > 0 && this.getFormNeedConfirmState()) {
      this.$bkInfo({
        title: '此操作会导致您的编辑没有保存，确认吗？',
        type: 'warning',
        width: 500,
        confirmFn: () => {
          next();
        },
      });
    } else {
      next();
    }
  },
};
</script>
<style lang="postcss" scoped>
.app-page-container {
  height: 100%;
  overflow: hidden;
  .form-page-container {
    margin: 24px 24px 0;
    height: calc(100% - 48px);
    background: #ffffff;
    box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
    border-radius: 2px;
    overflow: auto;
  }
}
</style>
