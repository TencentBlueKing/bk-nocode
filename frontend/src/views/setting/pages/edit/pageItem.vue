<template>
  <div :class="editor?'field-form-content':''">
    <component
      :is="fieldComp"
      :page="page"
      @change="$emit('change', $event)">
    </component>
  </div>
</template>

<script>
import {  COMPONENT_TYPES, PAGE_TYPE_MAP }  from '@/constants/comps.js';
// 注册fields文件夹下所有字段类型组件
function registerPage() {
  const page = require.context('../components/', false, /\w+\.(vue)$/);
  const components = {};
  page.keys().forEach((fileName) => {
    const componentConfig = page(fileName);
    const comp = componentConfig.default;
    components[comp.name] = comp;
  });
  return components;
}
export default {
  name: 'PageItem',
  props: {
    page: {
      type: Object,
      default: () => ({}),
    },
    editor: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      value: {},
    };
  },
  computed: {
    fieldComp() {
      const type = Object.keys(PAGE_TYPE_MAP).find(key => PAGE_TYPE_MAP[key] === this.page.type);
      return COMPONENT_TYPES.find(item => item.type === type)?.comp;
    },
  },
  beforeCreate() {
    const page = registerPage();
    Object.keys(page).forEach((item) => {
      this.$options.components[item] = page[item];
    });
  },
};
</script>

<style scoped lang="postcss">

</style>
