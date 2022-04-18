<template>
  <div :class="['custom-page-container',{ 'exception-container': !pageList.length }]">
    <template v-if="pageList.length>0">
      <div v-for="(page,index) in pageList"
           :key="`${page.type}_${index}`"
           :class="['page-element',layoutMap[page.layout.lineLayout]]">
        <page-item :page="page" :editor="true"></page-item>
      </div>
    </template>
    <div v-else>
      <bk-exception class="fields-empty" type="empty" scene="part">
        暂无内容，请去
        <span @click="handleEditPage">编辑页面</span>
      </bk-exception>
    </div>
  </div>
</template>

<script>
import pageItem from './edit/pageItem.vue';

const LAYOUT_MAP = {
  COL_3: 'quarter-row',
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
    },
    appId: [String, Number],
    pageId: [String, Number],
  },
  data() {
    return {
      layoutMap: LAYOUT_MAP,
    };
  },
  methods: {
    handleEditPage() {
      this.$router.push({ name: 'customPage', params: { appId: this.appId, pageId: this.pageId } });
    },
  },

};
</script>

<style scoped lang="postcss">
.custom-page-container {
  padding: 20px;
}

.page-item {
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
.exception-container{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.fields-empty{
  span{
    color: #3a84ff;
    &:hover{
      cursor: pointer;
    }
  }
}
</style>
