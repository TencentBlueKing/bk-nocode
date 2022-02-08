const Setting = () => import('@/views/setting/index.vue');
const AppList = () => import('@/views/setting/list.vue');
const FormList = () => import('@/views/setting/forms/list.vue');
const FormEdit = () => import('@/views/setting/forms/edit/index.vue');
const FunctionList = () => import('@/views/setting/functions/list.vue');
const FunctionEdit = () => import('@/views/setting/functions/edit/index.vue');
const FunctionBasic = () => import('@/views/setting/functions/edit/basicConfig.vue');
const FunctionFlow = () => import('@/views/setting/functions/edit/flowConfig.vue');
const FunctionAdvanced = () => import('@/views/setting/functions/edit/advancedConfig.vue');
const Page = () => import('@/views/setting/pages/index.vue');
const PermissionTemplate = () => import('@/views/setting/permission/index.vue');
export default [
  {
    path: '/setting',
    component: Setting,
    children: [
      {
        path: '',
        name: 'settingList',
        component: AppList,
      },
      {
        path: ':appId/forms/:version',
        name: 'formList',
        component: FormList,
        props: route => ({ appId: route.params.appId, version: route.params.version }),
      },
      {
        path: ':appId/forms/edit/:version?/:formId?/',
        name: 'formEdit',
        component: FormEdit,
        props: route => ({
          appId: route.params.appId,
          formId: route.params.formId,
          version: route.params.version,
        }),
      },
      {
        path: ':appId/functions/',
        name: 'functionList',
        component: FunctionList,
        props: route => ({ appId: route.params.appId }),
      },
      {
        path: ':appId/functions/:funcId?',
        component: FunctionEdit,
        props: route => ({ appId: route.params.appId, funcId: route.params.funcId }),
        children: [
          {
            path: 'basic/',
            name: 'functionBasic',
            component: FunctionBasic,
          },
          {
            path: 'flow/',
            name: 'functionFlow',
            component: FunctionFlow,
          },
          {
            path: 'advanced/',
            name: 'functionAdvanced',
            component: FunctionAdvanced,
          },
        ],
      },
      {
        path: ':appId/pages/:id?/',
        name: 'pageEdit',
        component: Page,
        props: route => ({ appId: route.params.appId }),
      },
      {
        path: ':appId/permission/',
        name: 'permissionTemplate',
        component: PermissionTemplate,
        props: route => ({ appId: route.params.appId }),
      },
    ],
  },
];
