<template>
  <div class="custom-page-container">
      <div v-for="(page,index) in pageList"
           :key="`${page.type}_${index}`"
           :class="['page-element',layoutMap[page.layout.lineLayout]]">
          <page-item :page="page" :editor="false"></page-item>
      </div>
  </div>
</template>

<script>
import pageItem from './edit/pageItem.vue';
const LAYOUT_MAP = {
  COL_3: 'half-row',
  COL_6: 'half-row',
  COL_9: 'three-fourths-row',
};
export default {
  name: 'ShowCustomPage',
  components: {
    pageItem,
  },
  props: {
    pageList: {
      type: Array,
      default: () => ({}),
      appId: String,
      appName: String,
      version: String,
    },
  },
  data() {
    return {
      layoutMap: LAYOUT_MAP,
    };
  },

};
</script>

<style scoped lang="postcss">
.custom-page-container {
  padding: 20px;
  width: 760px;
}
.page-item{
  width: 100%;
}
.page-element {
  position: relative;
  display: inline-block;
  width: 100%;
  min-height: 86px;
  border: 1px solid transparent;
  vertical-align: top;
  overflow: hidden;
}

.half-row {
  width: 50%;
}

.quarter-row {
  width: 25%;
}

.three-fourths-row {
  width: 75%;
}

</style>
