import Vue from 'vue';
import Vuex from 'vuex';
import common from './modules/common.js';
import manage from './modules/manage';
import setting from './modules/setting';
import workbench from './modules/workbench';
import application from './modules/application.js';
import permission from './modules/permission.js';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    common,
    manage,
    setting,
    workbench,
    application,
    permission,
  },
  state: {
    isSuperUser: window.is_superuser === 'true',
    allPersonList: [],
    navFolded: localStorage.getItem('nocode_nav_status') === 'fold', // 左侧导航展开、收起状态，open、fold
  },
  mutations: {},
  actions: {},
});
