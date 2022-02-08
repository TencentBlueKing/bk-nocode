<template>
  <section class="applications-center">
    <header>
      <div class="application-title">应用中心</div>
      <div class="applications-search">
        <bk-input
          placeholder="请输入"
          :clearable="true"
          :right-icon="'bk-icon icon-search'"
          @enter="handleSearch"
          @clear="handleSearchClear"
          @change="handleChange"
          v-model.trim="searchValue">
        </bk-input>
      </div>
    </header>
    <div class="card-container" v-bkloading="{ isLoading: listLoading }">
      <template v-if="listData.length > 0">
        <app-card v-for="app in listData" :key="app.key" :app="app" class="app-card-item" @handleClick="handleClick">
        </app-card>
      </template>
      <bk-exception v-else class="no-data" type="empty" scene="part"></bk-exception>
    </div>
  </section>
</template>
<script>
import AppCard from '../setting/components/appCard.vue';

export default {
  name: 'ApplicationCenter',
  components: {
    AppCard,
  },
  data() {
    return {
      searchValue: '',
      listData: [],
      listLoading: false,
    };
  },
  mounted() {
    this.getAppList();
  },
  methods: {
    handleSearch() {
      if (this.searchValue === '') {
        return;
      }
      this.getAppList();
    },
    handleSearchClear() {
      this.searchValue = '';
      this.getAppList();
    },
    handleChange(val) {
      if (!val) {
        this.getAppList();
      }
    },
    async getAppList() {
      try {
        this.listLoading = true;
        const params = {};
        if (this.searchValue !== '') {
          params.name__icontains = this.searchValue;
        }
        const res = await this.$store.dispatch('setting/getAllApp', params);
        res.data.forEach((item) => {
          if (!item.color) {
            item.color = ['#3a84ff', '#6cbaff'];
          }
        });
        this.listData = res.data.filter(item => ['RELEASED', 'CHANGED'].includes(item.publish_status));
      } catch (e) {
        console.error(e);
      } finally {
        this.listLoading = false;
      }
    },
    handleClick(app, type) {
      if (!type) {
        this.$router.push({ name: 'appPageContent', params: { appId: app.key, version: app.version_number } });
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
.applications-center {
  margin: 0 auto;
  width: 1216px;
  padding: 44px 0;

  header {
    margin: 0 8px;
    display: flex;
    justify-content: space-between;
  }

  .application-title {
    width: 80px;
    font-family: MicrosoftYaHei;
    font-size: 20px;
    color: #313238;
    letter-spacing: 0;
    line-height: 28px;
  }

  .applications-search {
    width: 320px;
  }

  .card-container {
    min-height: 510px;
    margin-top: 32px;

    .app-card-item {
      cursor: pointer;
      width: 288px;
      height: 160px;
      float: left;
      margin: 0 8px 16px;
    }
  }

  .no-data {
    position: absolute;
    top: calc(50% - 60px);
  }
}
</style>
