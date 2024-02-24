# Scripts

## Configuration

- Copy `.env.sample` to `.env` and adjust the value from the placeholders accordingly

## AssumeRoleWithWebIdentity

- Ensure you are currently logged in or part-of and authenticated to Cloud Identity object defined in [this variable](https://github.com/franzramadhan/franzramadhan-dot-dev-materials/blob/master/02-gcp-to-aws-short-lived-credential/iac/01_gcp_serviceaccount/01-variables.tf#L5)
- Ensure [gcp_assume_aws_role](./gcp_assume_aws_role) is executable and copy it to `/usr/local/bin`
- You can test the script by invoking it directly. The output should be something similar to:

   ```json
    {
      "Version": 1,
      "AccessKeyId": "ASIAWTPCDEUL",
      "SecretAccessKey": "5fKpGI2Y8ZqoAb",
      "SessionToken": "IQoJb3JpZ2luX2VjEKL//////////wEaDmFwLXNvdXRoZWFzdC0xIkgwRgIhAMG6hor6KOyzome/tswp7BtlSt9fvLBgSK5Ib6dJ1IBIAiEA8ZXiD7joZf1YKr501Oo7mFl/wDTSkMYcWHHlpsAGGZ4qzAIIi///////////ARAEGgw0NTQxMzAwODMwOTQiDJtv1p6ekFvSokXybiqgApe15ORWW6U1MKrjfe9pGoTGJnIOcCTF4+bcvL7XakIsnXwToevOJ5VzwMBSMMcIj0fy52O+lKEq2NYZR2z6m3aeIdd98iuuZJTFqAab6q+HgADv0V+dS+rvhl0+E4MVsmTON/wIIqud7dvuc=",
      "Expiration": "2024-02-02T10:10:10+00:00"
    }
   ```

- Append the content of [config.sample](./config.sample) to the `~/aws/config` so you can easily switch to your designated profile for GCP. Adjust the parameters accordingly.

## WorkloadIdentityFederation for Service Account Access Token Credential

- Ensure you have authenticated to the authorized IAM role ARN for your workload identity provider.
- Execute the [aws_impersonate_gcp_sa.py](./aws_impersonate_gcp_sa.py). You will get output similar to this:

  ```text
  {"audience": "1231231231231231321", "expiration_unix_timestamp": "1708771574", "expiration_in_seconds": "3599", "access_token": "ya29.c.c0AY_VpZgpg4w-QvHwRdN1Oz-PYs6gtF7Ypa0oROKXeQcU37zwz0f6RlALvYS_iH_SSsdFZLcp7bU-NKFoG6-dOAglfBRV90mVgHB-2Sy1WIuEafPzEvkItskZYHb21fZn2xGHRPe30ktOhuGUjEcCExyKqUEJ-pKJwb1fvZqdRdaWUWokxTBtDYDFPaJHwj2pFFylr7xjW60z4cBMjyfxXJFpuX-l7-qokSz9k_WsUfV4-fmzJeuzX49lIvj5nuRjqQuoy3BjleSqscdtqkBWbq4aoSl4nkM8OWvnoug_QFmFlejmwoSFupBdX-nX2SdMXuFgYyc6v6f38Xs5caXRm0rZ_z"}
  ```

- You can parse the access_token only <br>
  `python aws_impersonate_gcp_sa.py | jq -r '.access_token'`.
- Once you already have an access token, use one of the following methods to pass the access token to the gcloud CLI:
  - Store the access token in a file and set its path through the --access-token-file flag.
  - Store the access token in a file and set its path in the auth/access_token_file property.
  - Set the CLOUDSDK_AUTH_ACCESS_TOKEN environment variable to the access token value.

## References:
- [https://cloud.google.com/sdk/docs/authorizing](https://cloud.google.com/sdk/docs/authorizing)

