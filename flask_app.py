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
    email = request.args.get("email")
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

    return render_template("account.html", username=session["username"])


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

    if postBody:
        postId = str(uuid.uuid4())
        postDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dynamodb_table = dynamodb.Table(DYNAMODB_TABLE)
        dynamodb_table.put_item(
            Item={
                'post': postId,
                'body': postBody,
                'title': titlePost,
                'date': postDate
            }
        )
        return {'post': postId, 'body': postBody,'title': titlePost,'date': postDate},200
    else:
        return 'Failed to upload post!', 400


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


@app.route('/dashboard')
def loadPage():
    dynamodb_table = get_post(DYNAMODB_TABLE)
    response = dynamodb_table.scan()
    items = response['Items']
    sorted_posts = sorted(items, key=lambda x: x['date'], reverse=True)

    return {'result': sorted_posts}



@app.route('/dashboard.html')
def dashboard():
    return render_template("dashboard.html")


@app.route('/register.html')
def register():
    return render_template('register.html')


@app.route('/createaccount', methods=['POST'])
def postAccount():
    email = request.form['txtEmail']
    password = request.form['txtPassword']
    username = str(uuid.uuid4())

    if email and password:

        dynamodb_table = dynamodb.Table(ACCOUNT_TABLE)
        dynamodb_table.put_item(
            Item={
                'email': email,
                'password': password,
                'username': username
            }
        )
        return {'email': email, 'passeord': password, 'username': username},200
    else:
        return 'Failed to create account!', 400


if __name__ == '__main__':
    app.run(debug=True)

