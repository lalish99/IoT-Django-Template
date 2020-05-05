# Custom Access Token:
In order to facilitate the control of access to different devices a custom 
access token class was added, this being `CustomAccessTokens` which can 
generate multiple tokens per user.

This tokens are generated using `UUID4` then hashed using `sha256` hashing algorithm 
for safety purposes.

## Creation and management:
*As of current version* `Access Tokens` can only be manipulated within the admin 
console by super users, and must belong to a user

After the creation of an `Access Token` a message will be displayed with the raw token 
### **IMPORTANT! You must save the token displayed within the message**
after the message disappears there's no way to recover the token, you'll need to delete 
the existing token and create a new one

----
## Adding Custom Token as authentication method:
If you want to add the `Acces Token` as your authentication method in any of the `django-rest` 
views you can include and use the `CAccessTokenRestAuth` class located in `users.api.cauth.py` 