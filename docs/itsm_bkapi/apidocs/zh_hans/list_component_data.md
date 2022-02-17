##### 简要描述

- 获取某个列表组件的数据

##### 请求URL
- ` /openapi/data_instance/list_component_data/ `
  
##### 请求方式
- POST 

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|version_number |是  |string |版本号   |
|page_id |是  |string |列表页面id   |
|conditions |否  |dict |搜索条件   |


##### 返回示例 

``` 
{
   {
    "result": true,
    "code": "OK",
    "message": "success",
    "data": [
        {
            "id": ,
            "create_at": "",
            "update_at": "",
            "field_key": value,
            ...
        },
       ...
    ]
}
}
 
```
