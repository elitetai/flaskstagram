from app import app
import boto3, botocore
import braintree

# S3 AWS
s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config["S3_KEY"],
   aws_secret_access_key=app.config["S3_SECRET"]
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_s3(file, username, acl="public-read"):
   
    try:
        s3.upload_fileobj(
        file,
        app.config["S3_BUCKET"],
        "{}/{}".format(username,file.filename),
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}/{}".format(username,file.filename)

# Braintree payment gateway
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=app.config["BT_ENVIRONMENT"],
        merchant_id=app.config["BT_MERCHANT_ID"],
        public_key=app.config["BT_PUBLIC_KEY"],
        private_key=app.config["BT_PRIVATE_KEY"]
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]