# -*- coding: utf-8 -*-
#
# This file is covered by the LICENSING file in the root of this project.
#

FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build-env
WORKDIR /app

# Copy csproj and restore as distinct layers
COPY ./src/open-hackathon-server/Kaiyuanshe.OpenHackathon.Server/*.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY ./src/open-hackathon-server ./
RUN dotnet publish -c Release -o out

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:5.0
WORKDIR /app
COPY --from=build-env /app/out .
ENTRYPOINT ["dotnet", "Kaiyuanshe.OpenHackathon.Server.dll"]