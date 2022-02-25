##### 简要描述

- 万能查询：根据筛选条件获取列表的数据

##### 请求URL
- ` /openapi/data_instance/worksheet_data/ `
  
##### 请求方式
- POST 

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|token |是  |string |鉴权token   |
|fields |是  |string |查询字段   |
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
