# 📝 AWS-Serverless-Contact-Form

<p align="center">
  <img src="https://img.shields.io/badge/AWS-Free%20Tier-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Serverless-100%25-black?style=for-the-badge&logo=serverless&logoColor=white"/>
</p>

A project to create a **Contact Form** on AWS using Serverless Services.
AWS Serverless Contact Form is a cloud-native, fully serverless application for collecting and managing user tickets. It uses **Amazon S3**, **API Gateway**, and **AWS Lambda** for backend processing, and **DynamoDB** and **SES** for data storage and real-time email notifications—without the need for traditional servers or EC2.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [AWS Services](#-aws-services)
- [Project Structure](#-project-structure)
- [Deployment Steps](#-deployment-steps)
- [Testing](#-testing)
- [Cost Estimate](#-cost-estimate)
- [Cleanup](#-cleanup)

---

## 🎯 Overview

**Contact Form** is a production-ready serverless contact form built entirely on AWS. Users fill out a form, their message is saved to DynamoDB, and the site Admin receives an instant email via SES — all without managing any servers.

### ✨ Features

- ✅ **Real-time form submission** with loading state
- ✅ **Instant email notifications** to site Admin via Amazon SES
- ✅ **Input validation** on both client and server side
- ✅ **Honeypot protection** to block automated spam bots
- ✅ **100% Serverless** — zero server management
- ✅ **Runs entirely on AWS Free Tier**

---

## 🏗️ Architecture
![AWS Architecture Diagram](images/Contact%20Form%20AWS.png)
---

## ☁️ AWS Services

| Service | Role | Free Tier Limit |
|---|---|---|
| **Amazon S3** | Hosts the static frontend | 5GB + 20K GETs/month |
| **Amazon API Gateway** | REST API endpoints | 1M requests/month (1st year) |
| **AWS Lambda** | Backend business logic | 1M invocations/month |
| **Amazon DynamoDB** | Stores all messages | 25GB + 200M requests/month |
| **Amazon SES** | Email notifications | 1,000 emails/month |
| **AWS IAM** | Lambda permissions | Always free |

---

## 📁 Project Structure

```text
contact-project/
│
├── frontend/
│   ├── index.html        # Contact form UI
│   ├── style.css         # Styles and responsive design
│   └── script.js         # API calls and form logic
│
├── lambda/
│   └── lambda_function.py # Handles POST /contact & GET /stats
│
└── README.md
```

## 🚀 Deployment Steps


### Step 1 — Create DynamoDB Table

1. Open [AWS Console](https://console.aws.amazon.com) → search **DynamoDB**
2. Click **Create table**
3. Fill in:
   - **Table name:** `contact-messages`
   - **Partition key:** `message_id` → type: **String**
4. Under **Table settings** → choose **Customize settings**
5. **Capacity mode:** On-demand
6. Click **Create table**
7. Wait until status shows **Active** ✅

---

### Step 2 — Create SES
Search **SES**  → **Create Identity**
1. From Configuration → Identities → Create identity
2. **Identity type:** Email address
3. **Email address:** Add your email

---

### Step 3 — Create IAM Policy & Role

**Create the Policy:**

1. Search **IAM** → **Policies** → **Create policy**
2. Click the **JSON** tab → paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/contact-messages"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

3. Click **Next**
4. **Policy name:** `contact-lambda-policy`
5. Click **Create policy**

**Create the Role:**

6. **IAM** → **Roles** → **Create role**
7. **Trusted entity:** AWS service → **Lambda**
8. Click **Next**
9. Search for `contact-lambda-policy` → check it ✅
10. Click **Next**
11. **Role name:** `contact-lambda-role`
12. Click **Create role**
---

### Step 4 — Create Lambda Function

1. Search **Lambda** → **Create function**
2. Choose **Author from scratch**
3. Fill in:
   - **Function name:** `contact-handler`
   - **Runtime:** Python 3.12
4. Under **Permissions** → **Change default execution role**
5. Choose **Use an existing role** → `contact-lambda-role`
6. Click **Create function**

**Upload the code:**

7. In the **Code** tab → open `lambda/lambda_function.py` in VSCode
8. Select all (`Ctrl+A`) → copy (`Ctrl+C`)
9. In the Lambda editor → select all → paste → click **Deploy** 🟠

**Set environment variables:**

10. Go to **Configuration** → **Environment variables** → **Edit**
11. Click **Add environment variable** twice:

| Key | Value |
|---|---|
| `TABLE_NAME` | `contact-messages` |
| `SENDER_EMAIL` | your email you add in Identity |

12. Click **Save**

**Set timeout:**

13. **Configuration** → **General configuration** → **Edit**
14. **Timeout:** `0 min 15 sec`
15. Click **Save**

---

### Step 5 — Create API Gateway

1. Search **API Gateway** → **Create API**
2. Choose **REST API** → **Build**
3. **API name:** `contact-api`
4. Click **Create API**

**Create POST /contact:**

5. **Actions** → **Create Resource**
6. **Resource name:** `contact` → **Create Resource**
7. With `/contact` selected → **Actions** → **Create Method** → `POST` → ✓
8. **Integration type:** Lambda Function
9. ✅ Enable **Use Lambda Proxy integration**
10. **Lambda Function:** `contact-handler`
11. Click **Save** → **OK**
12. **Actions** → **Enable CORS** → **Enable CORS and replace existing CORS headers** → **Yes, replace**

**Create GET /stats:**

13. Click root `/` → **Actions** → **Create Resource**
14. **Resource name:** `stats` → **Create Resource**
15. With `/stats` selected → **Actions** → **Create Method** → `GET` → ✓
16. **Integration type:** Lambda Function
17. ✅ Enable **Use Lambda Proxy integration**
18. **Lambda Function:** `contact-handler`
19. Click **Save** → **OK**
20. **Actions** → **Enable CORS** → **Enable CORS and replace existing CORS headers** → **Yes, replace**

**Deploy the API:**

21. **Actions** → **Deploy API**
22. **Deployment stage:** `[New Stage]`
23. **Stage name:** `prod`
24. Click **Deploy**
25. **Copy and save the Invoke URL** — looks like:
    
    ```
    https://xxxxxxxxxx.execute-api.us-east-2.amazonaws.com/prod
    ```

---
### Step 6 — Update Frontend Config

1. Open `frontend/script.js` in VSCode
2. On **line 4**, replace:
   
   ```js
   const API_URL = "https://YOUR_API_ID.execute-api.us-east-2.amazonaws.com/prod";
   ```
   with your real Invoke URL:
   ```js
   const API_URL = "https://xxxxxxxxxx.execute-api.us-east-2.amazonaws.com/prod";
   ```
3. Save the file (`Ctrl+S`)

---

### Step 7 — Create S3 Bucket & Upload Files

1. Search **S3** → **Create bucket**
2. **Bucket name:** `contact-frontend-YOUR_ACCOUNT_ID`
   > Find your Account ID: click your name (top right) in the Console
3. **Region:** us-east-2
4. Under **Block Public Access** → **uncheck** "Block all public access"
5. Confirm the warning checkbox
6. Click **Create bucket**

**Upload files:**

7. Open your bucket → click **Upload** → **Add files**
8. Select all 3 files from VSCode:
   - `frontend/index.html`
   - `frontend/style.css`
   - `frontend/script.js`
9. Click **Upload**

**Enable Static Website Hosting:**

10. Go to **Properties** tab → scroll down → **Static website hosting** → **Edit**
11. **Enable** → Index document: `index.html`
12. Click **Save changes**

**Add Bucket Policy:**

13. Go to **Permissions** tab → **Bucket policy** → **Edit**
14. Paste (replace `YOUR-BUCKET-NAME` with your actual bucket name):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
  }]
}
```

15. Click **Save changes**
16. 
----

### Step 8 — Go Live! 🎉

1. Open your **S3 Bucket** → **Properties** tab.
2. Scroll down to **Static website hosting** and copy the **Bucket website endpoint**.
3. Open the endpoint URL in your browser:
   ```text
   http://contact-frontend-YOUR_ACCOUNT_ID.s3-website.us-east-2.amazonaws.com
   ```

**Your serverless contact form is now live and fully operational on the internet!**

---

## 🧪 Testing

### Test Lambda directly

In Lambda → **Test** tab → paste this event payload and click **Test**:

```json
{
  "httpMethod": "POST",
  "path": "/contact",
  "body": "{\"name\":\"Ali Soliman\",\"email\":\"test@example.com\",\"subject\":\"AWS Test\",\"message\":\"This is a direct test message for Lambda execution.\"}"
}
```

**Expected response:**

```json
{
  "statusCode": 200,
  "body": "{\"message_id\": \"uuid-here\", \"message\": \"Your message has been sent successfully!\"}"
}
```

### Test the full flow

| Action | Expected Result |
| --- | --- |
| **Open S3 Website URL** | Contact form loads with styled UI |
| **Submit empty form** | Client-side validation triggers |
| **Submit valid message** | ✅ Green success notification appears |
| **Check verified inbox** | Email alert received via SES |
| **Open DynamoDB → Explore items** | New record added in `contact-messages` |
| **GET `/stats` endpoint** | Returns updated total count |

---

## 💰 Cost Estimate

| Service | Free Tier Limit | Expected Usage | Cost |
| --- | --- | --- | --- |
| **AWS Lambda** | 1M requests/month | ~500 | **$0** |
| **Amazon API Gateway** | 1M requests/month | ~500 | **$0** |
| **Amazon DynamoDB** | 25GB + 200M requests | < 1MB | **$0** |
| **Amazon S3** | 5GB storage + 20K GETs | < 1MB | **$0** |
| **Amazon SES** | 1,000 emails/month | ~100 | **$0** |

### 💵 Total estimated monthly cost: **$0.00**

---

## 🧹 Cleanup

To prevent unexpected AWS charges, delete resources in the following sequence:

1. **Amazon S3** → Empty `contact-frontend-YOUR_ACCOUNT_ID` bucket → Delete bucket
2. **Amazon API Gateway** → Delete `contact-api`
3. **AWS Lambda** → Delete `contact-handler` function
4. **Amazon DynamoDB** → Delete `contact-messages` table
5. **Amazon SES** → Delete verified identity
6. **AWS IAM** → Delete `contact-lambda-role` → Delete `contact-lambda-policy`

---

## 🔮 Future Improvements

* [ ] Add **Amazon CloudFront** for global CDN delivery & custom HTTPS certificate
* [ ] Add **Amazon Cognito** for secure admin authentication dashboard
* [ ] Add **Automated User Confirmation Responses** via Amazon SES
* [ ] Add **API Gateway Throttling & Rate Limiting** to prevent abuse
* [ ] Store message **attachments** in S3
* [ ] Add **spam filter** using Amazon Comprehend

---
