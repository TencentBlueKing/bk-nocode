<template>
  <div
    :class="['page-element',layoutMap[page.layout.lineLayout]]"
    @mouseenter="isHover = true"
    @mouseleave="isHover = false"
    @click="$emit('action', 'edit')">
    <transition name="fade">
      <div v-show="isHover" class="drag-icon-wrapper">
        <i class="drag-icon bk-icon icon-grag-fill"></i>
      </div>
    </transition>
    <div class="field-container">
      <div class="mask"></div>
      <page-item :page="page"></page-item>
    </div>
    <transition name="slide-left">
      <div v-show="isHover" class="actions-area">
        <i class="custom-icon-font icon-copy bk-icon" @click.stop="$emit('action', 'copy')"></i>
        <i class="bk-icon icon-delete" @click.stop="$emit('action', 'delete')"></i>
      </div>
    </transition>
  </div>
</template>

<script>
import pageItem from './pageItem.vue';
const LAYOUT_MAP = {
  COL_3: 'half-row',
  COL_6: 'half-row',
  COL_9: 'three-fourths-row',
};
export default {
  name: 'PageElement',
  components: {
    pageItem,
  },
  props: {
    page: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      isHover: false,
      layoutMap: LAYOUT_MAP,
    };
  },
};
</script>

<style scoped lang="postcss">
.page-element {
  position: relative;
  display: inline-block;
  padding: 12px 40px;
  width: 100%;
  min-height: 86px;
  border: 1px solid transparent;
  vertical-align: top;
  overflow: hidden;
  cursor: move;
  transition: background 0.2s ease-in-out, border 0.2s ease-in-out;

  &:hover {
    background: #fafbfd;
    border-color: #dcdee5;
  }

  &.half-row {
    width: 50%;
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

.field-container {
  position: relative;

  .mask {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 100;
  }

  .field-form-item {
    margin-top: 0;
    width: 100%;
  }
}

.drag-icon-wrapper {
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  color: #c4c6cc;
  z-index: 2;
}

.actions-area {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 36px;
  background: #fcfcfc;
  border-left: 1px solid #dcdee5;
  z-index: 2;

  i {
    padding: 6px 0;
    width: 100%;
    font-size: 14px;
    color: #979ba5;
    cursor: pointer;

    &:hover {
      color: #3a84ff;
    }
  }
}

.slide-left-enter,
.slide-left-leave-to {
  right: -36px;
}

.slide-left-enter-to,
.slide-leave {
  right: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: right 0.2s ease-in-out;
}
</style>
