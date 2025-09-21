Action()
{
    lr_start_transaction("FetchData");


    // Save the full response body for debugging
    web_reg_save_param_ex(
        "ParamName=response_body",
        "LB=",
        "RB=",
        "Notfound=warning",
        LAST);

    // Register to capture the "Name" field
    web_reg_save_param_json(
        "ParamName=Name",
        "QueryString=$.data.Name",  // Extract "Name" from "data"
        LAST);

    // Register to capture the "phone_number" field
    web_reg_save_param_json(
        "ParamName=PhoneNumber",
        "QueryString=$.data.phone_number",  // Extract "phone_number" from "data"
        LAST);

    // Register to capture the "age" field
    web_reg_save_param_json(
        "ParamName=Age",
        "QueryString=$.data.age",  // Extract "age" from "data"
        LAST);

    // Register to capture the "hobbies" field
    web_reg_save_param_json(
        "ParamName=Hobbies",
        "QueryString=$.data.hobbies",  // Extract "hobbies" from "data"
        LAST);

    // Send the GET request to the API Gateway
    web_custom_request("FetchData",
        "URL={gen_url}",
        "Method=GET",
        "TargetFrame=",
        "Resource=0",
        "RecContentType=application/json",
        "Mode=HTML",
        LAST);

    // Log the captured values
    lr_output_message("Name: %s", lr_eval_string("{Name}"));
    lr_output_message("Phone Number: %s", lr_eval_string("{PhoneNumber}"));
    lr_output_message("Age: %s", lr_eval_string("{Age}"));
    lr_output_message("Hobbies: %s", lr_eval_string("{Hobbies}"));

    lr_end_transaction("FetchData", LR_PASS);

    return 0;
}
