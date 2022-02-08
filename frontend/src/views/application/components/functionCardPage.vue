<template>
  <div class="function-card-page">
    <div class="card-container">
      <function-card
        v-for="card in cards"
        class="card-item"
        :key="card.id"
        :show-collect-icon="!collectedLoading"
        :always-show-collected="true"
        :collected="collectedList.includes(card.id)"
        :app-id="appId"
        :card="card"
        @select="handleSelect"
        @collectChange="handleCollectChange">
      </function-card>
    </div>
  </div>
</template>
<script>
import permission from '@/components/permission/mixins.js';
import FunctionCard from '@/views/setting/components/funcCard.vue';

export default {
  name: 'FunctionCardPage',
  components: {
    FunctionCard,
  },
  mixins: [permission],
  props: {
    appId: String,
    appName: String,
    version: String,
    page: {
      type: Object,
      default: () => ({}),
    },
    cards: {
      type: Array,
      default: () => [],
    },
    actionsPermMap: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      collectedLoading: true,
      collectedList: [],
    };
  },
  created() {
    this.getCollectedList();
  },
  methods: {
    async getCollectedList() {
      try {
        this.collectedLoading = true;
        const res = await this.$store.dispatch('application/getCollectedCards', { page_id: this.page.id });
        this.collectedList = res.data.collection_components;
        this.collectedLoading = false;
      } catch (e) {
        console.error(e);
      }
    },
    handleSelect(card) {
      // 按钮权限映射表如果没有卡片id字段，则点击无效果
      if (!(card.id in this.actionsPermMap)) {
        return;
      }
      if (this.actionsPermMap[card.id] === false) {
        const resource = {
          action: [{ id: card.id, name: card.config.name }],
          page: [{ id: this.page.id, name: this.page.name }],
          project: [{ id: this.appId, name: this.appName }],
        };
        this.applyForPermission(['action_execute'], [], resource);
        return;
      }
      const { page_id, value, id } = card;
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
    },
    handleCollectChange(id, collected) {
      if (collected) {
        this.collectedList.push(id);
      } else {
        this.collectedList = this.collectedList.filter(item => item !== id);
      }
      this.$emit('collectChange', id, collected);
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../../css/scroller.css';

.function-card-page {
  padding: 12px;
  height: 100%;
  overflow: auto;
  @mixin scroller;
}
.card-container {
  display: flex;
  align-items: center;
  flex-flow: wrap;
}
.card-item {
  margin: 12px;
  cursor: pointer;
}
</style>
