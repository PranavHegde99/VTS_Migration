Action()
{
    // Start a transaction to measure the time taken to push data to DynamoDB via API Gateway
    lr_start_transaction("PushDataToDynamoDB");

    // Register a parameter to capture the response from the API Gateway
    web_reg_save_param("Response", "LB=", "RB=", LAST);

    // Send the POST request to the API Gateway
    web_custom_request("PushDataToDynamoDB",
        "URL={GEN_URL}",
        "Method=POST",
        "TargetFrame=",
        "Resource=0",
        "RecContentType=application/json",
        "Mode=HTML",
        "EncType=application/json",  // Set content type to JSON
        "Body={"
            "\"PORT\": \"1007\","
            "\"data\": ["
                "{\"Name\": \"Pranav\", \"phone_number\": \"101-101-1010\", \"age\": 21, \"hobbies\": \"swimming\"},"
                "{\"Name\": \"Vindhya\", \"phone_number\": \"102-102-412\", \"age\": 22, \"hobbies\": \"running\"},"
                "{\"Name\": \"Aditya\", \"phone_number\": \"103-103-1030\", \"age\": 23, \"hobbies\": \"drawing\"}"
            "]}",
            LAST);

    // Log the response for debugging
    lr_output_message("Lambda Response: %s", lr_eval_string("{Response}"));

    // Validate the response and end the transaction based on success or failure
    if (strstr(lr_eval_string("{Response}"), "Item") != NULL) {
        lr_end_transaction("PushDataToDynamoDB", LR_PASS);
    } else {
        lr_end_transaction("PushDataToDynamoDB", LR_FAIL);
    }

    return 0;
}
