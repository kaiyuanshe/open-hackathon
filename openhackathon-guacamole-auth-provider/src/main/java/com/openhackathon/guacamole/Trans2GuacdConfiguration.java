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


import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Iterator;

/**
 * @foundation transfor the jsonString to GuacamoleConfiguration
 *
 * @author v-bih
 *
 */
public class Trans2GuacdConfiguration {

    private final Logger logger = LoggerFactory.getLogger(Trans2GuacdConfiguration.class.getClass());


    public GuacamoleConfiguration getConfiguration(final String jsonString) {
        try {

            final JSONObject json = new JSONObject(jsonString);
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
