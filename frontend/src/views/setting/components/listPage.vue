<template>
  <div class="list-page"
       v-bkloading="{ isLoading: loading ,zIndex: 9999 }" @click="handleClick">
    <div class="table-config" :class="'is-active'">
      <div class="header-config">
        <div class="function-btn">
          <button-group
            :button-group="config.buttonGroup"
            :current-index="btnGroupIndex"
            :edit="true"
            :work-sheet-id="config.value"
            @deleteItem="handleDelete"
            @handleAddFunction="handleAddFunction">
          </button-group>
        </div>
        <div class="search-icon" @click.stop="isShowSearchInfo=!isShowSearchInfo">
          <i class="custom-icon-font icon-filter-funnel"></i>
        </div>
      </div>
      <search-info
        v-if="filedList.length!==0&&isShowSearchInfo"
        :filed-list="filedList"
        :search-info="config.searchInfo"
        @change="handleAddSearch"
        @delete="handleRemove"
        @end="handleMove">
      </search-info>
      <div class="custom-table" v-if="filedList.length!==0">
        <span
          class="bk-table-setting-icon bk-icon icon-cog-shape setting-icon"
          v-bk-tooltips="htmlConfig"
          ref="settingTooltips">
        </span>
        <div id="setting-content" class="setting-content">
          <div class="filed-content">
            <div class="filed-title">
              <div class="table-setting">表格设置</div>
              <div class="select-all">
                <bk-checkbox v-model="selectAll" @change="handleSelectAll">
                  全选
                </bk-checkbox>
              </div>
            </div>
            <div class="sys-filed">系统字段</div>
            <bk-checkbox-group v-model="sysfileds" style="margin-bottom: 24px">
              <bk-checkbox
                v-for="item in sysfiledList"
                :value="item.key"
                :key="item.key"
                ext-cls="sys-box">
                {{ item.name }}
              </bk-checkbox>
            </bk-checkbox-group>
            <div class="sys-filed">自定义字段</div>
            <div class="custom-container">
              <bk-checkbox-group v-model="customFileds">
                <bk-checkbox
                  v-for="item in selectionFileds"
                  :value="item.key"
                  :key="item.key"
                  ext-cls="sys-box">
                  {{ item.name }}
                </bk-checkbox>
              </bk-checkbox-group>
            </div>
          </div>
          <div class="confirm-sty">
            <bk-button :theme="'primary'" @click="confirm">确定</bk-button>
            <bk-button :theme="'default'" @click="cancel">取消</bk-button>
          </div>
        </div>
        <bk-table
          ext-cls="table-border"
          :data="[{}]"
          :outer-border="false"
          :header-border="false">
          <bk-table-column
            v-for="field in filedList"
            :key="field.key"
            :label="field.name"
            :prop="field.key"
            :show-overflow-tooltip="true">
          </bk-table-column>
          <bk-table-column label="操作" width="200" fixed="right">
            <template slot-scope="{ row }">
              <div class="option-btn-content">
                <bk-button
                  v-for="(btn,index) in config.optionList "
                  :key="btn.key"
                  theme="primary"
                  class="option-btn"
                  :class="index===curIndex&&'option-active'"
                  text
                  :title="btn.name"
                  @click.stop="handleSelectOption(btn,index)">
                   <span class="circle" @click.stop="handleDeleteOptionList(index)" v-if="curIndex===index">
                     <i class="bk-icon icon-close"></i>
                   </span>
                  <span class="btn-name">{{ btn.name }}</span>
                </bk-button>
                <i class="bk-icon icon-plus" @click.stop="handleAddOption" />
              </div>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
import buttonGroup from './buttonGroup.vue';
import { SYS_FIELD } from '@/constants/sysField.js';
import cloneDeep from 'lodash.clonedeep';
import Bus from '@/utils/bus.js';
import searchInfo from './searchInfo.vue';

export default {
  name: 'ListPage',
  components: {
    buttonGroup,
    searchInfo,
  },
  props: {
    list: {
      type: Object,
      default: () => {
      },
    },
  },
  data() {
    return {
      loading: false,
      filedList: [],
      curIndex: -1,
      selectionFileds: [],
      isShowSearchInfo: true,
      btnGroupIndex: 0,
      config: cloneDeep(this.list.config),
      sysfileds: [],
      customFileds: [],
      sysfiledList: SYS_FIELD,
      selectAll: false,
      htmlConfig: {
        allowHtml: true,
        width: 500,
        trigger: 'click',
        theme: 'light',
        content: '#setting-content',
        placement: 'bottom-end',
        extCls: 'custom-tip',
      },
    };
  },
  watch: {
    list: {
      handler(val) {
        this.config = cloneDeep(val.config);
        this.config.value = this.list.value;
        if (val.type === 'LIST' && val.value) {
          this.getTableFileds(Number(val.value));
          // this.config.searchInfo = [];
        } else {
          this.filedList = [];
        }
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    Bus.$on('sendFormData', async (val) => {
      const { option, curIndex, value, workSheetId, name, type, showMode } = val;
      if (option === 'HEADER') {
        this.btnGroupIndex = 0;
        this.curIndex = -1;
        this.config.buttonGroup.splice(curIndex, 1, { option, value, name, type });
      }
      if (option === 'INNER') {
        this.config.optionList.splice(curIndex, 1, { option, value, name, type });
      } else if (option === 'TABLE') {
        if (workSheetId !== this.config.value) {
          this.config.value = workSheetId;
          this.config.fields = [];
          this.config.showMode = '';
          this.config.buttonGroup = [];
          this.config.optionList = [];
          await this.getTableFileds(Number(workSheetId));
          this.config.searchInfo = [];
        } else {
          this.config.show_mode = { mode: showMode };
        }
      }
    });
    Bus.$on('sendConfigRules', (val) => {
      this.config.conditions = val;
    });
  },
  beforeDestroy() {
    Bus.$off('sendFormData');
  },
  methods: {
    handleAddFunction() {
      this.curIndex = -1;
      const item = { option: 'HEADER', value: '', type: '', name: '' };
      this.config.buttonGroup.push(item);
    },
    handleAddOption() {
      this.btnGroupIndex = -1;
      const item = { option: 'INNER', value: '', type: '', name: '默认' };
      this.config.optionList.push(item);
      this.handleSelectOption(item, this.config.optionList.length - 1);
    },
    handleClick() {
      this.curIndex = -1;
      this.btnGroupIndex = -1;
      Bus.$emit('selectFunction', {
        option: 'TABLE',
        workSheetId: this.config.value || '',
        showMode: this.config.show_mode.mode,
      });
    },
    handleSelectOption(item, index) {
      this.btnGroupIndex = -1;
      this.curIndex = index;
      Bus.$emit('selectFunction', {
        ...item,
        curIndex: this.curIndex,
        workSheetId: this.config.value || '',
        showMode: this.config.show_mode.mode,
      });
    },
    async getTableFileds(val) {
      if (val) {
        this.loading = true;
        const tempSysfiledList = this.sysfiledList.filter(filed => this.list.config.fields
          && this.list.config.fields.includes(filed.key));
        try {
          const res = await this.$store.dispatch('setting/getFormFields', val);
          if (this.config.fields.length !== 0) {
            this.filedList = cloneDeep(res.data).filter(item => this.list.config.fields.includes(item.id));
            this.customFileds = this.filedList.map(item => item.key);
          } else {
            this.filedList = cloneDeep(res.data);
            this.customFileds = res.data.map(item => item.key);
          }
          this.filedList.push(...tempSysfiledList);
          this.config.fields = this.filedList.map(item => item.id);
          this.selectionFileds = res.data;
          // this.customFileds = res.data.map(item => item.key);
          this.sysfileds = tempSysfiledList.map(item => item.key);
        } catch (e) {
          console.log(e);
        } finally {
          this.loading = false;
        }
      }
    },
    handleDelete(index) {
      this.config.buttonGroup.splice(index, 1);
    },
    handleAddSearch(item) {
      this.config.searchInfo.push(item.id);
    },
    handleRemove(index) {
      this.config.searchInfo.splice(index, 1);
    },
    handleMove(item) {
      const { newIndex, oldIndex } = item;
      const { searchInfo } = this.config;
      [searchInfo[oldIndex], searchInfo[newIndex]] = [searchInfo[newIndex], searchInfo[oldIndex]];
    },
    handleDeleteOptionList(index) {
      this.config.optionList.splice(index, 1);
    },
    getData() {
      const { value, buttonGroup, fields, optionList, searchInfo, sys_fields, show_mode, conditions } = this.config;
      const params = {
        value,
        config: { buttonGroup, fields, optionList, searchInfo, sys_fields, show_mode, conditions },
      };
      return params;
    },

    cancel() {
      this.$refs.settingTooltips._tippy.hide();
    },
    confirm() {
      const tempList = this.sysfiledList.filter(filed => this.sysfileds.includes(filed.key));
      this.filedList = cloneDeep(this.selectionFileds).filter(field => this.customFileds.includes(field.key));
      this.filedList.push(...tempList);
      this.config.fields = this.filedList.map(item => item.id);
      // tempSearchInfo is record id , customFileds and sysfileds is record key so do some <trans>
      const tempSearchInfo = this.filedList.map((item) => {
        if (this.customFileds.concat(this.sysfileds).includes(item.key)) {
          return item.id;
        }
      });
      this.config.searchInfo = cloneDeep(this.config.searchInfo)
        .filter(filed => tempSearchInfo.includes(filed));
      this.config.sys_fields = tempList.map(item => item.key);
      this.$refs.settingTooltips._tippy.hide();
    },
    handleSelectAll() {
      if (this.selectAll) {
        this.sysfileds.push(...this.sysfiledList.filter(filed => !this.sysfileds.includes(filed.key))
          .map(field => field.key));
        this.customFileds.push(...this.selectionFileds.filter(field => !this.customFileds.includes(field.key))
          .map(field => field.key));
        // this.sysfiledList.filter(filed => this.sysfileds.includes(filed.key)).map(filed => filed.key);
      } else {
        this.sysfileds = [];
        this.customFileds = [];
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
@import "../../../css/scroller.css";

.list-page {
  position: relative;
  height: 100%;

  .circle {
    position: absolute;
    top: -5px;
    right: 20px;
    width: 14px;
    height: 14px;
    background: #979BA5;
    border-radius: 50%;
    display: block;
    z-index: 5;

    i {
      color: #fcfcfc;
      font-size: 14px;
      height: 14px;
      display: block;
      line-height: 14px;
    }
  }

  .table-config {
    margin: 24px;
    padding: 20px 16px;
    border-radius: 2px;
    background: #FFFFFF;
    height: calc(100% - 56px);
    overflow: auto;
    position: relative;
    @mixin scroller;
  }

  .is-active {
    border: 1px dashed #3A84FF;
  }

  .header-config {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .function-btn {
    display: flex;
  }

  .add-btn {
    padding: 2px;
    border: 1px solid transparent;
  }

  .isActive {
    background: #E1ECFF;
    border: 1px dashed #3a84ff;
  }


  .option-active {
    background: #E1ECFF;
    border: 1px dashed #3a84ff;
  }

  .option-btn-content {
    display: flex;
    flex-wrap: wrap;
    width: 200px;
    z-index: 9999;

    i {
      font-size: 20px;
      line-height: 22px;
      color: #3a84ff;
      cursor: pointer;
    }
  }

  .option-btn {
    width: 42px;
    position: relative;

    .btn-name {
      width: 42px;
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
      display: block;
    }
  }


  .table-border {
    margin-top: 16px;
  }

  .search-icon {
    display: flex;
    width: 26px;
    height: 26px;
    background: #FFFFFF;
    border: 1px solid #C4C6CC;
    border-radius: 2px;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    cursor: pointer;

    &:hover {
      border: 1px solid #979BA5;
    }

    i {
      color: #979BA5;
      display: block;
      line-height: 26px;
      margin: auto 0;
    }
  }

  .custom-table {
    position: relative;
  }

  /deep/ .bk-table {
    &::before {
      height: 0;
    }

    .cell {
      overflow: unset;
    }

    .bk-table-column-setting {
      border-left: none;
    }
  }

  .circle {
    position: absolute;
    top: -5px;
    right: -8px;
    width: 12px;
    height: 12px;
    background: #979BA5;
    border-radius: 50%;
    display: block;
    z-index: 5;

    i {
      color: #fcfcfc;
      font-size: 14px;
      height: 14px;
      display: block;
      line-height: 10px;
    }
  }
}

.option-column {
  z-index: 100;
}

.setting-icon {
  position: absolute;
  top: 0;
  right: 0;
  width: 42px;
  height: 42px;
  z-index: 555;
  color: #63656E;
  line-height: 42px;
  border-left: 1px solid #DCDEE5;
}

.setting-icon {
  color: #C4C6CC;;
}

.confirm-sty {
  font-size: 14px;
  padding: 10px;
  height: 50px;
  text-align: right;
  margin-top: 8px;
  margin-left: -14px;
  margin-bottom: -8px;
  margin-right: -14px;
  background-color: #fafbfd;
  border-top: 1px solid #dcdee5;
  border-bottom: 1px solid #dcdee5;
}

.custom-container {
  height: 150px;

  /deep/ .bk-form-control {
    height: 117px;
    overflow: auto;
    margin-bottom: 24px;
    @mixin scroller;
  }
}

.filed-title {
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: content-box;
  padding-bottom: 24px;

  .table-setting {
    font-size: 20px;
    line-height: 28px;
    color: #313238;
    width: 90px;
  }

  .select-all {
    font-size: 14px;
    color: #63656E;
    width: 50px;
  }
}

.sys-filed {
  display: inline-block;
  font-size: 14px;
  color: #313238;
  margin-bottom: 12px;
}

.sys-box {
  display: inline-block;
  width: calc(33.33333% - 15px);
  margin: 10px 15px 0 0;

  /deep/ .bk-checkbox-text {
    overflow: hidden;
    white-space: nowrap;
    width: calc(100% - 22px);
    text-overflow: ellipsis;
  }
}

</style>

<style lang="postcss">
.bk-table-setting-content {
  .content-title {
    display: none;
  }

  .content-line-height {
    display: none;
  }

}

.custom-tip {
  .tippy-tooltip {
    width: 400px !important;
    max-height: 420px;
    border: 1px solid #DCDEE5;
    box-shadow: 0 0 6px 0 #DCDEE5;
  }

  .tippy-content {
    height: 100%;
  }

  .setting-content {
    height: 100%;

    .filed-content {
      min-height: 100%;
      margin-bottom: -50px;
      padding: 13px 10px;;
    }
  }

}
</style>
