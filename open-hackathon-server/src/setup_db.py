# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

try:
    from hackathon.hmongo.models import User, Hackathon
except ImportError:
    pass


def setup_db():
    """Initialize db tables

    make sure database and user correctly created in db
    in case upgrade the table structure, the origin table need be dropped firstly
    """
    # init REQUIRED db data.

    # reserved user is deleted, may not need in mongodb implementation

    # default super admin

    admin = User(
        name="admin",
        nickname="admin",
        password="e8104164dfc4a479e42a9f6c0aefd2be",
        is_super=True)

    User.objects(name="admin").update_one(__raw__={"$set": admin.to_mongo().to_dict()}, upsert=True)

    from hackathon.util import get_now
    hackathon1 = Hackathon(
        name="hackathon1",
        display_name="display1",
        ribbon="ribbon1",
        short_description = "short_description1",
        description="description1",
        location="location1",
        banners=["https://octodex.github.com/hanukkat", "https://octodex.github.com/welcometocat", "https://octodex.github.com/filmtocat"],
        status=1,
        creator_id=User.objects(name="admin").first(),
        type=1,
        tags=["tag1", "tag2", "tag3"],
        event_start_time = get_now(),
        event_end_time = get_now(),
        registration_start_time = get_now(),
        registration_end_time = get_now(),
        judge_start_time = get_now(),
        judge_end_time = get_now(),
    )

    hackathon2 = Hackathon(
        name="hackathon2",
        display_name="display2",
        ribbon="ribbon2",
        short_description = "short_description2",
        description="description2",
        location="location2",
        banners=["https://octodex.github.com/privateinvestocat", "https://octodex.github.com/gracehoppertocat", "https://octodex.github.com/gobbleotron"],
        status=1,
        creator_id=User.objects(name="admin").first(),
        type=1,
        tags=["tag1", "tag2", "tag3"],
        event_start_time = get_now(),
        event_end_time = get_now(),
        registration_start_time = get_now(),
        registration_end_time = get_now(),
        judge_start_time = get_now(),
        judge_end_time = get_now(),
    )

    hackathon1.save(force_insert=True)
    hackathon2.save(force_insert=True)
    

setup_db()
