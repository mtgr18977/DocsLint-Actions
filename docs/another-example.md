API Integration Guide

Authentication

To access the private endpoints, an API key is required.
The key can be generated in the user settings dashboard.
Once obtained, the key must be included in the header of every request.

Authorization: Bearer <YOUR_API_KEY>


Creating a User

A user is created by sending a POST request to /api/users.
The following JSON body is expected by the server:

{
  "username": "jdoe",
  "email": "jdoe@example.com"
}


If the request is successful, a 201 Created status is returned.
However, if the data is invalid, a 400 Bad Request error is thrown.

Rate Limiting

Requests are limited to 100 per minute.
If this limit is exceeded, the client is blocked for 60 seconds.