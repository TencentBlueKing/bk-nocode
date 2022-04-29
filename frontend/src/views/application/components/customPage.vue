<template>
  <div class="custom-page-container">
    <div v-for="(page,index) in pageList"
         :key="`${page.type}_${index}`"
         :class="['page-element',layoutMap[page.layout.lineLayout]]" @click="handleClick(page)">
      <page-item :page="page" :editor="true"></page-item>
    </div>
  </div>
</template>

<script>
import pageItem from '@/views/setting/pages/edit/pageItem.vue';
const LAYOUT_MAP = {
  COL_3: 'quarter-row',
  COL_6: 'half-row',
  COL_9: 'three-fourths-row',
};
export default {
  name: 'CustomPage',
  components: {
    pageItem,
  },
  props: {
    pageList: {
      type: Array,
      default: () => ([]),
    },
    appId: String,
    appName: String,
    version: String,
  },
  data() {
    return {
      layoutMap: LAYOUT_MAP,
    };
  },
  methods: {
    handleClick(page) {
      const { id, page_id, value, type } = page;
      switch (type) {
        case 'FUNCTION':
          this.$router.push({
            name: 'commonCreateTicket',
            params: {
              appId: this.appId,
              version: this.version,
              pageId: page_id,
              funcId: value,
              actionId: id,
            },
            query: {
              componentId: id,
            },
          });
          break;
        case 'LINK':
          this.goToLink(value);
          break;
      }
    },
    goToLink(val) {
      let url = val;
      if (url.indexOf('http') !== 0) {
        url = `http://${url}`;
      }
      window.open(url, '_blank');
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-page-container {
  padding:0 20px;
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
  &:hover{
    cursor: pointer;
  }
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
