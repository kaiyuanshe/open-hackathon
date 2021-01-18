Open Hackathon Platform
======

![dotnet build, push and publish](https://github.com/kaiyuanshe/open-hackathon/workflows/dotnet%20build,%20push%20and%20publish/badge.svg)

# Introduction
Open Hackathon Platform

The Open Hackathon Platform is a cloud-based platform to enable Hackathon organizers to host an offline/online hackathon with most needed features; Hackathon event participants can use a HTML5 capable web browser to login an Hackathon event, provision his development environment of choice and collaborate with teammates.

The Open Hackathon can be deployed as a standalone web application, and can leverage Docker based technology to efficiently manage the cloud resources.

# Contributing
Pull request is welcome and appreciated.

Questions go to [dev team](mailto:msopentechdevsh@microsoft.com)

# Documenation

## Event Participator
For user who wants to browse and attend hackathon events, please see [User Guide](https://github.com/kaiyuanshe/open-hackathon/wiki/%E5%BC%80%E6%94%BE%E9%BB%91%E5%AE%A2%E6%9D%BE%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)

## Event Organizer
For those who wants to create a new hackathon event or manage existing ones, please follow [Organizer Guide](https://github.com/kaiyuanshe/open-hackathon/blob/master/documents/organizer_guide.md)

## Developer
For those who wants to contribute to Open Hackathon, pleae choose one of the following. Open Hackathon has mainly two parts, a Web UI presentation layer and a backend api server, both were written in Python in the first place. Recently we are working to move it to modern technologies. The UI layer is being rewritten using Node Js and the backend API is being replaced with Dotnet Core 3.1.
- To contribute to new Web UI, please visit [OpenHackathon Web 2.0](https://github.com/kaiyuanshe/OpenHackathon-Web) for more details.
- To contribute to new backend API server, please browse to directory `src`. The docs are ongoing. Basically it's a typical DotNet core Web App.
- To contribute to v1.0 Web UI and/or API, please read [Developer Guide](https://github.com/kaiyuanshe/open-hackathon/blob/master/documents/developer_guide.md). They are being retired, currently only critical fixes accepted. Read [manual](https://github.com/kaiyuanshe/open-hackathon/blob/master/documents/README.md) for more.

# Author
The project is now maintained by Kaiyuanshe.

# License
This project is licensed under [MIT License](https://github.com/kaiyuanshe/open-hackathon/blob/master/LICENSE.md)

