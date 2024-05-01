@app.route('/dashboard')
def loadPage():
    dynamodb_table = get_post(DYNAMODB_TABLE)
    response = dynamodb_table.scan()
    items = response['Items']
    for item in items: 
       username = item['username']
       account_table = get_table(ACCOUNT_TABLE)
       account_response = account_table.get_item(Key={'username': username})
       
       profile_info = account_response.get('Item')
       profile_pic_filename = profile_info.get('profilePicFile')
       
       item['profilePicFile'] = profile_pic_filename
       item['profilePicURL'] = STORAGE_URL + profile_pic_filename
             
    return {'result': items}     
    