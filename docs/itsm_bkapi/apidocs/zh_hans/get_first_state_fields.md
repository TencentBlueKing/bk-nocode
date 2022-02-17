##### 简要描述

- 外链功能，获取提单节点字段

##### 请求URL
- ` /openapi/ticket/get_first_state_fields/ `
  
##### 请求方式
- GET 

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|token |是  |string| 鉴权token   |



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
            "key": value,
            ...
        },
       ...
    ]
}
}
```
