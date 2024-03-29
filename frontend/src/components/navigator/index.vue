<template>
  <bk-navigation
    header-title="no-code"
    side-title="S-Maker"
    navigation-type="top-bottom"
    :class="showAppSelector ? 'with-app-selector' : ''"
    :default-open="!$store.state.navFolded"
    :need-menu="!!sideMenuList.length"
    @toggle="navFolded = !$event"
    @toggle-click="handleToggleClick">
    <template slot="side-icon">
      <img :src="imgUrl" @click="handleClik"></img>
    </template>
    <template slot="header">
      <ul class="top-entry-list">
        <li v-for="entry in topEntry" :key="entry.id" :class="['entry-item', { active: entry.id === activeEntry }]">
          <router-link :to="entry.path">
            {{ entry.name }}
          </router-link>
        </li>
      </ul>
    </template>
    <template v-if="sideMenuList.length > 0" slot="menu">
      <bk-navigation-menu
        item-active-bg-color="#e1ecff"
        item-active-color="#3a84ff"
        item-default-color="#979ba5"
        item-default-icon-color="#979ba5"
        item-active-icon-color="#3a84ff"
        :toggle-active="true"
        :default-active="activeMenu">
        <app-selector
          v-if="showAppSelector"
          :list="appList"
          :loading="appListLoading"
          :disabled="appListLoading"
          :simple="navFolded"
          :value="$route.params.appId"
          @change="handleAppchange">
        </app-selector>
        <bk-navigation-menu-item
          v-for="menu in sideMenuList"
          :key="menu.id"
          :id="menu.id"
          :has-child="Array.isArray(menu.children) && menu.children.length > 0"
          :icon="menu.icon"
          @click="handleSideRouterClick(menu)">
          {{ menu.name }}
          <div v-if="Array.isArray(menu.children)" slot="child">
            <bk-navigation-menu-item
              v-for="child in menu.children"
              :key="child.id"
              :id="child.id"
              :disabled="child.disabled"
              :icon="child.icon"
              @click="changeNav(child)">
              <span>{{ child.name }}</span>
            </bk-navigation-menu-item>
          </div>
        </bk-navigation-menu-item>
      </bk-navigation-menu>
    </template>
    <slot></slot>
  </bk-navigation>
</template>
<script>
import { APP, WORKBENCH, SETTING, MANAGE } from '@/constants/navMenu.js';
import AppSelector from '../appSelector.vue';

export default {
  name: 'Navigator',
  components: {
    AppSelector,
  },
  data() {
    return {
      topEntry: this.getTopEntry(),
      activeEntry: '',
      activeMenu: '',
      sideMenuList: [],
      appList: [],
      appListLoading: false,
      navFolded: this.$store.state.navFolded,
      imgUrl: require('@/assets/images/logo-smarker.svg'),
    };
  },
  computed: {
    showAppSelector() {
      return this.activeEntry === 'settingHome';
    },
  },
  watch: {
    $route() {
      this.activeEntry = '';
      this.activeMenu = '';
      this.sideMenuList = [];
      this.setNavData();
      if (this.$route.name !== 'settingList' && this.activeEntry === 'settingHome') {
        this.getAppList();
      }
    },
  },
  methods: {
    getTopEntry() {
      let topEntry = [APP, WORKBENCH, SETTING, MANAGE];
      // 非平台管理员需要隐藏「平台管理」的部分侧边栏导航项，如果侧边导航为空，则隐藏「平台管理」
      if (!this.$store.state.isSuperUser) {
        MANAGE.menu = MANAGE.menu.slice(0).filter(item => !['operateLog', 'apiConfig', 'adminSetting'].includes(item.id));
        if (MANAGE.menu.length === 0) {
          topEntry = [APP, WORKBENCH, SETTING];
        } else {
          MANAGE.path = MANAGE.menu[0].path;
        }
      }
      return topEntry;
    },
    async getAppList() {
      try {
        this.appListLoading = true;
        const res = await this.$store.dispatch('setting/getAllApp', { show_type: 'manager_center' });
        this.appList = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.appListLoading = false;
      }
    },
    setNavData() {
      const { name } = this.$route;
      let crtEntry;
      let menulist;
      this.topEntry.some((entry) => {
        crtEntry = entry.id;
        if (entry.id === name) {
          this.activeEntry = crtEntry;
          return true;
        }
        if (Array.isArray(entry.subRoutes) && entry.subRoutes.includes(name)) {
          this.activeEntry = crtEntry;
        }
        if (Array.isArray(entry.menu)) {
          menulist = entry.menu || [];
          return entry.menu.some((m) => {
            if (m.id === name || (Array.isArray(m.subRoutes) && m.subRoutes.includes(name))) {
              this.activeEntry = crtEntry;
              this.activeMenu = m.id;
              this.sideMenuList = menulist;
              return true;
            }
            if (Array.isArray(m.children)) {
              return m.children.some((i) => {
                if (i.id === name || (Array.isArray(i.subRoutes) && i.subRoutes.includes(name))) {
                  this.activeEntry = crtEntry;
                  this.activeMenu = i.id;
                  this.sideMenuList = menulist;
                  return true;
                }
              });
            }
          });
        }
      });
    },
    handleSideRouterClick(menu) {
      if (Array.isArray(menu.children) && menu.children.length > 0) {
        return;
      }
      this.changeNav(menu);
    },
    changeNav(menu) {
      const params = { ...this.$route.params };
      const query = {};
      this.$router.push({ name: menu.id, params, query });
    },
    handleToggleClick(val) {
      this.navFolded = !val;
      localStorage.setItem('nocode_nav_status', val ? 'open' : 'fold');
    },
    handleAppchange(app) {
      const router = this.$router.resolve({ name: 'formList', params: { appId: app.key } });
      window.location.href = router.href;
    },
    handleClik() {
      this.$router.push({ name: 'applicationList' });
    },
  },
};
</script>
<style lang="postcss" scoped>
.top-entry-list {
  display: flex;
  align-items: center;
  .entry-item {
    display: flex;
    align-items: center;
    margin-right: 40px;
    height: 50px;
    font-size: 14px;
    & > a {
      color: #96a2b9;
    }
    &.active > a {
      color: #ffffff;
    }
    &:hover {
      > a {
        color: #d3d9e4;
      }
    }
  }
}
.bk-navigation {
  min-width: 1366px;
  /deep/.bk-navigation-wrapper {
    .navigation-container {
      max-width: none !important;
    }
    .container-content {
      padding: 0;
    }
  }
}
.bk-navigation.with-app-selector /deep/ .nav-slider-list {
  padding-top: 0px;
}
</style>
