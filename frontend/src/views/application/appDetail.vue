<template>
  <div class="app-detail-page">
    <div class="page-navi-area">
      <page-navi :list="pageList" :crt-page="crtPage" @appListLoaded="appList = $event" @select="handleSelectPage">
      </page-navi>
    </div>
    <page-wrapper
      class="page-content-area"
      :title="curName"
      :back-icon="$route.name === 'commonCreateTicket'"
      @back="updateUrl">
      <template v-if="crtPage.id">
        <router-view
          v-if="crtPage.canView"
          ref="pageComp"
          :app-id="appId"
          :app-name="appName"
          :version="version"
          :page-id="pageId"
          :crt-page="crtPage">
        </router-view>
        <apply-perm-page v-else class="apply-page-view-perm" :permission-data="permissionData"> </apply-perm-page>
      </template>
    </page-wrapper>
  </div>
</template>
<script>
import permission from '@/components/permission/mixins.js';
import PageWrapper from '@/components/pageWrapper.vue';
import PageNavi from './components/pageNavi.vue';
import ApplyPermPage from '@/components/permission/applyPage.vue';

export default {
  name: 'AppDetail',
  components: {
    PageWrapper,
    PageNavi,
    ApplyPermPage,
  },
  mixins: [permission],
  props: {
    appId: String,
    version: String,
    pageId: [String, Number],
  },
  data() {
    return {
      appList: [],
      pageList: [],
      pageDataLoading: true,
      crtPage: {},
      permissionData: {},
    };
  },
  computed: {
    appName() {
      const appData = this.appList.find(item => item.key === this.appId);
      return appData ? appData.name : '';
    },
    curName() {
      return `${this.crtPage.name}${this.$route.params.actionName ? `/${this.$route.params.actionName}` : ''}`;
    },
  },
  watch: {
    crtPage(val) {
      const { canView, name, id } = val;
      if (id && !canView) {
        this.permissionData = {};
        const resource = {
          page: [{ id: this.pageId, name }],
          project: [{ id: this.appId, name: this.appName }],
        };
        this.permissionData = this.getPermissionData(['page_view'], [], resource);
      }
    },
  },
  created() {
    this.getPageData();
  },
  methods: {
    async getPageData() {
      try {
        this.pageDataLoading = true;
        const params = {
          project_key: this.appId,
          version_number: this.version,
        };
        const res = await Promise.all([
          this.$store.dispatch('permission/getPagePerm', { project_key: this.appId }),
          this.$store.dispatch('application/getPageList', params),
        ]);
        const [pagePerm, pageList] = res;
        this.pageList = pageList.data.children.map((item) => {
          if (item.type === 'GROUP') {
            item.children.forEach((page) => {
              page.canView = pagePerm.data[page.id] === true;
            });
          } else {
            item.canView = pagePerm.data[item.id] === true;
          }
          return item;
        });
        this.setDefaultCrtPage();
      } catch (e) {
        console.error(e);
      } finally {
        this.pageDataLoading = false;
      }
    },
    // 设置当前选中页面
    setDefaultCrtPage() {
      if (this.pageList.length > 0) {
        if (this.pageId) {
          this.crtPage = this.findPage(this.pageId); // URL参数带页面id
        } else {
          // URL 参数不带页面id默认选中第一个非分组页面
          this.pageList.some((item) => {
            if (item.type === 'GROUP') {
              if (item.children.length > 0) {
                this.crtPage = item.children[0];
                return true;
              }
            } else {
              this.crtPage = item;
              return true;
            }
          });
          this.updateUrl();
        }
      }
    },
    findPage(id) {
      let page;
      this.pageList.some((item) => {
        if (id === item.id) {
          if (item.type === 'GROUP') {
            if (item.children.length > 0) {
              [page] = item.children;
              return true;
            }
          } else {
            page = item;
            return true;
          }
        } else if (item.type === 'GROUP') {
          return item.children.some((p) => {
            if (id === p.id) {
              page = p;
              return true;
            }
          });
        }
      });
      return page;
    },
    updateUrl() {
      this.$router.push({
        name: 'appPageContent',
        params: { appId: this.appId, version: this.version, pageId: this.crtPage.id },
      });
    },
    handleSelectPage(val) {
      this.crtPage = val;
      this.updateUrl();
    },
  },
};
</script>
<style lang="postcss" scoped>
.app-detail-page {
  height: calc(100vh - 52px);
  overflow: hidden;
}
.page-navi-area {
  float: left;
  position: relative;
  width: 240px;
  height: 100%;
  z-index: 100;
}
.page-content-area {
  margin-left: 240px;
}
</style>
