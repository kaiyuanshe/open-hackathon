/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved. 
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package com.openhackathon.guacamole;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class Connect2OpenHackathon {

    private Logger logger = LoggerFactory.getLogger(Connect2OpenHackathon.class.getClass());
    private String openHackathonBaseUrl = null;

    public Connect2OpenHackathon(final String openHackathonBaseUrl) {
        this.openHackathonBaseUrl = openHackathonBaseUrl;
    }


    public String getGuacamoleJSONString(final String connectionName, final String tokenString) {

        logger.debug("getGuacamoleJSONString from openhackathon. connectionName:" + connectionName + ", token:" + tokenString);
        HttpURLConnection conn = null;
        BufferedReader in = null;

        try {

            final URL url = new URL(this.openHackathonBaseUrl + "?name=" + connectionName);

            logger.debug("getGuacamoleJSONString from " + url.toString());

            HttpURLConnection.setFollowRedirects(false);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setUseCaches(false);
            conn.setRequestProperty("token", tokenString);
            conn.connect();

            int status = conn.getResponseCode();

            if (status != 200) {
                logger.error("Fail to getGuacamoleJSONString from OpenHackathon. The response code is :" + conn.getResponseCode());
                logger.debug("user may have not login , please do it before your request !!!");
                return null;
            }

            in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String result = "";
            String line;
            while ((line = in.readLine()) != null) {
                result += line;
            }
            return result;

        } catch (Exception e) {
            logger.error("Exception when getGuacamoleJSONString from openHackathon", e);
            return null;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
                if (conn != null) {
                    conn.disconnect();
                }
            } catch (Exception e2) {
                logger.error(e2.getMessage(), e2);
            }
        }
    }

}

