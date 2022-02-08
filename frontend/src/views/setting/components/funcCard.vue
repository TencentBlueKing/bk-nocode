<template>
  <div
    class="func-card"
    :style="{ borderImage: cardData.config.bgColor || funcColors[0] }"
    @click="$emit('select', cardData)">
    <template v-if="showCollectIcon">
      <i
        v-if="!collectPending"
        :class="[
          'custom-icon-font  collect-icon',
          collected ? 'icon-function-collection icon-star-shape' : 'icon-un-collection icon-star',
          { fixed: alwaysShowCollected && collected },
        ]"
        @click.stop="toggleCollect">
      </i>
      <bk-spin v-else class="pending-icon" size="mini"></bk-spin>
    </template>
    <h4 class="card-title">{{ cardData.config.name }}</h4>
    <p v-if="showAppText" class="card-app">所属应用：{{ appName }}</p>
    <div class="card-desc">{{ cardData.config.desc }}</div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import { funcColors } from '@/constants/colors.js';

export default {
  name: 'FuncCard',
  props: {
    appId: String,
    appName: String,
    showCollectIcon: {
      type: Boolean,
      default: false,
    },
    showAppText: {
      type: Boolean,
      default: false,
    },
    card: {
      type: Object,
      default: () => ({}),
    },
    alwaysShowCollected: {
      type: Boolean,
      default: false,
    },
    collected: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      funcColors,
      cardData: cloneDeep(this.card),
      collectPending: false,
    };
  },
  watch: {
    card(val) {
      this.cardData = cloneDeep(val);
    },
  },
  methods: {
    async toggleCollect() {
      if (this.collectPending) {
        return;
      }
      try {
        this.collectPending = true;
        if (this.collected) {
          await this.$store.dispatch('workbench/cancelCollection', { component_id: this.cardData.id });
        } else {
          await this.$store.dispatch('workbench/addCollection', { component_id: this.cardData.id });
        }
        this.$emit('collectChange', this.cardData.id, !this.collected);
      } catch (e) {
        console.error(e);
      } finally {
        this.collectPending = false;
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
.func-card {
  position: relative;
  padding: 24px;
  width: 276px;
  height: 160px;
  background: #ffffff;
  border-top-width: 4px;
  border-top-style: solid;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.1);
  border-radius: 8px;
  background-image: url('../../../assets/images/card-bg.svg');
  background-repeat: no-repeat;
  background-size: 276px 80px;
  background-position: bottom right;
  &:hover {
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1), 0 2px 4px 0 rgba(25, 25, 41, 0.05);
    .collect-icon {
      display: inline-block;
    }
  }
  .collect-icon {
    display: none;
    position: absolute;
    top: 18px;
    right: 18px;
    font-size: 18px;
    color: #979ba5;
    cursor: pointer;
    &.fixed {
      display: inline-block;
    }
    &.icon-star-shape {
      color: #ff9c01;
    }
  }
  .pending-icon {
    position: absolute;
    top: 18px;
    right: 18px;
    font-size: 18px;
  }
  .card-title {
    margin: 0;
    font-size: 14px;
    color: #313238;
    line-height: 22px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .card-app {
    margin: 4px 0 0;
    line-height: 20px;
    font-size: 12px;
    color: #313238;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .card-desc {
    margin-top: 4px;
    height: 62px;
    line-height: 20px;
    font-size: 12px;
    color: #63656e;
    overflow: hidden;
    word-break: break-all;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    text-overflow: ellipsis;
  }
}
</style>
