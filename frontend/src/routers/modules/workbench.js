const Workbench = () => import('@/views/workbench/index.vue');
const Collection = () => import('@/views/workbench/collection.vue');
const Todo = () => import('@/views/workbench/todo.vue');
const Attention = () => import('@/views/workbench/attention.vue');
const Created = () => import('@/views/workbench/created.vue');
const All = () => import('@/views/workbench/all.vue');
const Approval = () => import('@/views/workbench/approval.vue');
// 开发画页面用
const ProcessDetail = () => import('@/views/workbench/processDetail.vue');

export default [
  {
    path: '/workbench',
    name: 'workbenchHome',
    component: Workbench,
    children: [
      {
        path: 'collection/',
        name: 'collection',
        component: Collection,
      },
      {
        path: 'todo/',
        name: 'todo',
        component: Todo,
      },
      {
        path: 'attention/',
        name: 'attention',
        component: Attention,
      },
      {
        path: 'created/',
        name: 'created',
        component: Created,
      },
      {
        path: 'all/',
        name: 'all',
        component: All,
      },
      {
        path: 'approval/',
        name: 'approval',
        component: Approval,
      },
      {
        path: 'processDetail/:id',
        name: 'processDetail',
        component: ProcessDetail,
        props: route => ({ id: route.params.id }),
      },
    ],
  },
];
