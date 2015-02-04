package com.openhackathon.guacamole;


import java.util.Iterator;

import org.glyptodon.guacamole.protocol.GuacamoleConfiguration;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @foundation transfor the jsonString to GuacamoleConfiguration
 * 
 * @author v-bih
 * 
 * @param  jsonString
 * @return GuacamoleConfiguration
 */
public class Trans2GuacdConfiguration {

    private GuacamoleConfiguration configuration ;
    private Logger logger = LoggerFactory.getLogger(Trans2GuacdConfiguration.class.getClass());

    public Trans2GuacdConfiguration(String jsonString) {

        configuration = new GuacamoleConfiguration();
        try {

            JSONObject json = new JSONObject(jsonString.replace("\\", ""));
            configuration = new GuacamoleConfiguration();

            /*Automlly set configuration value*/
            Iterator<String> keys = json.keys(); 
            while(keys.hasNext()){
                String key = keys.next();
                if (key.equals("displayname")) {
                    continue ;
                }
                if (key.equals("protocol")) {
                    configuration.setProtocol(json.getString("protocol"));
                }else {
                    configuration.setParameter(key, json.getString(key));
                }
            }

        } catch (Exception e) {
            logger.error("==================Failed when transfor jsonString to GuacamoleConfiguation  ");
            configuration = new GuacamoleConfiguration();
            e.printStackTrace();			
        }
}

    public GuacamoleConfiguration getConfiguration() {
        return configuration;
    }

}
