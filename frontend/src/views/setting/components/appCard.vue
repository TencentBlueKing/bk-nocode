<template>
  <div :class="['app-card', { 'popover-open': popoverOpen }]" @click="$emit('handleClick', app)">
    <template v-if="type === 'edit'">
      <bk-spin v-if="releasing" class="app-releasing" size="mini"></bk-spin>
      <div v-else class="status-tag" :style="{ background: appStatusConfig.bgColor, color: appStatusConfig.color }">
        {{ appStatusConfig.name }}
      </div>
      <div class="more-opt-area">
        <bk-popover
          ref="morePopover"
          placement="bottom"
          theme="light"
          ext-cls="more-app-popover"
          :tippy-options="{
            arrow: false,
            distance: 0,
            duration: [100, 100],
          }"
          :on-show="onPopoverShow"
          :on-hide="onPopoverHide">
          <i class="bk-icon icon-more more-dot-icon"></i>
          <div class="more-action" slot="content">
            <div
              class="action-item"
              v-if="['CHANGED', 'RELEASED'].includes(app.publish_status)"
              @click="$emit('handleClick', app, 'down')">
              下架
            </div>
            <div class="action-item" @click="$emit('handleClick', app, 'edit')">设置</div>
            <div
              class="action-item"
              v-if="['CHANGED', 'RELEASED'].includes(app.publish_status)"
              @click="$emit('handleClick', app, 'export')">
              导出
            </div>
            <div class="action-item" @click="$emit('handleClick', app, 'delete')">删除</div>
          </div>
        </bk-popover>
      </div>
    </template>
    <div class="basic-info">
      <div class="app-logo" :style="logoBgColor">{{ app.logo }}</div>
      <div class="app-msg">
        <h4
          :class="['title', { unreleased: app.publish_status === 'UNRELEASED' }]"
          @click="$emit('handleClick', app, 'view')">
          {{ app.name }}
        </h4>
        <p class="update-time">发布时间：{{ app.update_at }}</p>
      </div>
    </div>
    <p class="app-desc">{{ app.desc||'暂无描述' }}</p>
    <div v-if="type === 'edit'" class="buttons-area">
      <div :class="['button-item', { disabled: releasing }]" @click="onReleaseClick">
        <div class="text">发布</div>
      </div>
      <div class="button-item" @click="$emit('handleClick', app, 'detail')">
        <div class="text">编辑</div>
      </div>
      <!--<div class="button-item" @click="$emit('handleClick', app, 'edit')"><div class="text">设置</div></div>-->
    </div>
  </div>
</template>
<script>
import { APP_STATUS_CONFIG } from '@/constants/apps.js';

export default {
  name: 'AppCard',
  props: {
    type: {
      type: String,
      default: 'view',
    },
    releasing: {
      type: Boolean,
      default: false,
    },
    app: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      popoverOpen: false,
    };
  },
  computed: {
    logoBgColor() {
      return {
        background: `linear-gradient(90deg, ${this.app.color[0]}, ${this.app.color[1]})`,
      };
    },
    appStatusConfig() {
      // if (['UNRELEASED', 'DRAFT'].includes(this.app.publish_status)) {
      //   return APP_STATUS_CONFIG.find(item => item.id === this.app.publish_status);
      // }
      return APP_STATUS_CONFIG.find(item => item.id === this.app.publish_status) || {};
    },
  },
  methods: {
    onPopoverShow() {
      this.popoverOpen = true;
    },
    onPopoverHide() {
      this.popoverOpen = false;
    },
    onReleaseClick() {
      if (!this.releasing) {
        this.$emit('handleClick', this.app, 'release');
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
.app-card {
  position: relative;
  width: 288px;
  height: 160px;
  border-radius: 8px;
  background: #ffffff;
  background-image: url('../../../assets/images/app-card-bg.svg');
  background-repeat: no-repeat;
  background-size: 120px 120px;
  background-position: bottom right;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  overflow: hidden;

  &:hover {
    box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.1);
    .buttons-area {
      bottom: 0;
    }
  }
  &:hover,
  &.popover-open {
    .more-dot-icon {
      visibility: visible;
    }
  }
  &.popover-open {
    .more-dot-icon {
      color: #3a84ff;
    }
  }
}
.app-releasing {
  position: absolute;
  top: 10px;
  left: 10px;
}

.status-tag {
  position: absolute;
  top: 0;
  left: 0;
  padding: 2px 10px;
  font-size: 12px;
  line-height: 18px;
  /* background: #ffe8c3;
  color: #ff9c01; */
  border-bottom-right-radius: 8px;
}
.more-opt-area {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 10;
}
.more-dot-icon {
  display: inline-block;
  color: #979ba5;
  visibility: hidden;
  &:hover {
    color: #3a84ff;
  }
}
.basic-info {
  display: flex;
  align-items: center;
  padding: 24px 24px 4px;

  .app-logo {
    margin-right: 16px;
    width: 32px;
    height: 32px;
    text-align: center;
    line-height: 32px;
    font-size: 16px;
    border-radius: 50%;
    color: #ffffff;
    background: rgba(255, 255, 255, 0.8);
  }

  .app-msg {
    .title {
      margin: 0;
      font-size: 14px;
      font-weight: bold;
      line-height: 22px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      &:not(.unreleased):hover {
        color: #3a84ff;
        cursor: pointer;
      }
    }

    .update-time {
      font-size: 12px;
      line-height: 20px;
      color: #979ba5;
    }
  }
}

.app-desc {
  display: -webkit-box;
  margin: 8px 24px 0;
  max-height: 40px;
  font-size: 12px;
  color: #979ba5;
  line-height: 20px;
  word-break: break-all;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  text-overflow: ellipsis;
}

.buttons-area {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  background: #fafbfd;
  transition: bottom 0.3s ease-in-out;

  .button-item {
    display: flex;
    align-items: center;
    flex: 1;
    height: 100%;
    color: #63656e;
    cursor: pointer;

    .text {
      width: 100%;
      font-size: 12px;
      line-height: 12px;
      text-align: center;
    }

    &.disabled {
      cursor: not-allowed;
      color: #c4c6cc;
    }

    &:not(:last-child) {
      .text {
        border-right: 1px solid #f0f1f5;
      }
    }

    &:not(.disabled) {
      &:target {
        color: #1768ef;
      }

      &:hover {
        color: #3a84ff;
      }
    }
  }
}
.more-action {
  position: relative;
  .action-item {
    padding: 0 12px;
    height: 32px;
    line-height: 32px;
    color: #63656e;
    cursor: pointer;

    &:hover {
      background: #f4f6fa;
      color: #3a84ff;
    }

    i {
      width: 12px;
      margin-right: 4px;
    }
  }
}
</style>
<style lang="postcss">
.more-app-popover {
  background: #ffffff;
  .tippy-tooltip {
    padding: 2px 0;
  }
}
</style>
