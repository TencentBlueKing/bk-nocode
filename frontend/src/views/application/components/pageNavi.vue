<template>
  <div class="page-navi">
    <app-selector
      :list="appList"
      :loading="appListLoading"
      :disabled="appListLoading"
      :value="$route.params.appId"
      @change="handleAppchange">
    </app-selector>
    <div class="page-list-container">
      <div v-for="item in pageList" :class="['page-item', { expanded: item.expanded }]" :key="item.id">
        <div
          :class="[
            'name-wrapper',
            {
              active: crtPage.id === item.id,
              group: item.type === 'GROUP',
            },
          ]"
          @click="handlePageItemClick(item)">
          <div class="name-text">{{ item.name }}</div>
          <i
            v-if="item.type === 'GROUP'"
            :class="['bk-icon', 'icon-angle-right', 'arrow-icon', { expanded: item.expanded }]"></i>
        </div>
        <div
          v-if="item.type === 'GROUP'"
          class="sub-navi-wrapper"
          :style="{ height: item.children && item.expanded ? `${item.children.length * 40}px` : '0px' }">
          <div
            v-for="page in item.children"
            :key="page.id"
            :class="['sub-page-item', { active: crtPage.id === page.id }]"
            @click="handlePageItemClick(page)">
            <i class="sub-page-icon"></i>
            <span class="name-text">{{ page.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import appSelector from '@/components/appSelector.vue';

export default {
  name: 'PageNavi',
  components: {
    appSelector,
  },
  props: {
    list: {
      type: Array,
      default: () => [],
    },
    crtPage: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      pageList: this.transToPageList(),
      appList: [],
      appListLoading: false,
    };
  },
  watch: {
    list() {
      this.pageList = this.transToPageList();
    },
  },
  mounted() {
    this.getAppList();
  },
  methods: {
    async getAppList() {
      this.appListLoading = true;
      try {
        const res = await this.$store.dispatch('setting/getAllApp');
        this.appList = res.data.filter(item => ['RELEASED', 'CHANGED'].includes(item.publish_status));
        this.$emit('appListLoaded', this.appList);
      } catch (e) {
        console.error(e);
      } finally {
        this.appListLoading = false;
      }
    },
    transToPageList() {
      return this.list.map(item => {
        const pageItem = Object.assign({}, item);
        if (pageItem.type === 'GROUP') {
          pageItem.expanded = !!pageItem.children.find(p => p.id === this.crtPage.id);
        }
        return pageItem;
      });
    },
    handleAppchange({ key, version_number }) {
      this.$router.push({ name: 'appPageContent', params: { appId: key, version: version_number } }).then(() => {
        window.location.reload();
      });
    },
    handlePageItemClick(pageItem) {
      if (pageItem.type === 'GROUP') {
        this.pageList.forEach(item => {
          if (item.type === 'GROUP') {
            if (item.id === pageItem.id) {
              this.$set(pageItem, 'expanded', !pageItem.expanded);
            } else {
              this.$set(item, 'expanded', false);
            }
          }
        });
      } else {
        this.$emit('select', pageItem);
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/scroller.css';

.page-navi {
  height: 100%;
  background: #ffffff;
  box-shadow: 1px 0 0 0 #dcdee5;
}
.page-list-container {
  padding: 8px 0;
  height: calc(100% - 52px);
  overflow: auto;
  @mixin scroller;
}
.page-item {
  margin: 2px 0;
  &.expanded {
    background: #f0f1f5;
  }
}
.name-wrapper {
  position: relative;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  color: #63656e;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  cursor: pointer;
  &.active {
    background: #e1ecff;
    color: #3a84ff;
  }
  &:hover {
    background: #f0f1f5;
  }
  .arrow-icon {
    position: absolute;
    right: 10px;
    top: 10px;
    font-size: 18px;
    transition: transform 0.2s ease-in-out;
    &.expanded {
      transform: rotate(90deg);
    }
  }
}
.sub-navi-wrapper {
  transition: height 0.2s ease-in-out;
  overflow: hidden;
  .sub-page-item {
    position: relative;
    display: flex;
    align-items: center;
    padding: 0 20px;
    height: 40px;
    line-height: 40px;
    font-size: 14px;
    color: #63656e;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    cursor: pointer;
    &.active {
      background: #e1ecff;
      color: #3a84ff;
      .sub-page-icon {
        background: #3a84ff;
      }
    }
    .sub-page-icon {
      display: inline-block;
      margin: 0 22px 0 6px;
      width: 4px;
      height: 4px;
      background: #dcdee5;
      border-radius: 50%;
    }
  }
}
</style>
