<template>
  <div class="list-page" v-bkloading="{ isLoading: loading ,zindex: 999 }">
    <div class="table-config">
      <div class="header-config">
        <div class="function-btn">
          <bk-button
            v-for="(item,index) in config.buttonGroup.slice(0,2)"
            :key="index"
            :theme="index===0?'primary':'default'"
            size="small"
            class="btn-content">
            {{ item.name }}
          </bk-button>
          <bk-button
            :theme="'default'"
            size="small"
            style="margin-left: 8px">
            导出
          </bk-button>
          <bk-dropdown-menu
            @show="dropdownShow"
            @hide="dropdownHide"
            ref="dropdown"
            style="margin-left: 8px"
            v-if="config.buttonGroup.length>2">
            <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
              更多
              <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
            </div>
            <ul class="bk-dropdown-list" slot="dropdown-content"
                v-for="(item,index) in config.buttonGroup.slice(2,config.buttonGroup.length)"
                :key="index">
              <li><a href="javascript:;" @click="triggerHandler('import')">{{item.name}}</a></li>
            </ul>
          </bk-dropdown-menu>
        </div>
        <div class="search-icon">
        </div>
      </div>
      <div class="custom-table" v-bkloading="{ isLoading: loading }">
        <bk-table
          v-if="fields.length!==0"
          ext-cls="table-border"
          :data="tableData"
          :outer-border="false"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          :header-border="false">
          <bk-table-column v-for="field in fields" :key="field.id" :label="field.name" :prop="field.key">
          </bk-table-column>
          <bk-table-column label="操作" width="200">
            <template slot-scope="{ row }">
              <bk-button
                theme="primary"
                style="margin-right:8px "
                @click="handleOptionClick(row,'detail')"
                text>
                详情
              </bk-button>
              <bk-button
                v-for="(btn,index) in config.optionList"
                :key="index"
                theme="primary"
                style="margin-right:8px "
                @click="handleOptionClick(row,btn)"
                text>
                {{ btn.name }}
              </bk-button>
            </template>
          </bk-table-column>
          <bk-table-column type="setting">
            <bk-table-setting-content
              :fields="selectionFields"
              :selected="fields"
              :label-key="'name'"
              :value-key="'id'"
              @setting-change="handleSettingChange">
            </bk-table-setting-content>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'ShowListPage',
  props: {
    filedList: {
      type: Array,
      default: () => [],
    },
    config: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      loading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      selectionFields: cloneDeep(this.filedList),
      fields: cloneDeep(this.filedList),
      isDropdownShow: false,
    };
  },
  watch: {
    filedList(val) {
      this.fields = cloneDeep(val),
      this.selectionFields = cloneDeep(val);
    },
  },
  mounted() {
    this.getTableList();
  },
  methods: {
    async getTableList() {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        page_id: this.$route.params.id,
        version_number: this.$route.params.version,
      };
      try {
        this.loading = true;
        const res = await this.$store.dispatch('application/getListData', params);
        this.tableData = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.log(e);
      } finally {
        this.loading = false;
      }
    },
    handleOptionClick(row, type) {
      this.$emit('handleOptionClick', row, type);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getTableList();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.getTableList();
    },
    handleSettingChange({ fields }) {
      this.fields = fields;
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(item) {
      this.$emit('headerBtnClick', item);
      this.$refs.dropdown.hide();
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
    height: 32px;
    width: 100%;
    display: flex;
    justify-content: space-between;
  }

  .function-btn {
    display: flex;
  }

  .isActive {
    border: 1px dashed #3a84ff;
  }

  .table-border {
    margin-top: 16px;
  }

  .search-icon {
    width: 26px;
    height: 26px;
  }

  /deep/ .bk-table {
    &::before {
      height: 0;
    }

    .bk-table-column-setting {
      border-left: none;
    }
  }
  .dropdown-trigger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #c4c6cc;
    height: 26px;
    border-radius: 2px;
    padding: 0 15px;
    color: #63656E;
  }

  .dropdown-trigger-btn.bk-icon {
    font-size: 18px;
  }

  .dropdown-trigger-btn .bk-icon {
    font-size: 22px;
  }

  .dropdown-trigger-btn:hover {
    cursor: pointer;
    border-color: #979ba5;
  }
  .btn-content{
    margin-left: 8px;
  }
}
</style>
