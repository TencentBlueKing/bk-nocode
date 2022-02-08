<template>
  <div class="bk-api-tree">
    <div class="bk-tree-content">
      <div class="bk-tree-title">
        <span>应用选择</span>
        <span class="bk-icon icon-minus" @click="handleChangeSlider"></span>
      </div>
      <div class="search-content">
        <bk-input v-model="searchWord" :right-icon="'bk-icon icon-search'" :clearable="true" @clear="clearInfo">
        </bk-input>
        <bk-dropdown-menu
          class="group-text"
          @show="dropdownShow"
          @hide="dropdownHide"
          ref="dropdown"
          style="line-height: 32px">
          <div class="dropdown-trigger-btn" slot="dropdown-trigger">
            <i :class="['bk-icon icon-plus', { 'icon-flip': isDropdownShow }]"></i>
          </div>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li>
              <a href="javascript:;" :title="'接入'" @click="openDictionary('JION')">
                {{ '接入' }}
              </a>
            </li>
            <li>
              <a href="javascript:;" :title="'新增'" @click="openDictionary('ADD')">
                {{ '新增' }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
      </div>
      <div class="bk-tree-info" v-bkloading="{ isLoading: isTreeLoading }">
        <ul class="bk-tree-group" @scroll="scrollEvent">
          <li v-for="(item, index) in treeList" :key="index" @click="showBackground(item, index, 0)">
            <template v-if="!item.id">
              <div class="bk-group-parent bk-p18" :class="{ 'bk-group-li': item.check }">
                <span>{{ '全部系统' }}</span>
              </div>
            </template>
            <template v-else>
              <div class="bk-group-parent bk-p18 bk-handel" :class="{ 'bk-group-li': item.check }">
                <span class="bk-group-name">{{ item.name }}</span>
                <span style="display: inline-block" class="bk-edit" v-if="item.can_edit">
                  <i class="bk-icon icon-more bk-tree-point bk-point-selected"></i>
                  <ul class="bk-more" :style="styletranslateY">
                    <li v-if="!item.is_builtin" @click.stop="openDelete(item)">
                      <span>{{ '删除' }}</span>
                    </li>
                    <li @click.stop="openDictionary('CHANGE', item)">
                      <span>{{ '编辑' }}</span>
                    </li>
                  </ul>
                </span>
              </div>
              <collapse-transition>
                <template v-if="item.showMore && false">
                  <ul class="bk-group-child">
                    <li
                      v-for="(node, nodeIndex) in item.apis"
                      :key="nodeIndex"
                      class="bk-p42"
                      :class="{ 'bk-group-li': node.check }"
                      @click.stop="showBackground(node, index, 1)">
                      <span class="bk-group-child-name">{{ node.name }}</span>
                    </li>
                  </ul>
                </template>
              </collapse-transition>
            </template>
          </li>
        </ul>
      </div>
    </div>
    <!-- 接入系统 -->
    <bk-dialog
      v-model="dictDataTable.showDialog"
      :render-directive="'if'"
      :width="dictDataTable.width"
      :header-position="dictDataTable.headerPosition"
      :auto-close="dictDataTable.autoClose"
      :mask-close="dictDataTable.autoClose"
      :title="dictDataTable.title">
      <div class="bk-add-module">
        <bk-form
          :label-width="200"
          form-type="vertical"
          :model="dictDataTable.formInfo"
          :rules="rules"
          ref="dictDataForm">
          <template v-if="dictDataTable.type === 'ADD'">
            <bk-form-item :label="'系统名称：'" :required="true" :property="'addName'">
              <bk-input :clearable="true" v-model="dictDataTable.formInfo.addName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="'系统编码：'" :required="true" :property="'addCode'">
              <bk-input :clearable="true" v-model="dictDataTable.formInfo.addCode"></bk-input>
            </bk-form-item>
          </template>
          <template v-else>
            <bk-form-item :label="'系统名称：'" :required="true" :property="'code'">
              <template v-if="dictDataTable.type === 'CHANGE'">
                <bk-select
                  disabled
                  v-model="dictDataTable.formInfo.code"
                  :clearable="false"
                  searchable
                  @selected="changeCode">
                  <bk-option v-for="option in allCodeList" :key="option.id" :id="option.code" :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
              <template v-else>
                <bk-select v-model="dictDataTable.formInfo.code" :clearable="false" searchable @selected="changeCode">
                  <bk-option v-for="option in codeList" :key="option.id" :id="option.code" :name="option.name">
                  </bk-option>
                </bk-select>
              </template>
            </bk-form-item>
          </template>
          <bk-form-item
            :label="'系统域名：'"
            :property="'domain'"
            desc-type="border"
            :desc="{ content: '从蓝鲸API网关中接入的系统，不需要填写系统域名。', placements: ['right'] }">
            <bk-input :clearable="true" v-model="dictDataTable.formInfo.domain"></bk-input>
          </bk-form-item>
          <bk-form-item :label="'负责人：'">
            <member-select v-model="dictDataTable.formInfo.personInCharge"> </member-select>
          </bk-form-item>
          <bk-form-item :label="'备注：'">
            <bk-input :placeholder="'请输入备注'" :type="'textarea'" :rows="3" v-model="dictDataTable.formInfo.desc">
            </bk-input>
          </bk-form-item>
          <bk-form-item :label="'启用：'">
            <bk-switcher v-model="dictDataTable.formInfo.is_activated" size="small"></bk-switcher>
          </bk-form-item>
        </bk-form>
      </div>
      <div slot="footer" class="king-slider-footer">
        <bk-button theme="primary" @click="submitDictionary" :loading="secondClick"> 确定</bk-button>
        <bk-button theme="default" @click="closeDictionary" style="margin-left: 8px" :disabled="secondClick">
          取消
        </bk-button>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import collapseTransition from '../mixins/collapse-transition.js';
import memberSelect from '@/components/memberSelect.vue';
import commonMix from '@/commonMix/common.js';
import { errorHandler } from '../../../utils/errorHandler.js';
export default {
  name: 'ApiTree',
  components: {
    collapseTransition,
    memberSelect,
  },
  mixins: [commonMix],
  props: {
    treeListOri: {
      type: Array,
      default() {
        return [];
      },
    },
    codeList: {
      type: Array,
      default() {
        return [];
      },
    },
    allCodeList: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      secondClick: false,
      // 基本信息人员数组
      basicPerson: {
        // 禁用数组
        disabledList: [],
      },
      styletranslateY: {
        transform: 'translate(40px,-20px)',
      },
      isTreeLoading: false,
      searchWord: '',
      // 接入系统
      dictDataTable: {
        showDialog: false,
        width: 700,
        headerPosition: 'left',
        autoClose: false,
        precision: 0,
        formInfo: {
          addName: '',
          addCode: '',
          name: '',
          desc: '',
          code: '',
          domain: '',
          owners: '',
          personInCharge: [],
          contact_information: '',
          id: '',
          system_id: '',
          is_activated: true,
        },
      },
      isDropdownShow: false,
      rules: {},
    };
  },
  computed: {
    treeList: {
      // getter
      get() {
        const vm = this;
        return this.treeListOri.filter(item => item.name.indexOf(vm.searchWord) !== -1);
      },
      // setter
      set(newVal) {
        newVal.forEach((item) => {
          const ori = this.$parent.treeList.filter(ite => ite.system_id === item.system_id && ite.id === item.id);
          if (ori.length) {
            ori[0] = JSON.parse(JSON.stringify(item));
          }
        });
      },
    },
  },
  async mounted() {
    await this.treeListOri;
    // 获取所有系统
    await this.showBackground(this.treeList[0], 0, 0);
    // 校验
    this.rules.code = this.checkCommonRules('select').select;
    this.rules.addName = this.checkCommonRules('name').name;
    this.rules.addCode = this.checkCommonRules('key').key;
  },
  methods: {
    scrollEvent($event) {
      this.styletranslateY.transform = `translate(40px,${-$event.target.scrollTop - 20}px)`;
    },
    changeCode(code) {
      const dataItem = this.codeList.filter(item => item.code === code)[0];
      this.dictDataTable.formInfo.name = dataItem.name;
      this.dictDataTable.formInfo.system_id = dataItem.system_id;
    },
    clearInfo() {
      this.searchWord = '';
    },
    // 展开/收起tree
    showGroupChild(item) {
      item.showMore = !item.showMore;
      this.treeList = [...JSON.parse(JSON.stringify(this.treeList))];
    },
    // 显示底色
    showBackground(item, index, level) {
      if (!level) {
        this.$parent.displayInfo.level_1 = {};
        this.$parent.displayInfo.level_0 = item;
        // 展示 api列表
        // this.$parent.showConetnt = false
        this.$parent.getTableList(item.id);
        // this.$parent.getChannelPathList(item.system_id)
      } else {
        this.$parent.displayInfo.level_1 = item;
        // 展示 单个api
        // this.$parent.showConetnt = true
        this.$parent.getRemoteApiDetail(item.id);
      }
      this.treeList.forEach((tree) => {
        this.recordCheckFn(tree);
      });
      item.check = true;
      this.treeList = [...JSON.parse(JSON.stringify(this.treeList))];
    },
    recordCheckFn(tree) {
      tree.check = false;
      if (tree.apis && tree.apis.length) {
        tree.apis.forEach((node) => {
          node.check = false;
        });
      }
    },
    getRemoteSystemData() {
      this.$parent.getRemoteSystemData();
    },
    // 接入系统/修改系统
    async submitDictionary() {
      this.$refs.dictDataForm.validate().then(
        () => {
          if (this.secondClick) {
            return;
          }
          this.dictDataTable.formInfo.owners = this.dictDataTable.formInfo.personInCharge.join(',');
          const params = {
            name: this.dictDataTable.formInfo.name,
            desc: this.dictDataTable.formInfo.desc,
            code: this.dictDataTable.formInfo.code,
            domain: this.dictDataTable.formInfo.domain,
            system_id: this.dictDataTable.formInfo.system_id,
            owners: this.dictDataTable.formInfo.owners,
            contact_information: this.dictDataTable.formInfo.contact_information,
            is_activated: this.dictDataTable.formInfo.is_activated,
            headers: [],
            cookies: [],
            variables: [],
            // 现阶段先写死
            project_key: 'public',
          };
          if (this.dictDataTable.type === 'ADD') {
            params.name = this.dictDataTable.formInfo.addName;
            params.code = this.dictDataTable.formInfo.addCode;
          }
          if (this.dictDataTable.title === '修改系统') {
            params.id = this.dictDataTable.formInfo.id;
            this.secondClick = true;
            this.$store
              .dispatch('manage/putRemoteSystem', params)
              .then((res) => {
                this.$bkMessage({
                  message: '修改成功',
                  theme: 'success',
                });
                this.getRemoteSystemData();
                this.closeDictionary();
              })
              .catch((res) => {
                errorHandler(res, this);
              })
              .finally(() => {
                this.secondClick = false;
              });
            return;
          }
          this.secondClick = true;
          this.$store
            .dispatch('manage/postRemoteSystem', params)
            .then(() => {
              this.$bkMessage({
                message: '添加成功',
                theme: 'success',
              });
              this.getRemoteSystemData();
              this.closeDictionary();
            })
            .catch((res) => {
              this.$bkMessage({
                message: res.data.msg,
                theme: 'error',
              });
            })
            .finally(() => {
              this.secondClick = false;
            });
        },
        (validator) => {
          console.warn(validator);
        }
      );
    },
    openDictionary(type, item) {
      this.dictDataTable.showDialog = true;
      this.dictDataTable.type = type;
      this.dictDataTable.title = type === 'ADD' ? '新增系统' : item ? '修改系统' : '接入系统';
      this.dictDataTable.formInfo = {
        addName: '',
        addCode: '',
        name: item ? item.name : '',
        desc: item ? item.desc : '',
        domain: item ? item.domain : '',
        code: item ? item.code : '',
        owners: item ? item.owners : '',
        personInCharge: item && item.owners ? item.owners.split(',') : [],
        contact_information: item ? item.contact_information : '',
        id: item ? item.id : '',
        system_id: item ? item.system_id : '',
        is_activated: item ? item.is_activated : true,
      };
      this.$refs.dropdown.hide();
    },
    closeDictionary() {
      this.dictDataTable.showDialog = false;
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    // 二次弹窗确认
    openDelete(item) {
      this.$bkInfoBox({
        type: 'warning',
        title: '确认移除系统？',
        subTitle: '移除后，将无法使用该系统，请谨慎操作',
        confirmFn: () => {
          const { id } = item;
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store
            .dispatch('manage/deleteRemoteSystem', id)
            .then(() => {
              this.$bkMessage({
                message: '删除成功',
                theme: 'success',
              });
              this.getRemoteSystemData();
            })
            .catch((res) => {
              errorHandler(res, this);
            })
            .finally(() => {
              this.secondClick = false;
            });
        },
      });
    },
    handleChangeSlider() {
      this.$emit('changeSlider', false);
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';
@import '../../../css/scroller.css';
.bk-api-tree {
  padding: 20px 10px;


  .icon-minus{
    cursor: pointer;
  }
  .search-content {
    display: flex;
    justify-content: space-between;
    .group-text {
      margin-left: 4px;
    }
    .dropdown-trigger-btn {
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      width: 32px;
      height: 32px;
      background: #ffffff;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      text-align: center;
      font-size: 16px;
      i{
        line-height: 32px;
        font-size: 16px;
        color: #737987;
      }
    }
  }
  .bk-tree-title {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    span {
      font-family: MicrosoftYaHei;
      font-size: 12px;
      color: #63656e;
      display: inline-block;
      letter-spacing: 0;
      line-height: 20px;
      &:nth-child(2) {
        font-weight: 700;
      }
    }
  }
}

.bk-tree-info {
  color: #737987;
  font-size: 14px;
  line-height: 36px;
  min-height: 300px;
  margin-top: 12px;

  .bk-tree-group {
    height: 100%;
    @mixin scroller;
    @mixin scroller;
    overflow: auto;

    li {
      cursor: pointer;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    .bk-group-li {
      color: #4b8fff;
      background-color: #e1ecff;
    }

    .bk-group-name {
      display: inline-block;
      width: calc(100% - 72px);
    }

    .bk-group-child-name {
      display: inline-block;
      width: calc(100% - 30px);
    }

    .bk-p42 {
      padding-left: 42px;
    }

    .bk-p18 {
      padding-left: 18px;
    }

    .bk-ml5 {
      margin-right: 5px;
    }
  }
}

.bk-handel {
  position: relative;

  .bk-icon.icon-more.bk-tree-point.bk-point-selected {
    position: absolute;
    top: 8px;
    right: 0;
    font-size: 19px;
    line-height: 19px;
    cursor: pointer;
    font-weight: 500;
  }
}

.bk-group-parent.bk-handel {
  position: relative;

  .bk-edit {
    &:hover {
      .bk-more {
        display: inline-block;
      }
    }
  }

  .bk-more {
    display: none;
    position: fixed;
    width: 79px;
    background: #fff;
    -webkit-box-shadow: 0px 2px 2px 2px rgba(227, 225, 225, 0.5);
    box-shadow: 0px 2px 2px 2px rgba(227, 225, 225, 0.5);
    border-radius: 2px;
    z-index: 10;

    ul {
      width: 100%;
      height: 100%;
    }

    li {
      width: 100%;
      height: 36px;
      line-height: 36px;
      color: #63656e;
      text-align: center;
      cursor: pointer;
      font-size: 14px;

      &:hover {
        background: rgba(163, 197, 253, 0.2);
        color: #3a84ff;
      }
    }
  }
}

.bk-api-tree .bk-form .bk-label {
  font-weight: 500;
}
.group-text {
  cursor: pointer;
}
</style>
