<template>
  <div class="bk-api-run-config">
    <bk-input v-model="DetailInfo.path" :disabled="trueStatus">
      <template slot="prepend">
        <bk-dropdown-menu
          class="group-text"
          ref="requestwayDrop"
          slot="append"
          :font-size="'normal'"
          :disabled="trueStatus">
          <bk-button type="primary" slot="dropdown-trigger">
            <span> {{ DetailInfo.method }} </span>
            <i :class="['bk-icon icon-angle-down']"></i>
          </bk-button>
        </bk-dropdown-menu>
      </template>
      <template slot="append">
        <bk-button
          ext-cls="append-btn"
          :theme="'primary'"
          :title="'发送'"
          @click="testUrl">
          {{ '发送' }}
        </bk-button>
      </template>
    </bk-input>
    <div class="mt20 bk-run-configure">
      <bk-collapse v-model="activeName">
        <bk-collapse-item name="1" :ext-cls="'bk-border-line'">
          Query
          <template slot="content" v-if="DetailInfo.req_params && DetailInfo.req_params.length">
            <ul class="mb10">
              <li v-for="(item, index) in DetailInfo.req_params" :key="index" class="bk-run-content">
                <bk-input
                  style="width: 130px; margin-right: 10px;"
                  class="bk-run-input"
                  :disabled="trueStatus"
                  v-model="item.name">
                </bk-input>
                <bk-checkbox
                  :true-value="trueStatus"
                  :false-value="falseStatus"
                  v-model="item.is_necessary">
                </bk-checkbox>
                <span>=</span>
                <bk-input
                  style="width: calc(100% - 185px); float: right;"
                  class="bk-run-input"
                  v-model="item.value">
                </bk-input>
              </li>
            </ul>
          </template>
        </bk-collapse-item>
        <bk-collapse-item name="2">
          Body
          <div slot="content" class="mb10">
            <ace
              :value="bodyDetailConfig.value"
              :width="bodyDetailConfig.width"
              :height="bodyDetailConfig.height"
              :read-only="bodyDetailConfig.readOnly"
              :lang="bodyDetailConfig.lang"
              :full-screen="bodyDetailConfig.fullScreen"
              :theme="'textmate'"
              @blur="blur">
            </ace>
          </div>
        </bk-collapse-item>
      </bk-collapse>
    </div>
  </div>
</template>

<script>
import { errorHandler } from '../../../utils/errorHandler';
import ace from './acrEditor/index.js';
import mixins from '../mixins/mixins_api.js';

export default {
  components: {
    ace,
  },
  mixins: [mixins],
  props: {
    apiDetailInfoCommon: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      trueStatus: true,
      falseStatus: false,
      bodyDetailConfig: {
        value: '',
        width: '100%',
        height: 300,
        readOnly: false,
        fullScreen: true,
        lang: 'json',
      },
      DetailInfo: this.apiDetailInfoCommon,
      // url数据
      formInfo: {
        code: 'POST',
        poc: 'poc：https://paas-poc.o.',
        url: '/api/user/create',
      },
      // 显示隐藏
      showInfo: {
        headers: false,
        query: false,
        body: false,
      },
      // headersList
      headersList: [
        {
          key: 'id',
          value: '',
        },
      ],
      // queryList
      queryList: [
        {
          key: '',
          is_necessary: false,
          value: '',
        },
      ],
      // body
      bodyValue: '1415',
      secondClick: false,
      activeName: [],
    };
  },
  async mounted() {
    await this.apiDetailInfoCommon;
    await this.DetailInfo;
    this.initDate();
  },
  methods: {
    initDate() {
      if (this.DetailInfo.bodyJsonData) {
        this.bodyDetailConfig.value = JSON.stringify(this.DetailInfo.bodyJsonData.root, null, 4);
      }
      if (this.DetailInfo.req_params && this.DetailInfo.req_params.length) {
        this.DetailInfo.req_params.forEach((item) => {
          item.is_necessary = !!item.is_necessary;
        });
      }
    },
    showConten(val) {
      this.showInfo[val] = !this.showInfo[val];
    },
    async testUrl() {
      this.showInfo = {
        headers: false,
        query: false,
        body: false,
      };
      if (this.secondClick) {
        return;
      }
      const params = {
        id: this.DetailInfo.id,
        req_headers: this.listTojson(this.DetailInfo.req_headers.filter(item => !!item.name)),
        req_params: this.listTojson(this.DetailInfo.req_params.filter(item => !!item.name)),
        req_body: JSON.parse(this.bodyDetailConfig.value),
        sys_headers: {},
        cookies: {},
        variables: {},
        map_code: this.$parent.dataProcess.value,
        before_req: this.$parent.reqDataProcess.value,
      };
      this.secondClick = true;
      await this.$store.dispatch('manage/runRemoteApi', params).then((res) => {
        this.$parent.alarmDetailConfig.value = JSON.stringify(res.data, null, 4);
        if (res.data.result) {
          this.$parent.isSuccess = false;
        }
      })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.secondClick = false;
        });
    },
    blur(content) {
      try {
        this.bodyDetailConfig.value = JSON.stringify(JSON.parse(content), null, 4);
      } catch (e) {
        return;
      }

      try {
        JSON.parse(this.bodyDetailConfig.value);
      } catch (err) {
        // this.$bkMessage({
        //     message: err.message ? err.message : err,
        //     theme: 'error'
        // })
        return;
      }
      const tempArr = JSON.parse(this.bodyDetailConfig.value);
      this.apiDetailInfoCommon.bodyJsonschemaData = this.jsonToJsonschema(tempArr);
    },
    listTojson(listdata) {
      const jsondata = {};
      if (listdata.length) {
        listdata.forEach((item) => {
          jsondata[item.name] = item.value;
        });
      }
      return jsondata;
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';

.append-btn {
  border: none;
  height: 30px;
  border-radius: 0;
  border-bottom: 1px solid #dcdee5;
}

.bk-run-configure {
  border: 1px solid #dde4eb;
  background-color: #fafafa;

  .bk-run-content {
    margin-bottom: 10px;

    &::after {
      display: block;
      clear: both;
      content: "";
      font-size: 0;
      visibility: hidden;
    }

    .bk-run-input {
      float: left;
    }
  }
}

.bk-border-line {
  border-bottom: 1px solid #dde4eb;
}
</style>
