<template>
  <div class="bk-api-content">
    <div class="is-title-back">
      <p class="bk-come-back" @click="backTab">
        <arrow-left-icon></arrow-left-icon>
        <template>{{ backName }}</template>
      </p>
    </div>
    <div class="itsm-page-content">
      <div class="bk-api-ul">
        <ul>
          <li v-for="(item, index) in titleList"
              :key="index"
              :class="{ 'bk-api-check': checkIndex === index }"
              @click="changTitle(item, index)">
            <span>{{item.name}}</span>
          </li>
        </ul>
      </div>
      <div class="bk-api-info">
        <api-basic
          :api-detail-info="apiDetailInfo"
          v-if="checkIndex === 0">
        </api-basic>
        <api-editor
          :api-detail-info-common="apiDetailInfoCommon"
          :tree-list="treeList"
          :path-list="pathList"
          :is-builtin-id-list="isBuiltinIdList"
          v-if="checkIndex === 1">
        </api-editor>
        <api-run
          :api-detail-info-common="apiDetailInfoCommon"
          v-if="checkIndex === 2">
        </api-run>
      </div>
    </div>
  </div>
</template>

<script>
import apiBasic from './apiBasic.vue';
import apiEditor from './apiEditor.vue';
import apiRun from './apiRun.vue';
import arrowLeftIcon from './arrowLeftIcon.vue';
export default {
  name: 'ApiContent',
  components: {
    apiBasic,
    apiEditor,
    apiRun,
    arrowLeftIcon,
  },
  props: {
    apiDetailInfo: {
      type: Object,
      default() {
        return {};
      },
    },
    treeList: {
      type: Array,
      default() {
        return [];
      },
    },
    pathList: {
      type: Array,
      default() {
        return [];
      },
    },
    isBuiltinIdList: {
      type: Array,
      default() {
        return [];
      },
    },
    secondLevelInfo: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      apiDetailInfoCommon: this.apiDetailInfo,
      // tag
      titleList: [
        { name: '预览' },
        { name: '编辑' },
        { name: '运行' },
      ],
      checkIndex: 1,
    };
  },
  computed: {
    backName() {
      return this.secondLevelInfo.name;
    },
  },
  watch: {
    apiDetailInfo(newVal,) {
      this.apiDetailInfoCommon = JSON.parse(JSON.stringify(newVal));
      this.initData();
    },
  },
  mounted() {
    this.initData();
  },
  methods: {
    backTab() {
      this.$parent.displayInfo.level_1 = {};
      this.$parent.getTableList();
    },
    changTitle(item, index) {
      this.checkIndex = index;
    },
    initData() {
      if (this.apiDetailInfoCommon.req_headers) {
        if (!this.apiDetailInfoCommon.req_headers.length) {
          this.apiDetailInfoCommon.req_headers = [
            {
              name: '',
              value: '',
              sample: '',
              desc: '',
            },
          ];
        }
        if (!this.apiDetailInfoCommon.req_params.length) {
          this.apiDetailInfoCommon.req_params = [
            {
              name: '',
              is_necessary: 0,
              sample: '',
              desc: '',
              value: '',
            },
          ];
        }
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';
@import '../../../css/scroller.css';

.bk-api-content {
  padding: 0px 10px 60px 10px;
  height: 100%;
}

.bk-api-ul {
  ul {
    @minix clearfix;
  }

  li {
    float: left;
    padding: 0 12px;
    line-height: 50px;
    color: #737987;
    font-size: 14px;
    cursor: pointer;
  }

  .bk-api-check {
    border-bottom: 2px solid #3c96ff;
    color: #3c96ff;
  }
}

.bk-api-info {
  width: 100%;
  height: calc(100% - 52px);
  overflow: auto;
  @minix scroller;
  padding: 0 10px;
}

.is-title-back {
  padding: 10px;
  padding-bottom: 0px;
  font-size: 16px;
  color: #737987;
  cursor: pointer;

  i {
    color: #3c96ff;
    font-weight: bold;
  }
}

.bk-come-back {
  display: flex;
  align-items: center;
  font-size: 16px;
  height: 52px;
  .bk-icon {
    color: #3c96ff;
    font-weight: bold;
    margin-right: 5px;
    font-size: 24px;
  }
}
.itsm-page-content {
  padding: 20px;
}
</style>
