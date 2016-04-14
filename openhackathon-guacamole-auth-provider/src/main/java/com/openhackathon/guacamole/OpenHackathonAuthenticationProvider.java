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

import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.net.auth.Credentials;
import org.glyptodon.guacamole.net.auth.simple.SimpleAuthenticationProvider;
import org.glyptodon.guacamole.properties.StringGuacamoleProperty;
import org.glyptodon.guacamole.properties.GuacamoleProperties;
import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.http.HttpServletRequest;
import java.util.*;


public class OpenHackathonAuthenticationProvider extends SimpleAuthenticationProvider {

    private final Logger logger = LoggerFactory.getLogger(OpenHackathonAuthenticationProvider.class.getClass());
    private Connect2OpenHackathon conn;

    private static final StringGuacamoleProperty AUTH_REQUEST_URL = new StringGuacamoleProperty() {
        @Override
        public String getName() {
            return "auth-request-url";
        }
    };

    public OpenHackathonAuthenticationProvider() {
        initConnection();
        logger.info("initialize OpenHackathonAuthenticationProvider");
    }

    @Override
    public Map<String, GuacamoleConfiguration> getAuthorizedConfigurations(final Credentials credentials) throws GuacamoleException {

        initConnection();

        Map<String, GuacamoleConfiguration> configs = new HashMap<String, GuacamoleConfiguration>();

        final GuacamoleConfiguration config = getGuacamoleConfiguration(credentials.getRequest());
        if (config == null) {
            return configs;
        }

        configs.put(config.getParameter("name"), config);
        return configs;
    }


    private GuacamoleConfiguration getGuacamoleConfiguration(final HttpServletRequest request) throws GuacamoleException {

        final String tokenString = request.getParameter("oh");
        final String connectionName = request.getParameter("name");
        logger.info("open hackathon tokenString is : " + tokenString + ", connectionName is:" + connectionName);

        if(tokenString == null || connectionName==null){
            return null;
        }


        final String jsonString = this.conn.getGuacamoleJSONString(connectionName, tokenString);
        logger.info("get guacamole config json String :" + jsonString);
        if (jsonString == null) {
            logger.info("get null jsonString from openHackathon platform");
            return null;
        }

        // String finalString = jsonString.substring(1, jsonString.length()-1).replace("\\", "");
        return getConfiguration(jsonString);
    }

    private synchronized void initConnection() {
        if (conn != null)
            return;
        try {
            final String authRequestURL = GuacamoleProperties.getProperty(AUTH_REQUEST_URL);
            this.conn = new Connect2OpenHackathon(authRequestURL);
        } catch (GuacamoleException e) {
            logger.error("fail to get AUTH_REQUEST_URL from config file", e);
        }
    }

    @Override
    public String getIdentifier() {
        return "openhackathon";
    }


    private GuacamoleConfiguration getConfiguration(final String jsonString) {
        try {

            final JSONObject json = new JSONObject(jsonString);
            if(json.has("error")){
                logger.info("error returned from open hackathon platform");
                return null;
            }

            final GuacamoleConfiguration configuration = new GuacamoleConfiguration();
            final Iterator<String> keys = json.keys();
            while(keys.hasNext()){
                final String key = keys.next();
                if (key.equals("displayname")) {
                    continue;
                }
                if (key.equals("protocol")) {
                    configuration.setProtocol(json.getString("protocol"));
                } else {
                    configuration.setParameter(key, json.getString(key));
                }
            }
            return configuration;

        } catch (Exception e) {
            logger.error("Failed to load GuacamoleConfiguation from json " + jsonString, e);
            return null;
        }
    }
}
