<template>
  <section class="manage-admin-content">
    <!--    <page-wrapper title="api配置">-->
    <div class="common-page-wrapper">
      <div class="page-header-container">
        <div class="title-area">
          <div class="page-title">API配置</div>
        </div>
      </div>
    </div>
    <span :class="['custom-icon-font', 'icon-tree', 'api-show',!sidebarShow?'show-active':'']" @click="sidebarShow=!sidebarShow"></span>
    <div class="itsm-page-content">
      <div class="bk-api-configure">
        <div class="bk-directory-tree" v-if="sidebarShow">
          <api-tree
            ref="apiTree"
            :code-list="codeList"
            :all-code-list="allCodeList"
            :tree-list-ori="treeList"
            @changeSlider="changeSlider">
          </api-tree>
        </div>
        <div :class="sidebarShow?'bk-directory-table':'bk-directory-table1'"
              :style="{ height: Object.keys(displayInfo['level_1']).length?'100%':'',
            'margin-top': Object.keys(displayInfo['level_1']).length?'0':'25px'
            }">
          <api-table
            style="height:  626px; "
            v-if="!Object.keys(displayInfo['level_1']).length"
            ref="apiTable"
            :first-level-info="firstLevelInfo"
            :custom-paging="customPaging"
            :tree-list="treeList"
            :path-list="pathList"
            :list-info-ori="listInfo">
          </api-table>
          <api-content
            v-else
            :second-level-info="secondLevelInfo"
            :api-detail-info="apiDetailInfo"
            :tree-list="treeList"
            :path-list="pathList"
            :is-builtin-id-list="isBuiltinIdList">
          </api-content>
        </div>
      </div>
    </div>
    <!--    </page-wrapper>-->
  </section>
</template>
<script>
import apiTable from './component/apiTable.vue';
import apiContent from './component/apiContent.vue';
import apiTree from './component/apiTree.vue';
import mixins from './mixins/mixins_api';
// import PageWrapper from '@/components/pageWrapper.vue';

export default {
  name: 'ApiConfig',
  components: {
    apiTree,
    apiContent,
    apiTable,
    // PageWrapper,
  },
  mixins: [mixins],
  data() {
    return {
      sidebarShow: true,
      // 目前展示信息
      displayInfo: {
        level_0: {},
        level_1: {},
      },
      // API 详情
      apiDetailInfo: {},
      // API列表
      listInfo: [],
      // 系统分类列表
      treeList: [
        {
          id: 0,
          name: '全部系统',
          code: '',
          check: false,
        },
      ],
      // code列表
      codeList: [],
      allCodeList: [],
      pathList: [],
      isBuiltinIdList: [],
      isSelectedApiList: [],
      showConetnt: false,
      customPaging: {
        total_page: 1,
        page: 1,
        count: 0,
        page_size: 10,
        list: [
          { num: 5 },
          { num: 10 },
          { num: 15 },
          { num: 20 },
        ],
      },
    };
  },
  computed: {
    sliderStatus() {
      return this.$store.state.common.slideStatus;
    },
    firstLevelInfo() {
      return this.displayInfo.level_0;
    },
    secondLevelInfo() {
      return this.displayInfo.level_1;
    },
  },
  watch: {},
  created() {
    this.getRemoteSystemData();
  },
  mounted() {
  },
  methods: {
    // 获取系统
    async getRemoteSystemData() {
      const params = {};
      await this.$refs;
      await this.$refs.apiTree;
      this.$refs.apiTree.isTreeLoading = true;
      await this.$store.dispatch('manage/getRemoteSystem', params).then((res) => {
        this.isBuiltinIdList = res.data.map(item => item.system_id);
        res.data.forEach((item) => {
          item.moreShow = false;
          item.check = item.id === this.displayInfo.level_0.id;
        });
        this.treeList = [this.treeList[0], ...res.data];
        this.getSystems();
      })
        .catch((res) => {
          console.log(res);
          // this.$bkMessage({
          //   message: res.data.msg,
          //   theme: 'error',
          // });
        })
        .finally(() => {
          this.$refs.apiTree.isTreeLoading = false;
        });
    },
    // 获取codeList
    async getSystems() {
      const params = {};
      await this.$store.dispatch('manage/getSystems', params).then((res) => {
        this.allCodeList = res.data;
        this.codeList = res.data.filter(item => this.isBuiltinIdList.indexOf(item.system_id) === -1);
      })
        .catch((res) => {
          this.$bkMessage({
            message: res.data.msg,
            theme: 'error',
          });
        })
        .finally(() => {
        });
    },
    // 获取API详情
    async getRemoteApiDetail(id) {
      const params = {
        id,
      };
      await this.$store.dispatch('manage/getRemoteApiDetail', params).then((res) => {
        this.apiDetailInfo = res.data;
        this.apiDetailInfo.ownersInputValue = this.apiDetailInfo.owners ? this.apiDetailInfo.owners.split(',') : [];
        if (!this.apiDetailInfo.req_headers.length) {
          this.apiDetailInfo.req_headers = [];
        }
        if (!this.apiDetailInfo.req_params.length) {
          this.apiDetailInfo.req_params = [];
        } else {
          this.apiDetailInfo.req_params = [...this.apiDetailInfo.req_params.map((item) => {
            item.value = '';
            return item;
          })];
        }
        if (!Object.keys(this.apiDetailInfo.req_body).length
          || !Object.keys(this.apiDetailInfo.req_body.properties).length) {
          this.apiDetailInfo.treeDataList = [{
            has_children: false,
            showChildren: true,
            checkInfo: false,
            key: 'root',
            is_necessary: true,
            type: 'object',
            desc: '初始化数据',
            parentInfo: '',
            children: [],
          }];
          this.apiDetailInfo.bodyJsonData = {
            root: {},
          };
          this.apiDetailInfo.bodyTableData = [];
        } else {
          this.apiDetailInfo.treeDataList = this.jsonschemaToList({
            root: JSON.parse(JSON.stringify(this.apiDetailInfo.req_body)), // root初始 Jsonschema数据结构
          });
          this.apiDetailInfo.bodyJsonData = this.jsonschemaToJson({
            root: JSON.parse(JSON.stringify(this.apiDetailInfo.req_body)), // root初始 Jsonschema数据结构
          });
          const tempArr = JSON.parse(JSON.stringify(this.apiDetailInfo.treeDataList[0].children));
          this.apiDetailInfo.bodyTableData = this.treeToTableList(tempArr);
        }
        if (!Object.keys(this.apiDetailInfo.rsp_data).length
          || !Object.keys(this.apiDetailInfo.rsp_data.properties).length) {
          this.apiDetailInfo.responseTreeDataList = [{
            has_children: false,
            showChildren: true,
            checkInfo: false,
            key: 'root',
            is_necessary: true,
            type: 'object',
            desc: '初始化数据',
            parentInfo: '',
            children: [],
          }];
          this.apiDetailInfo.responseJsonData = {
            root: {},
          };
          this.apiDetailInfo.responseTableData = [];
        } else {
          this.apiDetailInfo.responseTreeDataList = this.jsonschemaToList({
            root: this.apiDetailInfo.rsp_data, // root初始 Jsonschema数据结构
          });
          this.apiDetailInfo.responseJsonData = this.jsonschemaToJson({
            root: this.apiDetailInfo.rsp_data, // root初始 Jsonschema数据结构
          });
          const tempArr = JSON.parse(JSON.stringify(this.apiDetailInfo.treeDataList[0].children));
          this.apiDetailInfo.responseTableData = this.treeToTableList(tempArr);
        }
      })
        .catch((res) => {
          this.$bkMessage({
            message: res.data.msg,
            theme: 'error',
          });
        });
    },
    // 获取已接入api接口列表数据
    async getTableList(id, customPaging, searchInfo) {
      await this.displayInfo.level_1;
      await this.$refs.apiTable;
      const params = {
        remote_system: id || '',
        page_size: customPaging ? customPaging.page_size : 10,
        is_draft: 0,
        page: customPaging ? customPaging.page : 1,
        // 关键字
        key: searchInfo ? searchInfo.key : '',
      };
      this.$refs.apiTable.isTableLoading = true;
      await this.$store.dispatch('manage/getRemoteApi', params).then((res) => {
        // console.log(res.data)
        this.isSelectedApiList = res.data.items.filter(ite => !ite.is_builtin).map(item => item.path);
        this.listInfo = res.data.items.map((item) => {
          item.check = false;
          return item;
        });
        // 分页
        this.$refs.apiTable.pagination.current = res.data.page;
        this.$refs.apiTable.pagination.count = res.data.count;
      })
        .catch((res) => {
          this.$bkMessage({
            message: res.data.msg,
            theme: 'error',
          });
        })
        .finally(() => {
          this.$refs.apiTable.isTableLoading = false;
        });
    },
    // 根据系统code --> 获取pathList 未接入api接口
    async getChannelPathList(code) {
      const params = {
        system_code: code,
        // system_id: systemId
      };
      await this.$store.dispatch('manage/getComponents', params).then((res) => {
        this.pathList = res.data.map((item) => {
          item.func_name = item.name;
          item.name = item.label;
          return item;
        });
        // console.log(this.pathList)
      })
        .catch((res) => {
          this.$bkMessage({
            message: res.data.msg,
            theme: 'error',
          });
        })
        .finally(() => {
        });
    },
    changeSlider(isShow) {
      this.sidebarShow = isShow;
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../css/clearfix.css';
@import "../../css/scroller.css";


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

.itsm-page-content {
  height: calc(100vh - 104px);
  overflow: hidden;
  @mixin scroller;
}

.api-show {
  display: block;
  position: absolute;
  z-index: 99;
  right: 16px;
  top: 16px;
  cursor: pointer;
}

.show-active{
  color: #3a84ff;
}

.bk-api-configure {
  height: 100%;
  @mixin clearfix;
}

.bk-directory-tree {
  background: #FFFFFF;
  margin-right: 24px;
  height: 100%;
  width: 240px;
  float: left;
  border: 1px solid #dde4eb;
  position: relative;
  overflow: auto;
  @mixin scroller;
}

.bk-directory-table {
  margin-top: 24px;
  background: #FFFFFF;
  margin-right:24px ;
  width:calc(100% - 288px);
  border: 1px solid #dde4eb;
  float: left;
  position: relative;
  overflow: auto;
  @mixin scroller;
}

.bk-directory-table1 {
  background: #FFFFFF;
  border: 1px solid #dde4eb;
  position: relative;
  overflow: auto;
  margin: 24px;
  @mixin scroller;
}
</style>
