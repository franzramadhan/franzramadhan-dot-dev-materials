import json
import urllib
import requests
import base64
import boto3
import configargparse

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from dotenv import load_dotenv


def generate_token_aws(project_number: str, workload_identity_pool_id: str, workload_identity_provider_id: str) -> bytes:
    # Prepare a GetCallerIdentity request.
    request = AWSRequest(
        method="POST",
        url="https://sts.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
        headers={
            "Host": "sts.amazonaws.com",
            "x-goog-cloud-target-resource": f"//iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{workload_identity_pool_id}/providers/{workload_identity_provider_id}",
        },
    )

    # Set the session credentials and Sign the request.
    # get_credentials loads the required credentials as environment variables.
    # Refer:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    SigV4Auth(boto3.Session().get_credentials(), "sts", "us-east-1").add_auth(request)

    # Create token from signed request.
    token = {"url": request.url, "method": request.method, "headers": []}
    for key, value in request.headers.items():
        token["headers"].append({"key": key, "value": value})

    # The token lets workload identity federation verify the identity without revealing the AWS secret access key.
    return bytes(urllib.parse.quote(json.dumps(token)), 'utf-8')

def generate_sts_federated_access_token_gcp(aws_subjet_token:str, project_number: str, workload_identity_pool_id: str, workload_identity_provider_id:str) -> str:
    
    aws_sigv4_token = base64.b64encode(aws_subjet_token)
    
    url = "https://sts.googleapis.com/v1/token"
    headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
    params = {
      "audience":f'//iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{workload_identity_pool_id}/providers/{workload_identity_provider_id}',
      "grant_type":"urn:ietf:params:oauth:grant-type:token-exchange",
      "requested_token_type":"urn:ietf:params:oauth:token-type:access_token",
      "scope":"https://www.googleapis.com/auth/cloud-platform",
      "subject_token_type":"urn:ietf:params:aws:token-type:aws4_request",
      "subject_token": base64.b64decode(aws_sigv4_token)
    }
    
    response = requests.post(url, params=params, headers=headers).json()
    return response["access_token"]
    

def generate_service_account_token_gcp(federated_access_token: str,service_account_unique_id: str, gcp_project_number: str, workload_identity_pool_id: str, workload_identity_provider_id:str) -> str:
    
    url = f'https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{service_account_unique_id}:generateAccessToken'
    headers = {
        'Content-Type' : 'text/json; charset=utf-8',
        'Authorization': f'Bearer {federated_access_token}'
    }
    data = '{"scope":["https://www.googleapis.com/auth/cloud-platform"]}'
    
    response = requests.post(url, data=data, headers=headers).json()
    return response["accessToken"]

def get_token_info(service_account_access_token: str) -> dict:
    
    url = f'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={service_account_access_token}'
    response = requests.get(url).json()
    
    result = dict()
    result["audience"] = response["aud"]
    result["expiration_unix_timestamp"] = response["exp"]
    result["expiration_in_seconds"] = response["expires_in"]
    return result

def main() -> None:
    
    load_dotenv()

    parser = configargparse.ArgParser(description='Get service-account access_token from AWS IAM role credential.')
    parser.add_argument("--gcp-project-number", dest='gcp_project_number' , env_var='GCP_PROJECT_NUMBER', help='gcp project number', required=True, type=str )
    parser.add_argument("--gcp-workload-identity-pool-id", dest='gcp_workload_identity_pool_id', env_var='GCP_WI_POOL_ID', help='gcp workload-identity pool-id', required=True, type=str )
    parser.add_argument("--gcp-workload-identity-provider-id", dest='gcp_workload_identity_provider_id', env_var='GCP_WI_PROVIDER_ID', help='gcp workload-identity pool-number', required=True, type=str )
    parser.add_argument("--gcp-service-account-unique-id", dest='gcp_service_account_unique_id', env_var='GCP_SERVICE_ACCOUNT_UNIQUE_ID', help='gcp service-account unique-id', required=True, type=str )
    args = parser.parse_args()
    
    
    # implementation 
    gcp_project_number = args.gcp_project_number
    service_account_unique_id = args.gcp_service_account_unique_id
    workload_identity_pool_id = args.gcp_workload_identity_pool_id
    workload_identity_provider_id = args.gcp_workload_identity_provider_id
    
    aws_token_encoded = generate_token_aws(gcp_project_number, workload_identity_pool_id, workload_identity_provider_id)
    sts_federated_access_token = generate_sts_federated_access_token_gcp(aws_token_encoded, gcp_project_number, workload_identity_pool_id, workload_identity_provider_id)
    service_account_token = generate_service_account_token_gcp(sts_federated_access_token, service_account_unique_id, gcp_project_number, workload_identity_pool_id, workload_identity_provider_id)

    result = dict()
    result["service_account_credential"] = get_token_info(service_account_token)
    result["service_account_credential"]["access_token"] = service_account_token
    
    print(json.dumps(result["service_account_credential"]))
    
if __name__ == "__main__":
    main()
