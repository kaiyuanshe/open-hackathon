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