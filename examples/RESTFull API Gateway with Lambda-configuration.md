
# How to Configure RESTFul links using AWS Lambda and API Gateway Services to launch EC2 application

Amazon API Gateway is an AWS service for creating, publishing, maintaining, monitoring, and securing REST, HTTP, and WebSocket APIs at any scale. 
In this tutorial we considered REST APIs. A REST (representational state transfer), also called RESTful API is an architectural style for an 
application program interface (API) that uses HTTP requests to access and use data. That data can be used to GET, PUT, POST and DELETE data types,
which refers to the reading, updating, creating and deleting of operations concerning resources.

### ***To accomplish this process we need to go through configuring three (3) aws services including IAM, Lambda and API Gateway in various steps. This tutorial provides step by step configuration guidline.***

## ***Login and choosing the region***

Go to **www.aws.amazon.com** to **sign in** to the console (on top right corner) using your credentials (username, password, etc.).
Once you are logged in, select the right **Region** (on top right corner) in which you want your deploy your desired services. If this is a new account, default region would work.

## ***IAM (Identity Access Management)***
### Step1.1 --IAM Dashboard--
Go to the **Services** (with 9 dots), click **Security, Identity & Compliance** and choose **IAM** on the right panel. Or, alternatively search for IAM and choose IAM from the services.

![text-here](./APIGateway_Images_dev/1.png)

![text-here](./APIGateway_Images_dev/2.png)

### Step1.1 --Create Role--
Now you are in the IAM dashboard where you can create a new role if you do not have one. Policies are attached to the Role to perform some specific tasks which we will allow you to have permissions to communicate between services. In this page click **Roles** ont the left panel and then **Create role** (blue button on the top right).

![text-here](./APIGateway_Images_dev/3.png)

![text-here](./APIGateway_Images_dev/4.png)

Select the entity type _(in this case it is **AWS Services**)_, next in the **Use Case** choose **API Gateway** as the use case service and select the **API Gateway** radio button, then click **Next** (blue button on the bottom right).

![text-here](./APIGateway_Images_dev/5.png)

In this page you do not need any modifications except clicking **Next** (blue button on the bottom right). 

![text-here](./APIGateway_Images_dev/6.png)

In **Role details**, enter a **Role name** and click **Create role** (blue button on the bottom right). You can leave everything st is. 

***We are done creating the **Role** which was the first step. Now we will move on to the next step which is configuring a lambda function!***

![text-here](./APIGateway_Images_dev/7.png)


![text-here](./APIGateway_Images_dev/8.png)
![text-here](./APIGateway_Images_dev/9.png)
![text-here](./APIGateway_Images_dev/10.png)
![text-here](./APIGateway_Images_dev/11.png)
![text-here](./APIGateway_Images_dev/12.png)
![text-here](./APIGateway_Images_dev/13.png)
![text-here](./APIGateway_Images_dev/14.png)
![text-here](./APIGateway_Images_dev/15.png)
![text-here](./APIGateway_Images_dev/16.png)
![text-here](./APIGateway_Images_dev/17.png)
