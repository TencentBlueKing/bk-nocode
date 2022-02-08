const Manage = () => import('@/views/manage/index.vue');
const ApiConfig = () => import('@/views/manage/apiConfig.vue');
const OperateLog = () => import('@/views/manage/operateLog.vue');
const AdminSetting = () => import('@/views/manage/adminSetting.vue');
const SheetManage = () => import('@/views/manage/sheetManage.vue');

export default {
  path: '/manage',
  name: 'ManageHome',
  component: Manage,
  children: [
    {
      path: 'apiConfig/',
      name: 'apiConfig',
      component: ApiConfig,
    },
    {
      path: 'operate_log/',
      name: 'operateLog',
      component: OperateLog,
    },
    {
      path: 'adminSetting/',
      name: 'adminSetting',
      component: AdminSetting,
    },
    {
      path: 'sheetManage/',
      name: 'sheetManage',
      component: SheetManage,
    },
  ],
};
