<template>
  <div class="permission-content">
    <div class="permission-header">
      <span class="title-icon">
        <img :src="lock" alt="permission-lock" class="lock-img" />
      </span>
      <h3>该操作需要以下权限</h3>
    </div>
    <table class="permission-table table-header">
      <thead>
        <tr>
          <th width="20%">系统</th>
          <th width="30%">需要申请的权限</th>
          <th width="50%">关联的资源实例</th>
        </tr>
      </thead>
    </table>
    <div class="table-content">
      <table class="permission-table">
        <tbody>
          <template v-if="permissionData.actions && permissionData.actions.length > 0">
            <tr v-for="(action, index) in permissionData.actions" :key="index">
              <td width="20%">{{ permissionData.system_name }}</td>
              <td width="30%">{{ action.name }}</td>
              <td width="50%">
                <p
                  class="resource-type-item"
                  v-for="(reItem, reIndex) in getResource(action.related_resource_types)"
                  :key="reIndex">
                  {{ reItem }}
                </p>
              </td>
            </tr>
          </template>
          <tr v-else>
            <td class="no-data" colspan="3">无数据</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PermissionContent',
  props: {
    permissionData: {
      type: Object,
      default: {},
    },
  },
  data() {
    return {
      lock: require('../../assets/images/lock-radius.svg'),
    };
  },
  methods: {
    getResource(resources) {
      if (resources.length === 0) {
        return ['--'];
      }
      console.log(resources);

      const data = [];
      resources.forEach(resource => {
        resource.instances.forEach(instanceItem => {
          if (instanceItem.length === 0) {
            data.push('--');
            return;
          }
          instanceItem.forEach(item => {
            data.push(`${item.type_name || item.name || '--'}`);
          });
        });
      });
      return data;
    },
  },
};
</script>
<style lang="postcss" scoped>
.permission-content {
  width: 100%;
  .permission-header {
    text-align: center;
    .title-icon {
      display: inline-block;
    }
    .lock-img {
      width: 120px;
    }
    h3 {
      margin: 6px 0 24px;
      color: #63656e;
      font-size: 20px;
      font-weight: normal;
      line-height: 1;
    }
  }
  .permission-table {
    width: 100%;
    color: #63656e;
    border-bottom: 1px solid #e7e8ed;
    border-collapse: collapse;
    table-layout: fixed;
    th,
    td {
      padding: 12px 18px;
      font-size: 12px;
      text-align: left;
      border-bottom: 1px solid #e7e8ed;
      word-break: break-all;
    }
    th {
      color: #313238;
      background: #f5f6fa;
    }
  }
  .table-content {
    max-height: 260px;
    border-bottom: 1px solid #e7e8ed;
    border-top: none;
    overflow: auto;
    .permission-table {
      border-top: none;
      border-bottom: none;
      td:last-child {
        border-right: none;
      }
      tr:last-child td {
        border-bottom: none;
      }
      .resource-type-item {
        padding: 0;
        margin: 0;
      }
    }
    .no-data {
      padding: 30px;
      text-align: center;
      color: #999999;
    }
  }
}
.button-group {
  .bk-button {
    margin-left: 7px;
  }
}
</style>
