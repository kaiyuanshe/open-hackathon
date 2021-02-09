# Kaiyuanshe.Openhackathon.Server
The next generation of backend server for Open Hackathon Platform.

## Develop

#### Install dotnet core
Install dotnet core if you haven't: https://docs.microsoft.com/en-us/dotnet/core/install/

#### Get a ConnectionString of Azure Storage Account. 
Any storage account will do. If you don't have one, contact [Kaiyuanshe Infrastructure Group](mailto:infra@kaiyuanshe.org) to get one for free(for 6 months).

#### Configure locally
Add the ConnectionString to [Environment variables](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-5.0#environment-variables). _**Never submit it to Github!**_. 

##### Windows Sample commands
run as Administrator: `setx Storage__Hackathon__ConnectionString "<The Connection String>" /M`. `setx ... /M` is preferred since it's machine wide and persistent. By contrast, `set ...` only works in current command window.

##### Linux
```
export Storage__Hackathon__ConnectionString="<The Connection String>"
```

##### Mac OS
```
set Storage__Hackathon__ConnectionString="<The Connection String>"
```

#### Run the application
if from command line:
```
git clone git@github.com:kaiyuanshe/open-hackathon.git
cd open-hackathon\src\open-hackathon-server\Kaiyuanshe.OpenHackathon.Server
dotnet restore
dotnet run
```

If from VS Studio/VS Code: open solution file `open-hackathon\src\open-hackathon-server\Kaiyuanshe.OpenHackathon.Server.sln` and click `Run`.

## Deploy
Source code is built as Docker image, can be run anywhere including Kubernetes. Below is the current deployment steps on Azure App Services

### Deploy to Azure App Service(Azure China)
- Create a new Azure App Service
- _[Optional]_Configure custom domain and certificate. For issue new certificate, see https://github.com/shibayan/keyvault-acmebot. For custom domain, see https://docs.azure.cn/zh-cn/app-service/app-service-web-tutorial-custom-domain
- configure github actions to build and publish: https://docs.microsoft.com/en-us/azure/app-service/deploy-container-github-action?tabs=publish-profile. 
