echo "Configuring DVC remote..."
dvc remote modify --local myremote access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify --local myremote secret_access_key $AWS_SECRET_ACCESS_KEY
dvc remote modify --local myremote region $AWS_DEFAULT_REGION

echo "Running DVC push..."
dvc push
echo "Pushing to S3 Bucket successful"