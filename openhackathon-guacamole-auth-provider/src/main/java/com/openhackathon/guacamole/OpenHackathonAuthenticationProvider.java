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
import org.glyptodon.guacamole.net.auth.UserContext;
import org.glyptodon.guacamole.net.auth.simple.SimpleAuthenticationProvider;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnection;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnectionDirectory;
import org.glyptodon.guacamole.properties.StringGuacamoleProperty;
import org.glyptodon.guacamole.properties.GuacamoleProperties;
import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.http.HttpServletRequest;
import java.util.*;


public class OpenHackathonAuthenticationProvider extends SimpleAuthenticationProvider {

    private final Logger logger = LoggerFactory.getLogger(OpenHackathonAuthenticationProvider.class.getClass());
    private Connect2OpenHackathon conn;
    private final Trans2GuacdConfiguration trans = new Trans2GuacdConfiguration();

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


    @Override
    public UserContext updateUserContext(final UserContext context, final Credentials credentials) throws GuacamoleException {
        final HttpServletRequest request = credentials.getRequest();
        final GuacamoleConfiguration config = getGuacamoleConfiguration(request);

        if (config == null) {
            return context;
        }

        final String name = config.getParameter("name");
        logger.info("Instance Type of ConnectionDirectory is: " + context.getConnectionDirectory().getClass().getName());
        final SimpleConnectionDirectory connections = (SimpleConnectionDirectory) context.getConnectionDirectory();
        logger.info("get info from GuacamoleConfiguration name:" + name);
        logger.info("protocol select :" + config.getProtocol());
        final SimpleConnection connection = new SimpleConnection(name, name, config);
        connections.putConnection(connection);
        return context;
    }

    private GuacamoleConfiguration getGuacamoleConfiguration(final HttpServletRequest request) throws GuacamoleException {
        logger.info("========================================test==========================test===================");
    	final String tokenString = request.getParameter("token");
    	

        while (enumString.hasMoreElements()){
        	logger.info("header :" + request.getHeader(enumString.nextElement()));
        }
        
        final String connectionName = request.getParameter("id");
        logger.info("tokenString is : " + tokenString + ", connectionName is:" + connectionName);

        final String jsonString = this.conn.getGuacamoleJSONString(connectionName, tokenString);
        logger.info("get guacamole config json String :" + jsonString);
        if (jsonString == null) {
            logger.info("get null jsonString from openHackathon platform");
            return null;
        }

        // String finalString = jsonString.substring(1, jsonString.length()-1).replace("\\", "");
        return trans.getConfiguration(jsonString);
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
}
