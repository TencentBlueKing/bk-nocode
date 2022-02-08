import Vue from 'vue';
import Router from 'vue-router';
import store from '../store/index.js';
import PageNotFound from '@/views/pageNotFound.vue';
import application from './modules/application.js';
import workbench from './modules/workbench.js';
import setting from './modules/setting.js';
import manage from './modules/manage.js';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  base: window.SITE_URL,
  routes: [
    {
      path: '/',
      redirect: { name: 'applicationList' },
    },
    ...application,
    ...workbench,
    ...setting,
    {
      path: '*',
      component: PageNotFound,
    },
  ],
});

// 「平台管理」模块根据用户是否是平台管理员动态添加路由
let manageRouters;
if (store.state.isSuperUser) {
  manageRouters = manage;
} else {
  const accessibleRoutes = manage.children.filter(item => !['apiConfig', 'operateLog', 'adminSetting'].includes(item.name));
  manageRouters = Object.assign({}, manage, { children: accessibleRoutes });
}
router.addRoute(manageRouters);

const originalPush = Router.prototype.push;
Router.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err);
};
export default router;
