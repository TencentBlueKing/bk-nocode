export const APP = {
  id: 'applicationList',
  name: '应用',
  path: '/app/list/',
  subRoutes: ['appPageContent', 'commonCreateTicket'],
};

export const WORKBENCH = {
  id: 'workbenchHome',
  name: '工作台',
  path: '/workbench/collection/',
  menu: [
    {
      id: 'collection',
      name: '我的收藏',
      icon: 'custom-icon-font icon-function-collection',
      path: '/workbench/collection/',
    },
    {
      id: 'ticket',
      name: '个人中心',
      icon: 'bk-icon icon-user-3',
      children: [
        {
          id: 'todo',
          name: '我的待办',
          path: '/workbench/todo/',
          subRoutes: ['processDetail'],
        },
        {
          id: 'created',
          name: '我发起的',
          path: '/workbench/created/',
          subRoutes: ['processDetail'],
        },
        {
          id: 'attention',
          name: '我关注的',
          path: '/workbench/attention/',
          subRoutes: ['processDetail'],
        },
        {
          id: 'all',
          name: '全部流程',
          path: '/workbench/all/',
          subRoutes: ['processDetail'],
        },
      ],
    },
  ],
};

export const SETTING = {
  id: 'settingHome',
  name: '应用管理',
  path: '/setting/',
  subRoutes: ['settingList'],
  menu: [
    {
      id: 'formList',
      name: '表单管理',
      icon: 'custom-icon-font icon-sheet-manage',
      path: '/forms/',
      subRoutes: ['formEdit'],
    },
    {
      id: 'functionList',
      name: '功能管理',
      icon: 'custom-icon-font icon-function-manage',
      path: '/functions/',
      subRoutes: ['functionBasic', 'functionFlow', 'functionAdvanced'],
    },
    {
      id: 'pageEdit',
      name: '页面管理',
      icon: 'custom-icon-font icon-page-manage',
      path: '/pages/',
    },
    {
      id: 'permissionTemplate',
      name: '权限管理',
      icon: 'custom-icon-font icon-lock-file',
      path: '/permissionTemplate/',
    },
  ],
};

export const MANAGE = {
  id: 'manage',
  name: '平台管理',
  path: '/manage/operate_log/',
  menu: [
    {
      id: 'operateLog',
      name: '操作日志',
      icon: 'custom-icon-font icon-option-log',
      path: '/manage/operate_log/',
    },
    {
      id: 'apiConfig',
      name: 'API配置',
      icon: 'custom-icon-font icon-api-config',
      path: '/manage/apiConfig/',
      children: [],
    },
    {
      id: 'adminSetting',
      name: '管理员设置',
      icon: 'custom-icon-font icon-admin-setting',
      path: '/manage/adminSetting/',
      children: [],
    },
    {
      id: 'sheetManage',
      name: '表单开放管理',
      icon: 'custom-icon-font icon-programmer',
      path: '/manage/sheetManage/',
      children: [],
    },
  ],
};
