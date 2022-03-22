export function getFieldConditions(type) {
  if (
    ['STRING', 'TEXT', 'DATE', 'INPUTSELECT', 'SELECT', 'MULTISELECT', 'MEMBER',
      'MEMBERS', 'RICHTEXT', 'DESC', 'LINK',
    ].includes(type)
  ) {
    return [
      { id: '==', name: '等于' },
      // { id: '!=', name: '不等于' },
      { id: 'in', name: '包含' },
      // { id: 'not_in', name: '不包含' },
    ];
  }
  return [
    { id: '==', name: '等于' },
    // { id: '!=', name: '不等于' },
    { id: '>', name: '大于' },
    { id: '<', name: '小于' },
    { id: '>=', name: '大于等于' },
    { id: '<=', name: '小于等于' },
  ];
};
// 页面列表 支持得筛选条件
export function getFieldConditionsInTablePage(type) {
  if (
    ['STRING', 'TEXT', 'DATE', 'INPUTSELECT', 'SELECT', 'MULTISELECT', 'MEMBER',
      'MEMBERS', 'RICHTEXT', 'DESC', 'LINK',
    ].includes(type)
  ) {
    return [
      { id: '==', name: '等于' },
      { id: 'icontains', name: '包含' },
    ];
  }
  return [
    { id: '==', name: '等于' },
    { id: '>', name: '大于' },
    { id: '<', name: '小于' },
    { id: '>=', name: '大于等于' },
    { id: '<=', name: '小于等于' },
  ];
};
