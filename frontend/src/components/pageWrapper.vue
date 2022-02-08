<template>
  <div class="common-page-wrapper">
    <div class="page-header-container">
      <div class="title-area">
        <i v-if="backIcon" class="bk-icon back-icon icon-arrows-left-shape" @click="$emit('back')" />
        <div :class="['page-title', { 'with-back-icon': backIcon }]">{{ title }}</div>
      </div>
      <div class="header-extend-area">
        <slot name="header"></slot>
      </div>
    </div>
    <div class="page-scoll-container">
      <div :class="['page-main-wrapper', { 'nav-folded': $store.state.navFold }]">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PageWrapper',
  props: {
    title: {
      type: String,
      default: '',
    },
    backIcon: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../css/scroller.css';

.common-page-wrapper {
  height: calc(100vh - 52px);
}
.page-header-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 52px;
  background: #ffffff;
  box-shadow: 0 3px 4px 0 rgba(64, 112, 203, 0.06);
  z-index: 1;
  .title-area {
    display: flex;
    align-items: center;
    height: 100%;
    .back-icon {
      padding-left: 32px;
      font-size: 12px;
      color: #3a84ff;
      cursor: pointer;
    }
    .page-title {
      padding-left: 24px;
      color: #313238;
      font-size: 16px;
      &.with-back-icon {
        padding-left: 10px;
        margin: 0 auto;
      }
    }
  }
}
.page-scoll-container {
  height: calc(100% - 52px);
  overflow: hidden;
}
.page-main-wrapper {
  height: 100%;
  overflow: auto;
  @mixin scroller;
  &.nav-folded {
    min-width: 1380px;
  }
}
</style>
