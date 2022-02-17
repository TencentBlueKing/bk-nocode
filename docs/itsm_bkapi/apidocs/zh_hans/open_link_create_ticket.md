##### 简要描述

- 外链功能:提单

##### 请求URL
- ` /openapi/ticket/create_ticket/ `
  
##### 请求方式
- POST

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|token |是  |string| 鉴权token  |
|fields|是| list|提单字段值|



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
			"sn": "",
			"ticket_url":"", 
            ...
        },
       ...
    ]
}
}
```
