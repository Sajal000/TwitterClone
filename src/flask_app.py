from flask import Flask, request, redirect, render_template, make_response, session
from flask_session import Session

import boto3
import uuid
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

AWSKEY = 'AKIA2UC3ETKLRFQQWHPJ' 
AWSSECRET = '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'
DYNAMODB_TABLE = 'personal_social'
ACCOUNT_TABLE = 'Users'
PFP_TABLE = 'twitterpfp'

S3_BUCKET_NAME = 'twitterpfp'
STORAGE_URL = "https://twitterpfp.s3.amazonaws.com/"
AWS_REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb',
                          region_name= AWS_REGION,
                          aws_access_key_id= AWSKEY,
                          aws_secret_access_key= AWSSECRET)

def get_table(name):
    client = boto3.resource(service_name='dynamodb',
                        region_name=AWS_REGION,
                        aws_access_key_id=AWSKEY,
                        aws_secret_access_key=AWSSECRET)
    table = client.Table(name)
    return table

def get_post(post):
    client = boto3.resource(service_name='dynamodb',
                        region_name=AWS_REGION,
                        aws_access_key_id=AWSKEY,
                        aws_secret_access_key=AWSSECRET)
    postTable = client.Table(post)
    return postTable

def get_pfp(image_details):
    client = boto3.resource(service_name='dynamodb',
                region_name=AWS_REGION,
                aws_access_key_id=AWSKEY,
                aws_secret_access_key=AWSSECRET)
    pfpTable = client.Table(image_details)
    return pfpTable

def getBucket():
    s3 = boto3.resource(service_name = 's3', 
                        region_name = AWS_REGION, 
                        aws_access_key_id = AWSKEY,
                        aws_secret_access_key = AWSSECRET)
    bucket = s3.Bucket(S3_BUCKET_NAME)
    return bucket

def rememberKey(email):
    table = get_table('remember')
    key = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())

    item = {'key': key, 'email': email}
    table.put_item(Item=item)
    return key


@app.route('/')
def home():
    if is_logged_in():
        return redirect('/account.html')
    return render_template("login.html")


@app.route('/login.html')
def login_page():
    return render_template('login.html')


@app.route('/thing')
def thing():
    return session["thing"]


@app.route('/login')
def login():
    email = request.args.get("email").lower()
    password = request.args.get("password")

    table = get_table("Users")
    item = table.get_item(Key={"email":email})

    if 'Item' not in item:
        return {'result':'Email not found.'}

    user = item['Item']

    if password != user['password']:
        return {'result':'Password does not match.'}

    session["email"] = user["email"]
    session["username"] = user["username"]

    result =  {'result':'OK'}
    response = make_response(result)

    remember = request.args.get('remember')
    if(remember == 'no'):
        response.delete_cookie('remember')
    else:
        key = rememberKey(user['email'])
        response.set_cookie('remember', key, max_age = 60*60*24*14) # Remember for 14 days

    return response


def auto_login():
    cookie = request.cookies.get('remember')
    if cookie is None:
        return False

    table = get_table('remember')
    result = table.get_item(Key={'key': cookie})
    if 'Item' not in result:
        return False

    remember = result['Item'] # row in the remember me table

    table = get_table('Users')
    result = table.get_item(Key = {'email': remember['email']})
    user = result['Item'] # Row from the users table

    session['email'] = user['email']
    session['username'] = user['username']

    return True


def is_logged_in():
    if not session.get("email"):
        return auto_login()
    return True


@app.route('/account.html')
def account():
    if not is_logged_in():
        return redirect("/")
    
    username = session.get("username", "Not loged in") 
    profile_pic_url = get_profile_pic_url(session.get("email"))
    return render_template("account.html", username=username, profile_pic_url=profile_pic_url)


def get_profile_pic_url(email):
    dynamodb_table = get_table(PFP_TABLE)
    response = dynamodb_table.get_item(Key={'email': email})
    if 'Item' in response:
        return response['Item']['profile_pic_url']
    else:
        return None

@app.route('/logout.html')
def logout():
    session.pop("email", None)
    session.pop("username", None)

    response = make_response (redirect("/"))
    response.delete_cookie('remember')
    return response


@app.route('/upload', methods=['POST'])
def upload():
    titlePost = request.form['titlePost']
    postBody = request.form['postBody']
    username = session.get('username')

    if postBody:
        postId = str(uuid.uuid4())
        postDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dynamodb_table = dynamodb.Table(DYNAMODB_TABLE)
        dynamodb_table.put_item(
            Item={
                'post': postId,
                'username': username,
                'body': postBody,
                'title': titlePost,
                'date': postDate
            }
        )
        return {'post': postId,'username': username, 'body': postBody,'title': titlePost,'date': postDate},200
    else:
        return 'Failed to upload post!', 400
    
@app.route('/profilepic', methods=['POST'])
def uploadpfp():
    file = request.files['file']
    if file:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=AWSKEY,
                                 aws_secret_access_key=AWSSECRET,
                                 region_name=AWS_REGION)
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
        
        email = get_email_from_account_table(session.get('email'))
        if email:
            image_uuid = str(uuid.uuid4())

            dynamodb_table = dynamodb.Table(PFP_TABLE)
            dynamodb_table.put_item(
                Item={   
                    'image_details': image_uuid,   
                    'image_name': file.filename,        
                    'email': email
                }
            )
            
            image_url = f"{STORAGE_URL}{file.filename}"
            return {'url': image_url}, 200
        else:
            return 'Failed to retrieve email from the account table!', 500
    else:
        return 'Failed to upload photo!', 400   
    
def get_email_from_account_table(email):
    dynamodb_table = get_table(ACCOUNT_TABLE)
    response = dynamodb_table.get_item(Key={'email': email})
    if 'Item' in response:
        return response['Item']['email']
    else:
        return None
    
@app.route('/delete/<postId>', methods=['DELETE'])
def delete_post(postId):

    if postId:
        dynamodb_table = dynamodb.Table(DYNAMODB_TABLE)
        dynamodb_table.delete_item(
            Key={
                'post': postId
            }
        )
        return 'Post deleted successfully!', 200
    else:
        return 'Failed to delete post!', 400


@app.route('/register.html')
def register():
    return render_template('register.html')


@app.route('/createaccount', methods=['POST'])
def postAccount():
    email = request.form['txtEmail'].lower()
    username = request.form['txtUsername'].lower()
    password = request.form['txtPassword']
    
    if email and password and username:
        
        emailExists = checkEmail(email)
        if emailExists:
            return 'Email already exists!', 400
        
        username = "@" + username
        
        dynamodb_table = dynamodb.Table(ACCOUNT_TABLE)
        dynamodb_table.put_item(
            Item={
                'email': email,
                'password': password,
                'username': username
            }
        )
        return {'email': email, 'password': password, 'username': username},200
    else:
        return 'Failed to create account!', 400


def checkEmail(email):
    dynamodb_table = dynamodb.Table(ACCOUNT_TABLE)
    response = dynamodb_table.get_item(Key={'email': email})
    return 'Item' in response


@app.route('/dashboard')
def loadPage():
    dynamodb_table = get_post(DYNAMODB_TABLE)
    response = dynamodb_table.scan()
    items = response['Items']
    sorted_posts = sorted(items, key=lambda x: x['date'], reverse=True)
    # for post in sorted_posts:
    #     profile_pic_url = get_profile_pic_url(post['username'])
    #     post['profile_pic_url'] = profile_pic_url
    return {'result': sorted_posts}

# @app.route('/dashboard')
# def loadPage():
#     dynamodb_table = get_table(DYNAMODB_TABLE)
#     response = dynamodb_table.scan()
#     items = response['Items']
#     for item in items:
#         item['url'] = STORAGE_URL + items['username']
        
#     return {'results': items } 


@app.route('/dashboard.html')
def dashboard():
    return render_template("dashboard.html")


if __name__ == '__main__':
    app.run(debug=True)
    