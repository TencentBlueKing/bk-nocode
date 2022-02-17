##### A brief description

- External chain function, get the bill of lading node field

##### Request URL
- ` /openapi/ticket/get_first_state_fields/`
  
##### request method
- GET

##### Parameters

|Parameter name|Required|Type|Description|
|:---- |:---|:----- |----- |
|token |Yes |string| Authentication token |



##### Return to example

````
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
````
