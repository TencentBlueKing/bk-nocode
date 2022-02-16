<template>
  <section class="workbench-collect-content" v-bkloading="{ isLoading: collectListLoading }">
    <page-wrapper title="我的收藏">
      <div class="collect-page-container">
        <div class="search-area">
          <bk-input
            v-model="searchStr"
            class="search-input"
            left-icon="bk-icon icon-search"
            placeholder="搜索关键字"
            :clearable="true"
            @change="handleChange"
            @enter="handleSearch"
            @clear="handleSearchClear">
          </bk-input>
        </div>
        <div v-if="Object.keys(collectList).length > 0" class="collect-card-area">
          <div v-for="(project, key) in collectList" class="project-item-wrapper" :key="key">
            <div class="header-title">
              <i
                :class="['bk-icon', 'icon-down-shape', 'arrow-icon', { folded: !project.expand }]"
                @click="project.expand = !project.expand">
              </i>
              <span
                class="project-icon"
                :style="{
                  background: `linear-gradient(90deg, ${project.project_color[0]}, ${project.project_color[1]})`,
                }">
                {{ project.project_logo }}
              </span>
              <span class="project-name">{{ project.project_name }}</span>
            </div>
            <div v-if="project.expand" class="card-wrapper">
              <func-card
                v-for="card in project.components"
                class="card-item"
                :key="card.id"
                :show-collect-icon="true"
                :card="card"
                :collected="true"
                @select="handleCardClick($event, project)"
                @collectChange="handleCollectCancel(arguments, project)">
              </func-card>
            </div>
          </div>
        </div>
        <div v-if="Object.keys(fullList).length === 0" class="collect-empty">
          <img :src="collectEmpty" alt="收藏列表为空" />
          <p>暂无收藏的功能卡片</p>
          <p style="font-size: 12px; color: #979ba5">将鼠标悬浮到功能卡片，点击收藏图标</p>
        </div>
        <div v-else-if="Object.keys(collectList).length === 0" class="search-empty">
          <img :src="searchEmpty" alt="收藏数据为空" />
          <p>搜索无结果，请重新搜索</p>
        </div>
      </div>
    </page-wrapper>
  </section>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import FuncCard from '@/views/setting/components/funcCard.vue';
import PageWrapper from '@/components/pageWrapper.vue';

export default {
  name: 'Collect',
  components: {
    FuncCard,
    PageWrapper,
  },
  data() {
    return {
      collectEmpty: require('@/assets/images/no-collect.svg'),
      searchEmpty: require('@/assets/images/search-null.svg'),
      fullList: [],
      collectList: {},
      collectListLoading: false,
      searchStr: '',
    };
  },
  computed: {},
  created() {
    this.getCollectList();
  },
  methods: {
    async getCollectList() {
      try {
        this.collectListLoading = true;
        const res = await this.$store.dispatch('workbench/getCollectList');
        const collectList = {};
        Object.keys(res.data).forEach((key) => {
          res.data[key].components.forEach(item => (item.collected = true));
          collectList[key] = Object.assign(res.data[key], { expand: true });
        });
        this.fullList = collectList;
        this.collectList = cloneDeep(collectList);
      } catch (e) {
        console.error(e);
      } finally {
        this.collectListLoading = false;
      }
    },
    handleSearch() {
      const collectList = {};
      Object.keys(this.fullList).forEach((key) => {
        const project = {
          ...this.fullList[key],
          components: [],
        };
        this.fullList[key].components.forEach((item) => {
          if (item.config.name.toUpperCase().includes(this.searchStr.toUpperCase())) {
            project.components.push(item);
          }
        });
        if (project.components.length > 0) {
          collectList[key] = project;
        }
      });
      this.collectList = collectList;
    },
    handleChange(val) {
      if (!val) {
        this.getCollectList();
      }
    },
    handleSearchClear() {
      this.collectList = cloneDeep(this.fullList);
      this.searchStr = '';
    },
    handleCardClick(card, project) {
      const { page_id, value, id } = card;
      const { project_config, project_version } = project;
      this.$router.push({
        name: 'commonCreateTicket',
        params: {
          appId: project_config.project_key,
          version: project_version,
          pageId: page_id,
          funcId: value,
          actionId: card.id,
        },
        query: {
          componentId: id,
        },
      });
    },
    handleCollectCancel(data, project) {
      const [id, collected] = data;
      if (!collected) {
        const index = project.components.findIndex(item => item.id === id);
        project.components.splice(index, 1);
        if (project.components.length === 0) {
          this.$delete(this.collectList, project.project_config.project_key);
        }
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
.collect-page-container {
  height: 100%;
  padding: 24px 0;
  overflow: auto;
  .project-item-wrapper {
    margin-top: 16px;
  }
}
.search-area {
  padding: 0 24px;
  .search-input {
    /deep/ .bk-form-input {
      height: 40px;
    }
  }
}
.header-title {
  display: flex;
  align-items: center;
  padding: 0 24px;
  .arrow-icon {
    color: #979ba5;
    font-size: 12px;
    cursor: pointer;
    transition: transform 0.2s ease-in-out;
    &:hover {
      color: #3a84ff;
    }
    &.folded {
      transform: rotate(-90deg);
    }
  }
  .project-icon {
    display: inline-block;
    margin: 0 8px;
    width: 24px;
    height: 24px;
    line-height: 24px;
    color: #ffffff;
    background: #3a84ff;
    border-radius: 50%;
    text-align: center;
  }
  .project-name {
    font-size: 16px;
    color: #313238;
  }
}
.card-wrapper {
  padding: 0 16px;
  overflow: hidden;
  .card-item {
    float: left;
    margin: 8px;
    cursor: pointer;
  }
}
.collect-empty {
  margin: 200px auto 0;
  text-align: center;
  & > img {
    width: 120px;
  }
  & > p {
    margin-top: 8px;
    font-size: 14px;
    color: #63656e;
  }
}
.search-empty {
  margin: 200px auto 0;
  text-align: center;
  & > img {
    width: 120px;
  }
  & > p {
    margin-top: 8px;
    font-size: 16px;
    color: #313238;
  }
}
</style>
