<!--
  - Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.
  -
  - License for BK-ITSM 蓝鲸流程服务:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
    <span
      :class="extCls"
      :title="statusMap[status].name"
      class="bk-status-color-info">
        <template v-if="type === 'text'">
            <span :class="['status-text', statusMap[status].cls]">{{ statusMap[status].name }}</span>
        </template>
        <span v-else-if="type === 'block'" :class="['status-block', statusMap[status].cls]">
            <i v-if="statusIcon === 'loading'" class="bk-itsm-icon icon-icon-loading"></i>
            <i v-else-if="statusIcon === 'success'" class="bk-itsm-icon icon-icon-finish"></i>
            <i v-else-if="statusIcon === 'failed'" class="bk-itsm-icon icon-itsm-icon-delete-fill"></i>
            <span :class="['status-text', statusMap[status].cls]">{{ statusMap[status].name }}</span>
        </span>
        <template v-else>
            <i v-if="['RUNNING', 'WAITING_FOR_BACKEND'].includes(status)" class="bk-itsm-icon icon-icon-loading"></i>
            <span v-else class="status-dot" :class="statusMap[status].cls"></span>
            {{ statusMap[status].name }}
        </template>
    </span>
</template>

<script>
export default {
  name: 'TaskStatus',
  props: {
    status: {
      type: String,
    },
    extCls: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      // 状态列表
      statusMap: {
        NEW: { name: '新' },
        QUEUE: { name: '待处理' },
        WAITING_FOR_OPERATE: { name: '待处理', cls: 'blue' },
        WAITING_FOR_BACKEND: { name: '后台处理中' },
        RUNNING: { name: '执行中', cls: 'blue' },
        WAITING_FOR_CONFIRM: { name: '待总结', cls: 'blue' },
        FINISHED: { name: '已完成', cls: 'green' },
        FAILED: { name: '失败', cls: 'red' },
        DELETED: { name: '已删除' },
        REVOKED: { name: '已撤销', cls: 'red' },
        SUSPENDED: { name: '已暂停', cls: 'blue' },
      },
      statusIconMap: {
        loading: ['QUEUE', 'WAITING_FOR_OPERATE', 'WAITING_FOR_BACKEND', 'RUNNING', 'WAITING_FOR_CONFIRM'],
        success: ['FINISHED'],
        failed: ['FAILED', 'DELETED', 'REVOKED', 'SUSPENDED'],
        default: [],
      },
    };
  },
  computed: {
    statusIcon() {
      const keys = Object.keys(this.statusIconMap);
      for (let i = 0; i < keys.length; i++) {
        const val = this.statusIconMap[keys[i]];
        if (val.includes(this.status)) {
          return keys[i];
        }
      }
      return '';
    },
  },
};
</script>

<style lang="postcss" scoped>
.bk-status-color-info {
  display: inline-block;
  vertical-align: middle;
  font-size: 12px;
  color: #63656E;
  .status-text {
    &.blue {
      color: #3a84ff;
    }
    &.red {
      color: #ea3536;
    }
    &.green {
      color:  #2dcb56;
    }
  }
  .status-dot {
    margin-right: 6px;
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #dcdee5;
    &.blue {
      background: #3a84ff;
    }
    &.red {
      background: #ea3536;
    }
    &.green {
      background:  #2dcb56;
    }
  }
  .bk-itsm-icon.icon-icon-loading {
    display: inline-block;
    font-size: 14px;
    color: #3A84FF;
  }
  .status-block {
    display: inline-block;
    height: 22px;
    line-height: 22px;
    overflow: hidden;
    vertical-align: middle;
    padding: 0 4px;
    background: #dcdee5;
    border-radius: 2px;
    > i {
      display: inline-block;
      vertical-align: middle;
      font-size: 17px;
    }
    &.blue {
      color: #3a84ff;
      background: rgba($color: #3a84ff, $alpha: 0.15);
    }
    &.red {
      color: #ea3536;
      background: rgba($color: #ea3536, $alpha: 0.15);
    }
    &.green {
      color:  #2dcb56;
      background: rgba($color:  #2dcb56, $alpha: 0.15);
    }
  }
}
</style>
