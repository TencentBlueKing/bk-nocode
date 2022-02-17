##### A brief description

- External link function: bill of lading

##### Request URL
- ` /openapi/ticket/create_ticket/`
  
##### request method
- POST

##### Parameters

|Parameter name|Required|Type|Description|
|:---- |:---|:----- |----- |
|token |Yes |string| Authentication token |
|fields|is |list|B/L Field Values|



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
"sn": "",
"ticket_url":"",
            ...
        },
       ...
    ]
}
}
````
