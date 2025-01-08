# How to create a pipeline to deploy on kubernetes cluster 

In this article we assume you have kubernetes, jenkins configured to follow along. In this article our goal is to configure a simple pipeline that will deploy a small application into kubernetes. For now, I will not add the trigger feature, meaning when a github commited is made an auto job will be triggered on jenkins. For we will manually trigger the job. 



How-To-Guides

How to setup K3s cluster setup convience script: https://github.com/sohaib1khan/kubernetes_craft/tree/main/k3s_setup

How to deploy Jenkin on kubernetes/K3s: https://github.com/sohaib1khan/kubernetes_craft/tree/main/Skaffold_Deployments/jenkins 

How to configure remote server with Jenkins: https://read.helixx.cloud/en/CiCD/Jenkins/HowtoRunJobsonRemoteServerfromJenkins


### Add Kubecomfig to Jenkins

Using kubectl config view: If kubectl is already configured on your machine, you can view the active configuration (kubeconfig) by running:

bash

    kubectl config view --raw > ~/kubeconfig

    Generate New Kubeconfig for Service Accounts: If needed, you can create a new kubeconfig for a service account. This is more advanced but allows for fine-grained access control in Kubernetes.

Upload Kubeconfig to Jenkins:

Once you have the kubeconfig file, follow these steps to upload it to Jenkins:

    Go to Jenkins > Manage Jenkins > Manage Credentials.
    Select the appropriate domain (usually Global credentials).
    Click Add Credentials.
    In the Kind dropdown, select Secret file.
    Upload your kubeconfig file (e.g., the one you saved as ~/kubeconfig).
    Give it an ID, for example, kubeconfig-file.

After this, you can reference this file in your Jenkinsfile as mentioned earlier.
Next Steps:

    Retrieve or generate your kubeconfig file from your Kubernetes cluster.
    Upload it as a Secret file in Jenkins credentials.
    Update your Jenkinsfile to use this secret file as shown in my previous messages.




To address the GitHub credentials issue properly:

    Create a Personal Access Token (PAT) on GitHub if you haven’t already:
        Go to GitHub > Settings > Developer settings > Personal access tokens.
        Create a new token with repo and workflow permissions.
        Copy the token and store it somewhere safe (you won’t be able to view it again).

    Add Credentials to Jenkins:
        In Jenkins, go to Manage Jenkins > Manage Credentials.
        Under the appropriate Domain (Global by default), click Add Credentials.
        Set the Kind to Username with password.
            Username: Your GitHub username.
            Password: The Personal Access Token (PAT) you just created.
        Give the credentials an ID (e.g., github-credentials).

    Configure the Pipeline to Use the Credentials:
        In your Jenkins pipeline configuration (the one you set up for the job), go to the Git section where you specified the Git repository URL.
        Make sure the Credentials dropdown is set to the credentials you just added (e.g., github-credentials).


You need to store your Kubeconfig file in Jenkins as a Secret file credential, not as a username/password credential.
Step-by-Step Instructions to Fix This:

    Store Kubeconfig as a Secret File:
        Go to Manage Jenkins > Manage Credentials > Global credentials (unrestricted) > Add Credentials.
        In the Kind dropdown, select Secret file.
        Upload your kubeconfig file.
        Give it a recognizable ID (e.g., kubeconfig-file).




# How to create a pipeline to deploy on kubernetes cluster 

In this article we assume you have kubernetes, jenkins configured to follow along. In this article our goal is to configure a simple pipeline that will deploy a small application into kubernetes. For now, I will not add the trigger feature, meaning when a github commited is made an auto job will be triggered on jenkins. For we will manually trigger the job. 



How-To-Guides

How to setup K3s cluster setup convience script: https://github.com/sohaib1khan/kubernetes_craft/tree/main/k3s_setup

How to deploy Jenkin on kubernetes/K3s: https://github.com/sohaib1khan/kubernetes_craft/tree/main/Skaffold_Deployments/jenkins 

How to configure remote server with Jenkins: https://read.helixx.cloud/en/CiCD/Jenkins/HowtoRunJobsonRemoteServerfromJenkins


### Add Kubecomfig to Jenkins

Using kubectl config view: If kubectl is already configured on your machine, you can view the active configuration (kubeconfig) by running:

bash

    kubectl config view --raw > ~/kubeconfig

    Generate New Kubeconfig for Service Accounts: If needed, you can create a new kubeconfig for a service account. This is more advanced but allows for fine-grained access control in Kubernetes.

Upload Kubeconfig to Jenkins:

Once you have the kubeconfig file, follow these steps to upload it to Jenkins:

    Go to Jenkins > Manage Jenkins > Manage Credentials.
    Select the appropriate domain (usually Global credentials).
    Click Add Credentials.
    In the Kind dropdown, select Secret file.
    Upload your kubeconfig file (e.g., the one you saved as ~/kubeconfig).
    Give it an ID, for example, kubeconfig-file.

After this, you can reference this file in your Jenkinsfile as mentioned earlier.
Next Steps:

    Retrieve or generate your kubeconfig file from your Kubernetes cluster.
    Upload it as a Secret file in Jenkins credentials.
    Update your Jenkinsfile to use this secret file as shown in my previous messages.




To address the GitHub credentials issue properly:

    Create a Personal Access Token (PAT) on GitHub if you haven’t already:
        Go to GitHub > Settings > Developer settings > Personal access tokens.
        Create a new token with repo and workflow permissions.
        Copy the token and store it somewhere safe (you won’t be able to view it again).

    Add Credentials to Jenkins:
        In Jenkins, go to Manage Jenkins > Manage Credentials.
        Under the appropriate Domain (Global by default), click Add Credentials.
        Set the Kind to Username with password.
            Username: Your GitHub username.
            Password: The Personal Access Token (PAT) you just created.
        Give the credentials an ID (e.g., github-credentials).

    Configure the Pipeline to Use the Credentials:
        In your Jenkins pipeline configuration (the one you set up for the job), go to the Git section where you specified the Git repository URL.
        Make sure the Credentials dropdown is set to the credentials you just added (e.g., github-credentials).


You need to store your Kubeconfig file in Jenkins as a Secret file credential, not as a username/password credential.
Step-by-Step Instructions to Fix This:

    Store Kubeconfig as a Secret File:
        Go to Manage Jenkins > Manage Credentials > Global credentials (unrestricted) > Add Credentials.
        In the Kind dropdown, select Secret file.
        Upload your kubeconfig file.
        Give it a recognizable ID (e.g., kubeconfig-file).


verificaiton on remote server: 

devk3s@devk3s:~/.kube$ kubectl get pod -A -w
NAMESPACE     NAME                                      READY   STATUS      RESTARTS      AGE
kube-system   coredns-7b98449c4-sdg6x                   1/1     Running     1 (13h ago)   22h
kube-system   helm-install-traefik-8gjgw                0/1     Completed   1             22h
kube-system   helm-install-traefik-crd-mjj7l            0/1     Completed   0             22h
kube-system   local-path-provisioner-6795b5f9d8-22wh9   1/1     Running     1 (13h ago)   22h
kube-system   metrics-server-cdcc87586-b9mm9            1/1     Running     1 (13h ago)   22h
kube-system   svclb-nginx-service-fdb6762c-p2h8c        1/1     Running     0             3m23s
kube-system   svclb-traefik-feefabf7-b24p4              2/2     Running     2 (13h ago)   22h
kube-system   traefik-67f6c94c47-lcd75                  1/1     Running     1 (13h ago)   22h
nginxtest     nginx-deployment-75455c549d-c8fv2         1/1     Running     0             3m23s
nginxtest     nginx-deployment-6bdb64d588-wh22f         0/1     Pending     0             0s
nginxtest     nginx-deployment-6bdb64d588-wh22f         0/1     Pending     0             0s
nginxtest     nginx-deployment-6bdb64d588-wh22f         0/1     Init:0/1    0             0s
nginxtest     nginx-deployment-6bdb64d588-wh22f         0/1     PodInitializing   0             1s
nginxtest     nginx-deployment-6bdb64d588-wh22f         1/1     Running           0             2s
nginxtest     nginx-deployment-75455c549d-c8fv2         1/1     Terminating       0             3m43s
nginxtest     nginx-deployment-75455c549d-c8fv2         0/1     Terminating       0             3m43s
nginxtest     nginx-deployment-75455c549d-c8fv2         0/1     Terminating       0             3m44s
nginxtest     nginx-deployment-75455c549d-c8fv2         0/1     Terminating       0             3m44s


