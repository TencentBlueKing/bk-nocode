const Application = () => import('@/views/application/index.vue');
const List = () => import('@/views/application/list.vue');
const AppDetail = () => import('@/views/application/appDetail.vue');
const AppPageContent = () => import('@/views/application/pageContent.vue');
const CommonCreateTicket = () => import('@/views/application/commonCreateTicket.vue');
const OpenCreatTicket = () => import('@/views/application/createTicket.vue');
export default [
  {
    path: '/app',
    name: 'Application',
    component: Application,
    children: [
      {
        path: 'list/',
        name: 'applicationList',
        component: List,
      },
      {
        path: ':appId/:version/:pageId?/',
        component: AppDetail,
        props: route => ({ appId: route.params.appId, version: route.params.version, pageId: route.params.pageId ? Number(route.params.pageId) : '' }),
        children: [
          {
            path: '',
            name: 'appPageContent',
            component: AppPageContent,
          },
          {
            path: ':funcId/:actionId?',
            name: 'commonCreateTicket',
            component: CommonCreateTicket,
            props: (route) => {
              const { funcId, actionId } = route.params;
              const { actionType, componentId } = route.query;
              return {
                funcId: Number(funcId),
                componentId: Number(componentId),
                actionId,
                actionType,
              };
            },
          },
        ],
      },
    ],
  },
  {
    path: '/form/:token?',
    name: 'openCreatTicket',
    component: OpenCreatTicket,
    props: route => ({ token: route.params.token }),
  },
];
