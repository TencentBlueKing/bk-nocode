<template>
  <div class="bk-api-table">
    <div class="bk-api-button mb20">
      <div class="bk-api-button">
        <div>
          <bk-dropdown-menu class="mr10 access-btn" @show="dropdownShow" @hide="dropdownHide" ref="apiDropdown">
            <div class="dropdown-trigger-btn" style="padding-left: 19px;" slot="dropdown-trigger">
              <span style="font-size: 14px;cursor: pointer">{{ '接入' }}</span>
              <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
            </div>
            <ul class="bk-dropdown-list" slot="dropdown-content">
              <li>
                <a href="javascript:;"
                   :title="'接入'"
                   @click="openShade('JOIN')">
                  {{ '接入' }}
                </a>
              </li>
              <li>
                <a href="javascript:;"
                   :title="'新增'"
                   @click="openShade('ADD')">
                  {{ '新增' }}
                </a>
              </li>
            </ul>
          </bk-dropdown-menu>
          <bk-button
            :theme="'default'"
            :title="'点击上传'"
            class="mr10 bk-btn-file">
            <input type="file" :value="fileVal" class="bk-input-file" @change="handleFile">
            {{ '导入' }}
          </bk-button>
          <bk-button
            :theme="'default'"
            class="mr10 batch-remove-btn"
            :title="'批量删除'"
            :disabled="!checkList.length"
            @click="deleteCheck">
            {{ '批量移除' }}
          </bk-button>
        </div>
        <bk-input
          class="bk-api-input"
          v-model="searchInfo.key"
          :placeholder="'请输入关键字'"
          :right-icon="'bk-icon icon-search'"
          :clearable="true"
          @clear="clearInfo"
          @change="handleChange"
          @enter="serchEntry">
        </bk-input>
      </div>
    </div>
    <bk-table
      v-bkloading="{ isLoading: isTableLoading }"
      :size="'small'"
      :data="listInfo"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange"
      @select-all="handleSelectAll"
      :outer-border="false"
      :header-border="false"
      :max-height="defaultTableHeight"
      @select="handleSelect">
      <bk-table-column
        type="selection"
        width="60"
        align="center"
        :selectable="disabledFn">
      </bk-table-column>
      <!--<bk-table-column type="index" label="No." align="center" width="60"></bk-table-column>-->
      <bk-table-column :label="'ID'" width="60" :fixed="true">
        <template slot-scope="props">
          <span :title="props.row.id">{{ props.row.id || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'接口名称'" show-overflow-tooltip width="150" :fixed="true">
        <template slot-scope="props">
          <!-- :disabled="props.row.is_builtin || !!props.row.count" -->
          <span
            class="bk-lable-primary"
            :title="props.row.name"
            @click="entryOne(props.row)">
              {{ props.row.name || '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'接口路径'" show-overflow-tooltip width="250" :fixed="true">
        <template slot-scope="props">
          <span class="bk-table-type">{{ props.row.method }}</span>
          <span :title="props.row.path">{{ props.row.path || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'接口分类'" show-overflow-tooltip width="100">
        <template slot-scope="props">
                    <span :title="systemName(props.row.remote_system)">
                        {{ systemName(props.row.remote_system) || '--' }}
                    </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'状态'" width="60">
        <template slot-scope="props">
                    <span :title="props.row.is_activated ? '启用' : '关闭'">
                        {{ props.row.is_activated ? '启用' : '关闭' }}
                    </span>
        </template>
      </bk-table-column>

      <bk-table-column :label="'负责人'">
        <template slot-scope="props">
          <span :title="props.row.owners">{{ props.row.owners || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'创建人'">
        <template slot-scope="props">
          <span :title="props.row.creator">{{ props.row.creator || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="'接入数'" prop="count" width="80"></bk-table-column>
      <bk-table-column :label="'操作'" width="150" fixed="right">
        <template slot-scope="props">
          <bk-button
            theme="primary" text
            :title="'导出'"
            style="margin-right: 12px"
            :disabled="props.row.is_builtin"
            @click="exportFlow(props.row)">
            {{ "导出" }}
          </bk-button>
          <bk-button
            theme="primary" text
            :title="'编辑'"
            style="margin-right: 12px"
            :disabled="props.row.is_builtin || !!props.row.count"
            @click="entryOne(props.row)">
            {{ "编辑" }}
          </bk-button>
          <bk-button
            theme="primary" text
            :title="'移除'"
            style="margin-right: 12px"
            :disabled="props.row.is_builtin"
            @click="openDelete(props.row)">
            {{ "移除" }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
    <bk-sideslider
      :is-show.sync="entryInfo.show"
      :title="entryInfo.title"
      :width="entryInfo.width">
      <div slot="content" style="padding: 20px" v-if="entryInfo.show">
        <add-api-info
          :first-level-info="firstLevelInfo"
          :tree-list="treeList"
          :type-info="typeInfo">
        </add-api-info>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import { errorHandler } from '../../../utils/errorHandler';
import addApiInfo from './addApiInfo.vue';

export default {
  name: 'ApiTable',
  components: {
    addApiInfo,
  },
  props: {
    treeList: {
      type: Array,
      default() {
        return [];
      },
    },
    listInfoOri: {
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
    firstLevelInfo: {
      type: Object,
      default() {
        return {};
      },
    },
    customPaging: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      secondClick: false,
      isDropdownShow: false,
      // tag
      titleList: [
        { name: 'API列表' },
        // { name: '编辑分类' }
      ],
      checkIndex: 0,
      isTableLoading: false,
      nameInfo: '',
      // 选中
      checkList: [],
      allCheck: false,
      // 查询
      searchInfo: {
        key: '',
      },
      // 分页
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      // 新增服务
      entryInfo: {
        show: false,
        title: '',
        width: 700,
      },
      fileVal: '',
      typeInfo: '',
      defaultTableHeight: '',
    };
  },
  computed: {
    listInfo: {
      // getter
      get() {
        return this.listInfoOri;
      },
      // setter
      set(newVal) {
        this.$parent.listInfo = newVal;
      },
    },
  },
  created() {
    this.defaultTableHeight = 626 - 48 - 32;
  },
  methods: {
    async entryOne(item) {
      this.$parent.displayInfo.level_1 = await item;
      await this.$parent.displayInfo.level_1;
      // 展示 单个api
      await this.$parent.getRemoteApiDetail(item.id);
    },
    getRemoteSystemData() {
      this.$parent.getRemoteSystemData();
      const customPaging = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
      };
      this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
    },
    handleChange(val) {
      if (!val) {
        this.serchEntry();
      }
    },
    systemName(id) {
      const system = this.treeList.filter(item => item.id === id);
      if (system.length) {
        return system[0].name;
      }
      return '--';
    },
    changTitle(item, index) {
      this.checkIndex = index;
    },
    // 新增
    openShade(type) {
      this.typeInfo = type;
      this.entryInfo.title = type === 'ADD' ? '新增接口' : '接入接口';
      this.$refs.apiDropdown.hide();
      this.entryInfo.show = !this.entryInfo.show;
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    // 查询
    serchEntry() {
      this.pagination.current = 1;
      const customPaging = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
      };
      this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
    },
    clearInfo() {
      this.searchInfo.key = '';
      this.serchEntry();
    },
    // 分页过滤数据
    handlePageLimitChange() {
      this.pagination.limit = arguments[0];
      const customPaging = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
      };
      this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      const customPaging = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
      };
      this.$parent.getTableList(this.$parent.displayInfo.level_0.id || '', customPaging, this.searchInfo);
    },
    // 全选 半选
    handleSelectAll(selection) {
      this.checkList = selection;
    },
    handleSelect(selection) {
      this.checkList = selection;
    },
    disabledFn(item) {
      return !item.is_builtin;
    },
    // 二次弹窗确认
    openDelete(item) {
      const h = this.$createElement;
      this.$bkInfoBox({
        type: 'warning',
        subHeader: h('div', {
          style: {
            'font-size': '14px',
          },
        }, '是否删除接口：' + `"${item.name}"?`),
        confirmFn: () => {
          const { id } = item;
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store.dispatch('manage/deleteApi', id).then(() => {
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
    deleteCheck() {
      const h = this.$createElement;
      this.$bkInfoBox({
        type: 'warning',
        subHeader: h('div', {
          style: {
            'font-size': '14px',
          },
        }, '是否批量删除接口？删除后将无法撤销，请谨慎操作。'),
        confirmFn: () => {
          const id = this.checkList.map(item => item.id).join(',');
          if (this.secondClick) {
            return;
          }
          this.secondClick = true;
          this.$store.dispatch('manage/batchDeleteApis', { id }).then(() => {
            this.$bkMessage({
              message: '批量删除成功',
              theme: 'success',
            });
            this.checkList = [];
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
    // 上传文件模板
    handleFile(e) {
      const fileInfo = e.target.files[0];
      if (fileInfo.size <= 10 * 1024 * 1024) {
        const data = new FormData();
        data.append('file', fileInfo);
        const fileType = 'json';
        this.$store.dispatch('manage/getApiImport', { fileType, data }).then((res) => {
          this.$bkMessage({
            message: `成功导入${res.data.success}个API接口，失败${res.data.failed}个`,
            theme: 'success',
          });
          this.getRemoteSystemData();
        }, (res) => {
          this.$bkMessage({
            message: res.data.message,
            theme: 'error',
          });
        })
          .finally(() => {
            this.fileVal = '';
          });
      } else {
        this.fileVal = '';
        this.$bkMessage({
          message: '文件大小不能超过10MB！',
          theme: 'error',
        });
      }
    },
    exportFlow(item) {
      window.open(`${window.SITE_URL}api/postman/remote_api/${item.id}/exports/`);
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';
@import '../../../css/scroller.css';

.bk-api-table {
  padding: 24px;
  height: 626px;

  /deep/ .bk-table {
    &::before {
      height: 0;
    }
   .bk-table-body-wrapper{
      @mixin scroller;
    }
  }
}

.bk-api-button {
  @minix clearfix;
  line-height: 32px;

  .bk-api-title {
    float: left;
    font-size: 14px;
    color: #424951;
  }

  .bk-api-button {
    display: flex;
    justify-content: space-between;

    .access-btn {
      float: left;
      vertical-align: middle;
    }
  }

  .bk-api-input {
    float: left;
    display: block;
    width: 200px;
  }

  .bk-btn-file {
    float: left;
    line-height: 30px;
    position: relative;
    cursor: pointer;

    .bk-input-file {
      position: absolute;
      top: 0;
      left: 0;
      width: 68px;
      height: 32px;
      overflow: hidden;
      opacity: 0;
      cursor: pointer;
      font-size: 0;
    }
  }

  .batch-remove-btn {
    float: left;
  }
}

.bk-table-type {
  padding: 2px 4px;
  background-color: #e1ecff;
  color: #4b8fff;
}

.dropdown-trigger-btn {
  padding: 0 15px;
  height: 32px;
  line-height: 32px;
  color: #63656e;
  font-size: 12px;
  border: 1px solid #c4c6cc;
  border-radius: 2px;

  .bk-icon {
    font-size: 18px;
  }

  .bk-icon {
    font-size: 22px;
  }

  &:hover {
    cursor: pointer;
    border-color: #979ba5;
  }
}

.bk-lable-primary {
  color: #3a84ff;
  cursor: pointer;
}
</style>

