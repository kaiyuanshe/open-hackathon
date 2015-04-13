AWS_ACCESS_KEY_ID=AKIAJMKHNCQNX4ISMHLA
AWS_SECRET_ACCESS_KEY=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
bal_hostname="$HOSTNAME"

PARAMS="AWSAccessKeyId=$AWS_ACCESS_KEY_ID&Action=CreateTags&ResourceId.1=$(curl http://169.254.169.254/latest/meta-data/instance-id)&SignatureMethod=HmacSHA256&SignatureVersion=2&Tag.1.Key=Name&Tag.1.Value=$bal_hostname&Timestamp=$(date -u "+%Y-%m-%dT%H%%3A%M%%3A%SZ")&Version=2013-10-15"
SIGBASE="POST
ec2.amazonaws.com
/
$PARAMS"
SIG="$(echo -n "$SIGBASE" | openssl dgst -sha256 -hmac $AWS_SECRET_ACCESS_KEY -binary | openssl enc -base64 | sed 's/+/%2B/g;s/=/%3D/g;')"

curl -d "$PARAMS&Signature=$SIG" https://ec2.amazonaws.com/
