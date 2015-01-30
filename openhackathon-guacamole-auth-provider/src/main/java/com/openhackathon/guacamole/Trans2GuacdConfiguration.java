package com.openhackathon.guacamole;


import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

            configuration.setProtocol(json.getString("protocol"));
            configuration.setParameter("name", json.getString("name"));
            configuration.setParameter("username", json.getString("username"));
            configuration.setParameter("password", json.getString("password"));
            configuration.setParameter("hostname", json.getString("hostname"));
            configuration.setParameter("port", json.getString("port"));
            return configuration;

        } catch (Exception e) {
            logger.error("Failed to load GuacamoleConfiguation from json " + jsonString, e);
            return null;
        }
    }
}
