import json
import boto3
import re
import logging

s3 = boto3.client("s3")
ses = boto3.client("ses")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"]) if "body" in event else event
        template_id = body.get("template_id")
        email_address = body.get("emailaddress")

        # Validate required fields
        if not template_id or not email_address:
            missing_field = "template_id" if not template_id else "emailaddress"
            logger.error(f"{missing_field} is required")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"{missing_field} is required"}),
            }

        bucket_name = "5a3f8d8c9f"
        template_file = f"5a3f2c3d8t/{template_id}"  # file path

        # Fetch the HTML template from S3
        try:
            template = (
                s3.get_object(Bucket=bucket_name, Key=template_file)["Body"]
                .read()
                .decode("utf-8")
            )
        except Exception as e:
            logger.error(f"Template not found: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Template not found: {str(e)}"}),
            }

        placeholders = re.findall(r"{{(.*?)}}", template)  # Find placeholders
        logger.info(f"Placeholders found: {placeholders}")

        missing_placeholders = [
            p for p in placeholders if p not in body
        ]  # Check for missing placeholders in the input JSON
        if missing_placeholders:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "error": "Missing placeholders in the input",
                        "missing_fields": missing_placeholders,
                    }
                ),
            }

        for placeholder in placeholders:
            template = template.replace(
                f"{{{{{placeholder}}}}}", str(body[placeholder])
            )  # Replace placeholders

        # Send the email using SES
        try:
            ses.send_email(
                Source="support@captivtech.com",
                Destination={"ToAddresses": [email_address]},
                Message={
                    "Subject": {"Data": "Your Requested Information"},
                    "Body": {"Html": {"Data": template}},
                },
            )
            email_sent_successfully = True
        except Exception as e:
            email_sent_successfully = False
            logger.error(f"Error sending email: {str(e)}")

        first_name = body.get("firstName", "Unknown")
        status_folder = "5a3fs6f2s" if email_sent_successfully else "5a3fa1b7e"
        s3_file_path = f"5a3f5c9a2u/{first_name}/{status_folder}/{email_address}.html"

        s3.put_object(  # Save to S3
            Bucket=bucket_name, Key=s3_file_path, Body=template, ContentType="text/html"
        )
        logger.info(
            f'Email sent successfully to "{email_address}" and the File saved to S3 at {s3_file_path}'
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "File saved successfully!", "file_path": s3_file_path}
            ),
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    event = {
        "template_id": "5a3f1e2u1r.html",
        "firstName": "perumal",
        "emailaddress": "dhanwanthfofficial27@gmail.com",
        "url": "https://www.google.com/",
    }
    print(lambda_handler(event, None))
