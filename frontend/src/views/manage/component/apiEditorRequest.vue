<template>
  <div class="bk-api-editor-request">
    <p class="bk-basic-p" v-if="basicInfo.method === 'GET'">Query：</p>
    <p class="bk-basic-p" v-if="basicInfo.method === 'POST'">Body：</p>
    <!-- Query -->
    <ul class="bk-request-ul" v-if="basicInfo.method === 'GET'">
      <template v-if="basicInfo.req_params && basicInfo.req_params.length">
        <li v-for="(item, index) in basicInfo.req_params" :key="index">
          <div class="bk-request-form">
            <div class="bk-ul-form">
              <bk-input
                :clearable="true"
                :disabled="basicInfo.is_builtin"
                :placeholder="'参数名称'"
                v-model="item.name">
              </bk-input>
            </div>
            <div class="bk-ul-form">
              <bk-select
                v-model="item.is_necessary"
                :clearable="false"
                :font-size="'medium'"
                :disabled="basicInfo.is_builtin">
                <bk-option
                  v-for="option in necessaryList"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                </bk-option>
              </bk-select>
            </div>
            <div class="bk-ul-form">
              <bk-input
                :clearable="true"
                :disabled="basicInfo.is_builtin"
                :placeholder="'参数示例'"
                v-model="item.sample">
              </bk-input>
            </div>
            <div class="bk-ul-form">
              <bk-input
                :clearable="true"
                :disabled="basicInfo.is_builtin"
                :placeholder="'备注'"
                v-model="item.desc">
              </bk-input>
            </div>
          </div>
          <div class="bk-request-operat" v-if="!basicInfo.is_builtin">
            <span class="bk-add-node" @click="addQuery(basicInfo.req_params, index)">
              <i class="bk-icon icon-plus" style="font-size: 24px"></i>
            </span>
            <span
              class="bk-reduce-node"
              :class="{ 'bk-reduce-disable': basicInfo.req_params.length === 1 }"
              @click="deleteQuery(basicInfo.req_params, index)">
                 <i class="bk-icon icon-close" style="font-size: 24px"></i>
            </span>
          </div>
        </li>
      </template>
    </ul>
    <!-- Body -->
    <template v-if="basicInfo.method === 'POST'">
      <div class="mb10">
        <bk-button
          :theme="'primary'"
          :title="'导入JSON'"
          :disabled="basicInfo.is_builtin"
          @click="closeDictionary">
          {{ '导入JSON' }}
        </bk-button>
      </div>
      <api-request-body
        :is-body="true"
        :is-builtin="basicInfo.is_builtin"
        :tree-data-list="treeDataList"
        @addBrotherLine="addBodyLine"
        @addChildLine="addBodyChild"
        @deleteLine="deleteBodyLine">
      </api-request-body>
    </template>
    <bk-dialog
      v-model="dictDataTable.showDialog"
      :render-directive="'if'"
      :width="dictDataTable.width"
      :header-position="dictDataTable.headerPosition"
      :loading="secondClick"
      :auto-close="dictDataTable.autoClose"
      :mask-close="dictDataTable.autoClose"
      :title="'导入JSON'"
      @confirm="submitDictionary">
      <div class="bk-add-module">
        <ace
          :value="responseDetailConfig.value"
          :width="responseDetailConfig.width"
          :height="responseDetailConfig.height"
          :read-only="responseDetailConfig.readOnly"
          :lang="responseDetailConfig.lang"
          :full-screen="responseDetailConfig.fullScreen"
          :theme="'textmate'"
          @blur="blur">
        </ace>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import apiRequestBody from './apiRequestBody.vue';
import ace from './acrEditor/index.js';
import mixins from '../mixins/mixins_api.js';

export default {
  components: {
    apiRequestBody,
    ace,
  },
  mixins: [mixins],
  props: {
    detailInfoOri: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      secondClick: false,
      responseDetailConfig: {
        value: '',
        width: '100%',
        height: 200,
        readOnly: false,
        fullScreen: true,
        lang: 'json',
      },
      // 导入JSON
      dictDataTable: {
        showDialog: false,
        width: 700,
        headerPosition: 'left',
        autoClose: false,
        precision: 0,
        formInfo: {
          name: '',
          desc: '',
          id: '',
          code: '',
        },
        checkout: {
          name: '',
        },
      },
      // tag
      titleList: [
        { name: 'Query' },
        { name: 'Body' },
      ],
      checkIndex: 1,
      necessaryList: [
        { id: 1, name: '必选' },
        { id: 0, name: '可选' },
      ],
      // body
      bodyInfo: {
        checkInfo: {},
      },
    };
  },
  computed: {
    // 基本设置
    basicInfo: {
      // getter
      get() {
        return this.detailInfoOri;
      },
      // setter
      set(newVal) {
        this.$parent.DetailInfo = newVal;
      },
    },
    treeDataList: {
      // getter
      get() {
        const treeDataList = this.basicInfo.treeDataList ? [...this.basicInfo.treeDataList] : [];
        treeDataList.forEach((item) => {
          this.recordParent(item, '');
        });
        return treeDataList;
      },
      // setter
      set(newVal) {
        this.$set(this.$parent.DetailInfo, 'treeDataList', newVal);
      },
    },
  },
  created() {
    if (this.basicInfo.req_params && this.basicInfo.req_params.length) {
      this.basicInfo.req_params.forEach((item) => {
        item.is_necessary = item.is_necessary ? 1 : 0;
      });
    }
  },
  methods: {
    initDate() {
      this.treeDataList.forEach((item) => {
        this.recordParent(item, '');
      });
    },
    recordParent(tree, parentInfo) {
      tree.parentInfo = parentInfo;
      if (tree.children == null || (tree.children && !tree.children.length)) {
        return;
      }
      tree.children.forEach((item) => {
        this.recordParent(item, tree);
      });
    },
    changTitle(item, index) {
      this.checkIndex = index;
    },
    // 新增Headers
    addLine(oriData, index) {
      const value = {
        name: '',
        value: '',
        sample: '',
        desc: '',
      };
      oriData.splice(index + 1, 0, value);
    },
    deleteLine(oriData, index) {
      if (oriData.length === 1) {
        return;
      }
      oriData.splice(index, 1);
    },
    // 新增Query
    addQuery(oriData, index) {
      const value = {
        name: '',
        is_necessary: 0,
        sample: '',
        desc: '',
        value: '',
      };
      oriData.splice(index + 1, 0, value);
    },
    deleteQuery(oriData, index) {
      if (oriData.length === 1) {
        return;
      }
      oriData.splice(index, 1);
    },
    // 新增Body
    addBodyLine(node) {
      this.bodyInfo.checkInfo = node;
      if (!node.parentInfo) {
        return;
      }
      const addnode = {
        has_children: false,
        showChildren: false,
        checkInfo: false,
        key: '',
        is_necessary: false,
        default: '',
        type: 'string',
        desc: '',
        parentInfo: node.parentInfo,
      };
      node.parentInfo.children.splice(node.parentInfo.children.indexOf(node) + 1, 0, addnode);
    },
    addBodyChild(node) {
      this.bodyInfo.checkInfo = node;
      const addnode = {
        has_children: false,
        showChildren: false,
        checkInfo: false,
        key: node.type === 'array' ? 'items' : '',
        is_necessary: false,
        default: '',
        type: 'string',
        desc: '',
        parentInfo: this.bodyInfo.checkInfo,
      };
      if (!node.children || !node.children.length) {
        this.$set(node, 'children', []);
        node.children = node.children.splice(0, node.children.length);
        node.has_children = true;
        node.showChildren = true;
      }
      node.children.push(addnode);
    },
    // 删除
    deleteBodyLine(node) {
      this.bodyInfo.checkInfo = node;
      if (!node.parentInfo) {
        return;
      }
      node.parentInfo.children.splice(node.parentInfo.children.indexOf(node), 1);
    },
    closeDictionary(e, id) {
      this.dictDataTable = Object.assign({}, {
        showDialog: !this.dictDataTable.showDialog,
        formInfo: {
          name: '',
          desc: '',
          id: id || '',
          code: '',
        },
        checkout: {
          name: '',
        },
        width: 700,
        headerPosition: 'left',
        autoClose: false,
        precision: 0,
      });
    },
    // 导入JSON
    async submitDictionary() {
      let rootJsonschemaData = {};
      try {
        rootJsonschemaData = this.jsonToJsonschema(JSON.parse(this.responseDetailConfig.value));
        this.basicInfo.treeDataList = this.jsonschemaToList(rootJsonschemaData);
        this.closeDictionary();
      } catch (err) {
        this.$bkMessage({
          message: err.message ? err.message : err,
          theme: 'error',
        });
      }
    },
    blur(content) {
      this.responseDetailConfig.value = content;
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';

.bk-basic-p {
  font-size: 14px;
  color: #737987;
  line-height: 36px;
}

.bk-request-ul {
  li {
    margin-bottom: 10px;
    &::after {
      display: block;
      clear: both;
      content: "";
      font-size: 0;
      visibility: hidden;
    }
  }

  .bk-request-form {
    float: left;
    width: calc(100% - 90px);
    &::after {
      display: block;
      clear: both;
      content: "";
      font-size: 0;
      visibility: hidden;
    }

    .bk-ul-form {
      margin-left: 0px;
      width: 25%;
      float: left;
      padding-right: 20px;
    }
  }

  .bk-request-operat {
    float: right;
    width: 90px;

    .bk-reduce-node,
    .bk-add-node {
      width: 32px;
      height: 32px;
      display: inline-block;
      border: 1px solid #3c96ff;
      font-size: 16px;
      text-align: center;
      line-height: 32px;
      color: #3c96ff;
      cursor: pointer;
    }

    .bk-reduce-node {
      color: #ff5656;
      margin-left: 8px;
    }

    .bk-reduce-disable {
      background-color: #fafafa;
      border: 1px solid #c3cdd7;
      cursor: not-allowed;
      color: #aaa;
    }
  }
}
</style>
