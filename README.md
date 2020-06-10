# Text Similarity REST API with Flask and MongoDB
A RESTful API that returns how much similar two texts are using Natural Language Processing.
Information is saved to a Mongo Database.

## See how the API works

https://virgoaugustine.github.io/text-similarity-frontend


## API

#### /register
* `POST`: Register as a new user to access the API
```
          { 
            "name": "",
            "username": "",
            "email": "",
            "password":""
          }
```

#### /login
* `POST`: Login as an existing user to access the API
```
          { 
            "username": "",
            "password":""
          }
```
#### /detect
* `POST` : Find the similarity between two texts.
```
            { 
              "username": "",
              "text1":"",
              "text2":""
             }
 ```
#### /refill
*   `POST`: Refill a user's tokens
```
  {
    "username": "",
    "admin_password": "",
    "refillNumber": ""
  }
```
    

