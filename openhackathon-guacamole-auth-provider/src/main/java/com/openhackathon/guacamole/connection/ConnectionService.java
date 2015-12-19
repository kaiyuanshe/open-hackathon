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
package com.openhackathon.guacamole.connection;

import com.openhackathon.guacamole.Connect2OpenHackathon;
import com.openhackathon.guacamole.Trans2GuacdConfiguration;
import org.glyptodon.guacamole.GuacamoleException;
import org.glyptodon.guacamole.net.auth.Connection;
import org.glyptodon.guacamole.net.auth.Credentials;
import org.glyptodon.guacamole.net.auth.simple.SimpleConnection;
import org.glyptodon.guacamole.properties.GuacamoleProperties;
import org.glyptodon.guacamole.properties.StringGuacamoleProperty;
import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

/**
 * Service for querying the connections available to a particular Guacamole
 * user according to openhackthon server.
 */
public class ConnectionService {
    private Connect2OpenHackathon connect2OpenHackathon;
    /**
     * Logger for this class.
     */
    private final Logger logger = LoggerFactory.getLogger(ConnectionService.class);

    private static final StringGuacamoleProperty AUTH_REQUEST_URL = new StringGuacamoleProperty() {
        @Override
        public String getName() {
            return "auth-request-url";
        }
    };


    private synchronized void initConnection() {
        String authRequestURL = null;
        try {
            authRequestURL = GuacamoleProperties.getProperty(AUTH_REQUEST_URL);
        } catch (GuacamoleException e) {
            logger.error("fail to get AUTH_REQUEST_URL from config file", e);
        }

        this.connect2OpenHackathon = new Connect2OpenHackathon(authRequestURL);

    }

    //There may be some problems here.
    public Map<String, Connection> getConnections(Credentials credentials) throws GuacamoleException {
        logger.info("Authenticate");
        initConnection();
        final HttpServletRequest request = credentials.getRequest();
        final GuacamoleConfiguration config = getGuacamoleConfiguration(request);
        if (config == null) {
            logger.info("Failed to get guacamole configuration.");
            return null;
        }
        final String name = config.getParameter("name");
        logger.info("protocol select :" + config.getProtocol());
        final SimpleConnection connection = new SimpleConnection(name, name, config);
        // Initially assume the user is unauthorized
        Map<String, Connection> connections = new HashMap<String, Connection>();
        connections.put(name, connection);
        return connections;
    }

    private GuacamoleConfiguration getGuacamoleConfiguration(final HttpServletRequest request) throws GuacamoleException {

        final String tokenString = request.getParameter("oh");
        final String connectionName = request.getParameter("name");
        logger.info("open hackathon tokenString is : " + tokenString + ", connectionName is:" + connectionName);

        if(tokenString == null || connectionName==null){
            return null;
        }


        final String jsonString = this.connect2OpenHackathon.getGuacamoleJSONString(connectionName, tokenString);
        logger.info("get guacamole config json String :" + jsonString);
        if (jsonString == null) {
            logger.info("get null jsonString from openHackathon platform");
            return null;
        }

        return Trans2GuacdConfiguration.getConfiguration(jsonString);
    }

}
