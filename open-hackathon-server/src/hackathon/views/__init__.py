# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys

sys.path.append("..")

from hackathon import api

from resources import *

__all__ = ["init_routes"]


def init_routes():
    """Register RESTFul API routes"""
    # health page API
    api.add_resource(HealthResource, "/", "/health")

    # system time API
    api.add_resource(CurrentTimeResource, "/api/currenttime")

    # APIs for template library
    api.add_resource(TemplateResource, "/api/template")  # query, create or delete template
    api.add_resource(TemplateCreateByFileResource, "/api/template/file")  # create template from file
    api.add_resource(TemplateListResource, "/api/template/list")  # list templates

    # APIs for hackathon query that not related to user or admin
    api.add_resource(HackathonResource, "/api/hackathon")  # query hackathon
    api.add_resource(HackathonListResource, "/api/hackathon/list")  # list hackathons
    api.add_resource(HackathonStatResource, "/api/hackathon/stat")  # get statistics of hackathon
    api.add_resource(HackathonRegistrationListResource, "/api/hackathon/registration/list")  # list registered users
    api.add_resource(HackathonGrantedAwardsResource, "/api/hackathon/grantedawards")  # list registered users
    api.add_resource(GranteAwardsResource, "/api/grantedawards")
    api.add_resource(TalentResource, "/api/talent/list")  # list talents(达人)
    api.add_resource(HackathonTagNamesResource, "/api/tags")  # all distinct tag names
    api.add_resource(HackathonNoticeListResource, "/api/hackathon/notice/list")  # list specfic notices

    # APIs for user(participant) to join hackathon
    api.add_resource(GuacamoleResource, "/api/user/guacamoleconfig")  # get remote paras for guacamole
    api.add_resource(UserResource, "/api/user")  # get current login user
    api.add_resource(UserLoginResource, "/api/user/login")  # user login/logout
    api.add_resource(UserProfileResource, "/api/user/profile")  # update user profile
    api.add_resource(UserPictureResource, "/api/user/picture")  # update user picture
    api.add_resource(UserTemplateListResource, "/api/hackathon/template")  # list templates for specific user
    api.add_resource(UserHackathonLikeResource, "/api/user/hackathon/like")  # like or unlike hackathon
    api.add_resource(UserRegistrationResource, "/api/user/registration")  # register hackathon
    api.add_resource(UserHackathonListResource, "/api/user/registration/list")  # participated hackathon list of user
    api.add_resource(UserExperimentResource, "/api/user/experiment")  # start or stop experiment
    api.add_resource(UserNoticeReadResource, "/api/user/notice/read")  # read the notice
    api.add_resource(UserFileResource, "/api/user/file")  # login-in user can upload files about team, hackathon or user

    # team APIs
    api.add_resource(TeamResource, "/api/team")  # create, update, dismiss and query team
    api.add_resource(MyTeamResource, "/api/team/my")  # get team of current login user
    api.add_resource(HackathonTeamListResource, "/api/hackathon/team/list",
                     "/api/admin/team/list")  # list teams of hackathon
    api.add_resource(TeamMemberResource, "/api/team/member")  # join or leave team, approve member
    api.add_resource(TeamScoreResource, "/api/team/score")  # query or set score by judge
    api.add_resource(TeamShowResource, "/api/team/show")  # query or add show by leader
    api.add_resource(HackathonTeamShowResource, "/api/hackathon/show/list")  # show list of a hackathon
    api.add_resource(UserTeamShowResource, "/api/user/show/list")  # get all team_shows of a user
    api.add_resource(TeamMemberListResource, "/api/team/member/list")  # list team members
    api.add_resource(TeamTemplateResource, "/api/team/template")  # select or unselect template for team

    # APIs for admin to manage hackathon and hackathon resources, features and users
    api.add_resource(AdminHackathonResource, "/api/admin/hackathon")  # create/update hackathon
    api.add_resource(AdminHackathonOnLineResource, "/api/admin/hackathon/online")
    api.add_resource(AdminHackathonApplyOnLineResource, "/api/admin/hackathon/applyonline")
    api.add_resource(AdminHackathonOffLineResource, "/api/admin/hackathon/offline")
    api.add_resource(AdminHackathonConfigResource, "/api/admin/hackathon/config")  # set hackathon config
    api.add_resource(AdminHackathonOrganizerResource, "/api/admin/hackathon/organizer")  # manage hackathon organizers
    api.add_resource(HackathonCheckNameResource, "/api/admin/hackathon/checkname")  # check hackathon name exists
    api.add_resource(AdminHackathonListResource, "/api/admin/hackathon/list")  # get entitled hackathon list
    api.add_resource(AdminAzureResource, '/api/admin/azure')  # manage azure subscription and certs
    api.add_resource(AdminAzureCheckSubIdResource, '/api/admin/azure/checksubid')
    api.add_resource(AdminRegisterListResource, "/api/admin/registration/list")  # get registered users
    api.add_resource(AdminRegisterResource, "/api/admin/registration")  # create, delete or query registration
    api.add_resource(AdminHackathonTemplateListResource,
                     "/api/admin/hackathon/template/list")  # get templates of hackathon
    api.add_resource(AdminHackathonTemplateResource, "/api/admin/hackathon/template")  # select template for hackathon
    api.add_resource(AdminExperimentResource, "/api/admin/experiment")  # start expr by admin
    api.add_resource(AdminExperimentListResource, "/api/admin/experiment/list")  # get expr list of hackathon
    api.add_resource(HackathonAdminListResource, "/api/admin/hackathon/administrator/list")  # list admin/judges
    api.add_resource(HackathonAdminResource, "/api/admin/hackathon/administrator")  # add or delete admin/judge
    api.add_resource(AdminTeamScoreListResource, "/api/admin/team/score/list")  # select or unselect template for team
    api.add_resource(HackathonAwardResource, "/api/admin/hackathon/award")  # manage award content for hackathon
    api.add_resource(HackathonAwardListResource, "/api/admin/hackathon/award/list")  # list award content for hackathon
    api.add_resource(TeamAwardResource, "/api/admin/team/award")  # list award content for hackathon
    api.add_resource(UserListResource, "/api/admin/user/list")  # search and get all related users
    api.add_resource(AdminHostserverListResource, "/api/admin/hostserver/list")  # get the list of host server
    api.add_resource(AdminHostserverResource, "/api/admin/hostserver")  # create/update/delete/get a host server
    api.add_resource(AdminHackathonNoticeResource,
                     "/api/admin/hackathon/notice")  # create/update/delete/get a hackathon notice
